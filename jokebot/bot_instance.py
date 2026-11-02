import discord
from discord.ext import commands, tasks
import json
import logging
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def _load_local_secrets():
    """Optional loader for local secret.txt / .env files during development."""
    for candidate in [BASE_DIR / "secret.txt", BASE_DIR.parent / "secret.txt", BASE_DIR / ".env", BASE_DIR.parent / ".env"]:
        if candidate.exists():
            try:
                for line in candidate.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip('"').strip("'")
                        if k and v:
                            os.environ.setdefault(k, v)
                            os.environ.setdefault(k.replace("_", "-"), v)
                            os.environ.setdefault(k.replace("-", "_"), v)
            except Exception:
                pass

_load_local_secrets()

def get_env_var(*names: str) -> str:
    """Case-insensitive, separator-agnostic environment variable getter.
    Matches JOKEBOT_DISCORD_TOKEN, jokebot-discord-token, etc. interchangeably.
    """
    normalized_env = {
        k.lower().replace("_", "").replace("-", ""): v
        for k, v in os.environ.items()
    }
    for name in names:
        norm = name.lower().replace("_", "").replace("-", "")
        if norm in normalized_env and normalized_env[norm]:
            return normalized_env[norm]
    return ""

config_path = BASE_DIR / "config.json"
config = {}
if config_path.exists():
    try:
        config_raw = config_path.read_text(encoding="utf-8")
        if config_raw.lstrip().startswith("$ANSIBLE_VAULT"):
            logging.warning("Config file appears to be Ansible Vault encrypted. Using environment overrides if present.")
        else:
            config = json.loads(config_raw)
    except Exception as exc:
        logging.warning("Failed to parse config file (%s): %s", config_path, exc)

# Token & key resolution supporting all naming conventions (case-insensitive & separator-agnostic):
# Matches JOKEBOT_DISCORD_TOKEN, jokebot-discord-token, DISCORD_TOKEN, discord-token, etc.
tokens_map = config.get("tokens", {}) if isinstance(config.get("tokens"), dict) else {}
selected_token = (
    get_env_var("jokebot_discord_token", "discord_token")
    or tokens_map.get("jokebot")
    or tokens_map.get("main")
    or config.get("token")
)
config["token"] = selected_token
config["xai_api_key"] = get_env_var("xai_api_key") or config.get("xai-api-key") or config.get("xai_api_key")

data_dir = BASE_DIR / "data"
data_dir.mkdir(parents=True, exist_ok=True)
log_path = data_dir / "bot_jokebot.log"

log_format = "%(asctime)s [%(levelname)s] [jokebot] %(message)s"

class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level: int):
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.addFilter(MaxLevelFilter(logging.INFO))
stdout_handler.setFormatter(logging.Formatter(log_format))

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.WARNING)
stderr_handler.setFormatter(logging.Formatter(log_format))

file_handler = logging.FileHandler(str(log_path))
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stdout_handler, stderr_handler]
)

discord_log_level = os.getenv("DISCORD_LOG_LEVEL", "WARNING").upper()
logging.getLogger("discord").setLevel(discord_log_level)
logging.getLogger("discord.client").setLevel(discord_log_level)
logging.getLogger("discord.gateway").setLevel(discord_log_level)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

def get_config():
    return config

try:
    from .reddit_loader import load_reddit_jokes
except ImportError:
    from reddit_loader import load_reddit_jokes

@tasks.loop(hours=24)
async def refresh_reddit_jokes():
    logging.info("Refreshing Reddit jokes (background)...")
    await load_reddit_jokes()
    logging.info("Reddit jokes refreshed.")

first_ready = True

@bot.event
async def on_ready():
    global first_ready
    logging.info(f"Bot logged in as {bot.user}!")
    await bot.change_presence(activity=discord.Game(name="Loading..."))

    try:
        if first_ready:
            logging.info("Loading Reddit jokes at startup...")
            await load_reddit_jokes()
            logging.info("Reddit jokes loaded.")
            refresh_reddit_jokes.start()

            try:
                from .commands import setup_all_commands
            except ImportError:
                from commands import setup_all_commands
            logging.info("Setting up jokebot command modules...")
            loaded = await setup_all_commands(bot)
            if not loaded:
                logging.error("No command modules loaded! Check import errors above.")
            logging.info("Syncing slash commands...")
            cmds = await bot.tree.sync()
            logging.info(f"Slash commands synced: {len(cmds)} cmds (expected ~{len(loaded)})")
            first_ready = False

        status_text = "Chat: /help"
        await bot.change_presence(activity=discord.Game(name=status_text))
        logging.info("Bot status set to '%s'.", status_text)
    except Exception as e:
        logging.exception("Exception in on_ready")
        await bot.change_presence(activity=discord.Game(name="Erreur au démarrage"))

