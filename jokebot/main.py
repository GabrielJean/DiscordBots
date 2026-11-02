import logging
try:
    from .bot_instance import bot, get_config  # type: ignore
except ImportError:
    from bot_instance import bot, get_config  # type: ignore

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting JokeBot...")
    token = get_config().get("token")
    if not token:
        raise RuntimeError("No Discord token found for JokeBot! Set DISCORD_TOKEN env var or configure tokens in config.json.")
    bot.run(token)

