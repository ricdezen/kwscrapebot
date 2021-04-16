import utils


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
        browser = utils.get_firefox()
        browser.get(target)
        content = browser.page_source
        browser.close()
        return content
