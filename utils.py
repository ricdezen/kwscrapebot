import json
from typing import Union, Dict
from pathlib import Path


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
