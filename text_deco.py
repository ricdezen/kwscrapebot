_BLUE = '\033[34m'
_GREEN = '\033[32m'
_CYAN = '\033[36m'
_RED = '\033[31'
_PURPLE = '\033[35'
_YELLOW = '\033[33'

_BOLD = '\033[1m'
_UNDERLINE = '\033[4m'

_END = '\033[0m'


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
