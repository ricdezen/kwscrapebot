from pathlib import Path
from typing import Union
import logging

import telegram
from telegram.ext import Updater, CommandHandler

from database import Database, Job


class Bot(object):
    START_MESSAGE = "Hello, I am a bot, nice to meet you."
    SET_USAGE = "/set <url> <frequency in hours> <keyword 1> <keyword 2> ..."
    LIST_USAGE = "/list"
    REMOVE_USAGE = "/remove <url>"

    def __init__(self, token: str, database_file: Union[str, Path]):
        """
        :param token: The token to run the bot on.
        :param database_file: The database file.
        """
        self._database_file = database_file

        self._updater = Updater(token=token, use_context=True)
        self._updater.dispatcher.add_handler(CommandHandler("start", self._add_user))
        self._updater.dispatcher.add_handler(CommandHandler("list", self._list_jobs))
        self._updater.dispatcher.add_handler(CommandHandler("set", self._add_job))
        self._updater.dispatcher.add_handler(CommandHandler("remove", self._remove_job))

    def start(self):
        self._updater.start_polling()

    def _add_user(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        """
        Callback for the addition of a user.
        """
        user = update.effective_chat.id
        # Add user to database.
        Database(self._database_file).add_user(user)
        # Answer user.
        context.bot.send_message(chat_id=user, text=self.START_MESSAGE)
        # Log the info about the new user.
        logging.info(f"/start command received by user: {user}.")

    def _add_job(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        """
        Callback for the update of a job. Message must be:
        ```
        /set <url> <frequency in hours> <keyword 1> <keyword 2> ...
        ```
        """
        user = update.effective_chat.id
        try:
            # Extract info.
            url = context.args[0]
            freq = int(context.args[1])
            keywords = context.args[2::]
            # Update database.
            Database(self._database_file).add_job(Job(user, url, freq, keywords))
            # TODO actually start the Job.
            # Send back a response as a confirmation.
            response = f"Will start searching {url} for links containing {', '.join(keywords)} every {freq} hours."
            update.message.reply_text(response)
            logging.info(f"/set command received by user: {user}. {response}")
        except (IndexError, ValueError):
            update.message.reply_text(f"Usage: {Bot.SET_USAGE}")
            logging.warning(f"Inappropriate /set command from user {user}.")

    def _list_jobs(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        """
        Send a message containing the scheduled jobs for the user.
        """
        user = update.effective_chat.id
        jobs = Database(self._database_file).get_jobs(user)
        if jobs:
            update.message.reply_markdown(
                "\n---\n".join([f"*JOB {i + 1}*\nurl: {j.url}\nkeywords: {j.keywords}\nEvery {j.freq} hours."
                                for i, j in enumerate(jobs)])
            )
        else:
            update.message.reply_text(f"No jobs scheduled.")
        logging.info(f"Sent job list to {user}.")

    def _remove_job(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        """
        Callback for the removal of a job. Message must be:
        ```
        /remove <url>
        ```
        """
        user = update.effective_chat.id
        try:
            url = context.args[0]
            db = Database(self._database_file)
            jobs = db.get_jobs(user)
            # Job not in database.
            if url not in [j.url for j in jobs]:
                update.message.reply_text(f"You have no job for url: {url}")
                logging.info(f"User {user} asked for removal of non-existing job {url}")
                return
            # Job in db, delete job.
            db.delete_job(user, url)
            # TODO actually remove the job.
            update.message.reply_text(f"You will receive no more updates from: {url}")
            logging.info(f"Removed job {url} for user {user}.")
        except IndexError:
            update.message.reply_text(f"Usage: {Bot.REMOVE_USAGE}")
            logging.warning(f"Inappropriate /remove command from user {user}.")

    def __del__(self):
        # Stop za bot.
        self._updater.stop()
