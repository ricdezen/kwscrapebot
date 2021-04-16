import logging
import telegram
from pathlib import Path
from typing import Union, Callable
from telegram.ext import Updater, CommandHandler, JobQueue

import utils
from database import Database, Job
from download import JavascriptDownloader
from scrape import LinkKeywordParser


def make_job_callback(job: Job, database_file: str) -> Callable:
    user = job.user
    url = job.url
    keywords = job.keywords

    def do_job(context: telegram.ext.CallbackContext):
        # Download and parse the desired webpage.
        links = LinkKeywordParser(keywords).parse(JavascriptDownloader().download(url))
        if links:
            db = Database(database_file)

            # Make absolute links.
            links = utils.to_abs_urls(url, links)

            # Find which links are the new ones.
            old_links = set(db.get_links(url))
            new_links = old_links.difference(set(links))

            # Send a notification to the user if there was anything new.
            if new_links:
                text = "\n---\n".join([f"{link.text}\n{link.href}" for link in new_links])
                context.bot.send_message(chat_id=user, text=text)

                # Delete old links.
                db.reset_links(url)
                # Keep only links that were found this time.
                db.add_links(url, links)
        else:
            logging.info(f"No links found on url {url} for user {user} :(")

    return do_job


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

        self._job_queue = JobQueue()
        self._job_queue.set_dispatcher(self._updater.dispatcher)
        self._job_queue.start()

        # Keep map {(user, url) : telegram.ext.Job} to allow canceling jobs.
        self._job_map = dict()

        # Load all Jobs in the database.
        for job in Database(self._database_file).get_jobs():
            self._schedule(job)

    def start(self):
        self._updater.start_polling()

    def idle(self):
        self._updater.idle()

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

            # Check url validity.
            if not utils.is_valid_url(url):
                update.message.reply_text(f"{url} is not a valid url.")
                logging.warning(f"Invalid url from user {user}.")
                return

            freq = int(context.args[1])
            keywords = context.args[2::]

            # Update database.
            job = Job(user, url, freq, keywords)
            Database(self._database_file).add_job(job)

            # Schedule job.
            self._schedule(job)

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

            # Job in db, delete and unschedule job.
            db.delete_job(user, url)
            self._unschedule(user, url)

            # Send back a response.
            update.message.reply_text(f"You will receive no more updates from: {url}")
            logging.info(f"Removed job {url} for user {user}.")

        except IndexError:
            update.message.reply_text(f"Usage: {Bot.REMOVE_USAGE}")
            logging.warning(f"Inappropriate /remove command from user {user}.")

    def _schedule(self, job: Job):
        """
        Schedule a new job for the bot. Tries to remove any previous job for the same key (user, url)

        :param job: The new job to schedule.
        """
        # Safely remove any old matching job.
        self._unschedule(job.user, job.url)

        # Set job to run every x hours and keep track to cancel it later.
        self._job_map[(job.user, job.url)] = self._job_queue.run_repeating(
            # TODO change from minutes to hours.
            make_job_callback(job, self._database_file), 60 * job.freq, 1
        )
        logging.info(f"Started job on url {job.url} for user {job.user}.")

    def _unschedule(self, user: int, url: str):
        """
        Remove the corresponding job from the queue.

        :param user: The user of the job.
        :param url: The url of the job.
        """
        old_job = self._job_map.pop((user, url), 0)
        if old_job != 0:
            old_job.schedule_removal()
            logging.info(f"Removed Telegram job on url {url} for user {user}.")

    def __del__(self):
        # Stop za bot.
        self._job_queue.stop()
        self._updater.stop()
