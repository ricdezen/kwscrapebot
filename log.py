import sys
from typing import Union, TextIO
from pathlib import Path

_BLUE = '\033[34m'
_GREEN = '\033[32m'
_CYAN = '\033[36m'
_RED = '\033[31'
_PURPLE = '\033[35'
_YELLOW = '\033[33'

_BOLD = '\033[1m'
_UNDERLINE = '\033[4m'

_END = '\033[0m'


class Log(object):

    def __init__(self, output: Union[str, Path] = sys.stdout):
        """
        :param output: String or Path object. Any object that can be opened and then written to works. See Path.
        Standard output by default.
        """
        self._output = output

    def set_output(self, output: Union[str, Path, TextIO]):
        """
        :param output: String or Path object. Any object that can be opened and then written to works. See Path.
        """
        self._output = output

    def write(self, text: str):
        """
        :param text: The text to print. See functions in this module for formatting.
        """
        text += '\n'
        if hasattr(self._output, 'write'):
            self._output.write(text)
        elif isinstance(self._output, str):
            with open(self._output, 'w+') as out:
                out.write(text)
        else:
            with self._output.open('w+') as out:
                out.write(text)

    def __rshift__(self, other):
        """
        Alternative for `Log.set_output(other)`.
        :return: This Log object.
        """
        self.set_output(other)
        return self


# --- Helper functions ---

def blue(text: str) -> str:
    return _BLUE + text + _END


def cyan(text: str) -> str:
    return _CYAN + text + _END


def green(text: str) -> str:
    return _GREEN + text + _END


def red(text: str) -> str:
    return _RED + text + _END


def purple(text: str) -> str:
    return _PURPLE + text + _END


def yellow(text: str) -> str:
    return _YELLOW + text + _END


def bold(text: str) -> str:
    return _BOLD + text + _END


def underline(text: str) -> str:
    return _UNDERLINE + text + _END


# --- Default output: stdout

_DEFAULT = Log()


def write(text: str):
    _DEFAULT.write(text)
