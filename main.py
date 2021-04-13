import time
import schedule
import log
from telegram.ext import Updater, CommandHandler

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Henlo, me is a bot, please talk to me!")


def job():
    log.write(log.blue("I'm working..."))


def main():
    updater = Updater(token=TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.start_polling()

    schedule.every(10).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
