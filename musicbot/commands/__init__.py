"""Dynamic command module loader for MusicBot."""
from importlib import import_module
import logging
from types import ModuleType
from typing import List

ALL_MODULES: List[str] = [
    "music",
    "yt",
    "suno",
    "moderation",
    "util",
    "help",
    "bot_mention",
]

async def setup_all_commands(bot) -> list[str]:
    """Import and setup all modules for MusicBot."""
    loaded: list[str] = []
    base_pkg = __name__
    for name in ALL_MODULES:
        full_name = f"{base_pkg}.{name}"
        try:
            mod: ModuleType = import_module(full_name)
        except ModuleNotFoundError:
            try:
                mod = import_module(name)
            except Exception as e:
                logging.exception("Failed to import module %s: %s", name, e)
                continue
        except Exception as e:
            logging.exception("Failed to import module %s: %s", full_name, e)
            continue

        if hasattr(mod, "setup"):
            try:
                await mod.setup(bot)
                loaded.append(name)
                logging.info("Loaded command module: %s", name)
            except Exception as e:
                logging.exception("Failed to setup module %s: %s", name, e)
        else:
            logging.warning("Module %s has no setup(bot) function", name)
    return loaded

