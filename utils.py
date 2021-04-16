import json
import re
import urllib.parse
from typing import Union, Dict, List
from pathlib import Path
from requests_html import HTMLSession

from scrape import Link

html_session = HTMLSession()
_ = html_session.browser


def get_config(file: Union[str, Path]) -> Dict:
    """
    :param file: Name or Path object for the json config file.
    :return: A dict containing what the file contained. Empty dict if file did not exist.
    """
    # Make Path if got a string.
    if isinstance(file, str):
        file = Path(file)
    # If the file does not exist, return an empty dict.
    if not file.exists():
        return dict()

    # Read json file and return.
    with file.open() as f:
        data = json.load(f)
    return data


def is_valid_url(url: str) -> bool:
    """
    Check if a given url is valid.
    See: https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45 for details.

    :param url: The url to check.
    :return: True if the url is valid, False otherwise.
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE
    )
    return re.match(regex, url) is not None


def to_abs_urls(url, links: List[Link]) -> List[Link]:
    """
    :param url: The base url of the web page.
    :param links: The links to turn into absolute paths.
    :return: A list of absolute links.
    """
    return [Link(urllib.parse.urljoin(url, link.href), link.text) for link in links]
