import os
import logging
from bot import Bot
from database import Database

import utils

# Set working directory to local directory.
abspath = os.path.abspath(__file__)
dir_name = os.path.dirname(abspath)
os.chdir(dir_name)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
try:
    # Try to add a lil colors.
    import coloredlogs

    coloredlogs.install(level='INFO')
except ImportError:
    logging.info("No colored logs :(")

config = utils.get_config("config.json")


def main():
    Database.prepare_db(config["database_file"])
    bot = Bot(**config)
    bot.start()
    bot.idle()


if __name__ == '__main__':
    main()
