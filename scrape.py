from typing import List
from dataclasses import dataclass
from bs4 import BeautifulSoup


class Parser(object):

    def parse(self, content: str) -> List:
        """
        :param content: Content of the web page to parse.
        :return: A list of items, based on the parsing logic.
        """
        raise NotImplementedError()


@dataclass(repr=True, eq=True, frozen=True)
class Link(object):
    href: str
    text: str


class LinkKeywordParser(Parser):
    """
    Basic parser class. Scans a web page for link tags. Returns the link tags that contain one of the given keywords in
    their text. If no keywords are given it just returns all the links.
    """

    def __init__(self, keywords: List[str] = None):
        """
        :param keywords: The keywords to look for in the link texts. Will be put in lower case.
        """
        self.keywords = keywords
        if self.keywords is not None:
            self.keywords = tuple(map(lambda k: k.lower(), self.keywords))

    def parse(self, content: str) -> List[Link]:
        """
        :param content: Content of the web page to parse.
        :return: A list of links. Excludes any link with href equal to '#'.
        """
        # Get the links from the page.
        soup = BeautifulSoup(content, "html.parser")
        links = [Link(t.get("href"), t.get_text().strip()) for t in soup("a")]
        links = filter(lambda link: link.href != '#', links)

        # If no keywords, all links automatically match.
        if self.keywords is None:
            return list(links)

        # Otherwise, return only the ones containing the keywords.
        return list(filter(self._matches, links))

    def _matches(self, link: Link) -> bool:
        """
        :param link: A link object.
        :return: True if the link's lower case text contains at least one of the given keywords, False otherwise.
        """
        text = link.text.lower()
        for k in self.keywords:
            if k in text:
                return True
        return False
