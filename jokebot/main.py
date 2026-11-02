import logging
try:
    from . import __version__
    from .bot_instance import bot, get_config  # type: ignore
except ImportError:
    try:
        from __init__ import __version__  # type: ignore
    except ImportError:
        __version__ = "1.0.0"
    from bot_instance import bot, get_config  # type: ignore

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Starting JokeBot v{__version__}...")
    token = get_config().get("token")
    if not token:
        raise RuntimeError("No Discord token found for JokeBot! Set discord-token env var or configure tokens in config.json.")
    bot.run(token)
