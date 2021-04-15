import logging
import sqlite3

from dataclasses import dataclass

from typing import List, Optional


@dataclass(repr=True)
class Job(object):
    """
    Class representing an object. Keywords will be stripped of whitespaces and set to lower case.
    If a keyword is, for instance "a b" it will be serialized as such, and later read as two keywords "a" and "b".
    """
    user: int
    url: str
    freq: str
    keywords: List[str] = None

    def __post_init__(self):
        # Ensure the keywords are properly formatted.
        if self.keywords is None:
            return
        self.keywords = list(map(lambda x: x.strip().lower(), self.keywords))

    @property
    def kw_string(self) -> Optional[str]:
        """
        :return: The keywords, in a single string separated by spaces, or None if there are no keywords.
        """
        if self.keywords:
            return ' '.join(self.keywords)
        else:
            return None


class Database(object):
    """
    Interface to manage an sqlite database to contain users and such.
    Handle database files with care, do not modify them via other classes. This class expects the provided files to be
    either empty or have the schema that is created if the file is empty.

    Schema:
    ```sql
    CREATE TABLE users (id integer PRIMARY KEY);
    CREATE TABLE jobs (
        user integer NOT NULL,
        url text NOT NULL,
        -- period in hours.
        freq integer NOT NULL,
        -- string of words separated by a space.
        keywords text,
        FOREIGN KEY (user) REFERENCES users(id),
        PRIMARY KEY (user, url)
    );
    ```
    """

    _TABLE_EXISTS = "Table \"{}\" already present, skipping it."

    def __init__(self, filename: str):
        """
        :param filename: Name of the database file that will be created in the current working directory.
        """
        self._filename = filename
        self._conn = sqlite3.connect(filename)

        with self._conn as c:
            # Create user table.
            try:
                c.execute("CREATE TABLE users (id integer PRIMARY KEY);")
            except sqlite3.OperationalError:
                logging.warning(Database._TABLE_EXISTS.format("users"))
            # Create job table.
            try:
                c.execute("""CREATE TABLE jobs (
                    user integer NOT NULL,
                    url text NOT NULL,
                    freq integer NOT NULL,
                    keywords text,
                    FOREIGN KEY (user) REFERENCES users(id),
                    PRIMARY KEY (user, url)
                );""")
            except sqlite3.OperationalError:
                logging.warning(Database._TABLE_EXISTS.format("jobs"))
            # Ensure foreign keys are enabled.
            c.execute("PRAGMA foreign_keys = ON;")

    def add_user(self, new_user: int):
        """
        Add new user with the given id. Does nothing if user already exists.

        :param new_user: Id for the new user to add.
        """
        with self._conn as c:
            c.execute("INSERT OR IGNORE INTO users(id) values (?);", (new_user,))

    def add_job(self, job: Job):
        """
        Add a job to the database. Updates the job's information (freq and keywords) in case of conflict.

        :param job: The job to add.
        """
        with self._conn as c:
            c.execute(
                "INSERT OR REPLACE INTO jobs(user, url, freq, keywords) values (?, ?, ?, ?);",
                (job.user, job.url, job.freq, job.kw_string)
            )

    def get_jobs(self, user: int = None) -> List[Job]:
        """
        :param user : The user. If None, all Jobs are returned.
        :return: A list of the jobs in the database.
        """
        if user is None:
            return [Job(r[0], r[1], r[2], r[3].split()) for r in self._conn.execute("SELECT * FROM jobs;")]
        else:
            return [Job(r[0], r[1], r[2], r[3].split()) for r in self._conn.execute(
                "SELECT * FROM jobs WHERE jobs.user = ?;", (user,)
            )]

    def __del__(self):
        # Close the connection when object is deleted.
        self._conn.close()


if __name__ == "__main__":
    Database("main.db")
