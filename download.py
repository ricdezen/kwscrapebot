from requests_html import HTMLSession


class Downloader(object):
    """
    Base class for a downloader.
    """

    def download(self, target: str) -> str:
        """
        :param target: The target. e.g. the web page URL.
        :return: The content.
        """
        raise NotImplementedError()


class JavascriptDownloader(Downloader):
    """
    Downloader that also runs the Javascript in the web page before downloading.
    """

    def download(self, target: str) -> str:
        """
        :param target: The target. e.g. the web page URL.
        :return: The content.
        """
        session = HTMLSession()
        response = session.get(target)
        response.html.render()
        return response.html.html
