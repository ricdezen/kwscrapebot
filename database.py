import logging
import sqlite3

from dataclasses import dataclass
from typing import List, Optional

from scrape import Link


@dataclass(repr=True)
class Job(object):
    """
    Class representing an object. Keywords will be stripped of whitespaces and set to lower case.
    If a keyword is, for instance "a b" it will be serialized as such, and later read as two keywords "a" and "b".
    """
    user: int
    url: str
    freq: int
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
    CREATE TABLE links (
        url text NOT NULL,
        href text NOT NULL,
        body text NOT NULL,
        PRIMARY KEY (url, href, body)
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
            # Ensure foreign keys are enabled.
            c.execute("PRAGMA foreign_keys = ON;")

    def add_user(self, new_user: int):
        """
        Add new user with the given id. Does nothing if user already exists.

        :param new_user: Id for the new user to add.
        """
        with self._conn as c:
            c.execute("INSERT OR IGNORE INTO users(id) VALUES (?);", (new_user,))

    def get_users(self) -> List[int]:
        """
        :return: The list of ids for the users.
        """
        return [r[0] for r in self._conn.execute("SELECT * FROM users;")]

    def add_job(self, job: Job):
        """
        Add a job to the database. Updates the job's information (freq and keywords) in case of conflict.

        :param job: The job to add.
        """
        with self._conn as c:
            c.execute(
                "INSERT OR REPLACE INTO jobs(user, url, freq, keywords) VALUES (?, ?, ?, ?);",
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

    def delete_job(self, job: Job):
        """
        Delete the given job.

        :param job: The job to remove.
        """
        with self._conn as c:
            c.execute("DELETE FROM jobs WHERE user = ? AND url = ?;", (job.user, job.url))

    def add_link(self, url: str, link: Link):
        """
        Add a link to the database.

        :param url: The url of the page hosting the link.
        :param link: The link object.
        """
        with self._conn as c:
            c.execute("INSERT OR REPLACE INTO links(url, href, body) VALUES (?, ?, ?);", (url, link.href, link.text))

    def add_links(self, url: str, links: List[Link]):
        """
        Add a set of links to the database.

        :param url: The url of the page hosting the links.
        :param links: The list of links to add.
        """
        with self._conn as c:
            c.executemany(
                "INSERT OR REPLACE INTO links(url, href, body) VALUES (?, ?, ?);",
                [(url, link.href, link.text) for link in links]
            )

    def get_links(self, url: str = None) -> List[Link]:
        """
        :param url: Optional host web page. If None all links will be retrieved.
        :return: The links hosted in `url` or all of them if `url` is None.
        """
        if url is None:
            return [Link(r[1], r[2]) for r in self._conn.execute("SELECT * FROM links;")]
        else:
            return [Link(r[1], r[2]) for r in self._conn.execute(
                "SELECT * FROM links WHERE links.url = ?;", (url,)
            )]

    def reset_links(self, url: str):
        """
        Reset the links for a given page.

        :param url: The page for which to clean the links.
        """
        with self._conn as c:
            c.execute("DELETE FROM links WHERE url = ?;", (url,))

    def __del__(self):
        # Close the connection when object is deleted.
        self._conn.close()

    @staticmethod
    def prepare_db(filename: str):
        """
        Prepares a database file with the appropriate schema by creating the necessary tables. If tables with same name
        are found they are skipped.

        :param filename: The filename for the db.
        """
        with sqlite3.connect(filename) as c:
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

            # Create link table.
            try:
                c.execute("""CREATE TABLE links (
                    url text NOT NULL,
                    href text NOT NULL,
                    body text NOT NULL,
                    PRIMARY KEY (url, href, body)
                );""")
            except sqlite3.OperationalError:
                logging.warning(Database._TABLE_EXISTS.format("links"))
