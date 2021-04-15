import time
import schedule
import logging
from telegram.ext import Updater, CommandHandler

import utils

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

config = utils.get_config("config.json")
TOKEN = config["get_token"]


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Henlo, me is a bot, please talk to me!")


def job():
    logging.log(logging.INFO, "Hello")


def main():
    updater = Updater(token=TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.start_polling()

    schedule.every(10).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
