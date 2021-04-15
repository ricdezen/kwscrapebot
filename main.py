import time
import logging
from bot import Bot
from database import Database

import utils

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

config = utils.get_config("config.json")
TOKEN = config["bot_token"]
DB_FILE = config["database_file"]


def main():
    Database.prepare_db(DB_FILE)
    bot = Bot(TOKEN, DB_FILE)
    bot.start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
