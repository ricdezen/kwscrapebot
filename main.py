import logging
from bot import Bot
from database import Database

import utils

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
TOKEN = config["bot_token"]
DB_FILE = config["database_file"]


def main():
    Database.prepare_db(DB_FILE)
    bot = Bot(TOKEN, DB_FILE)
    bot.start()
    bot.idle()


if __name__ == '__main__':
    main()
