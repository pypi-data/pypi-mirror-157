"""Functions utils."""
from Products.CMFPlone.utils import safe_text


def convert_path(path):
    """Convert path to a valid ascii string.
    If it contains non-ascii characters, raises an Exception."""
    if path.isascii():
        return safe_text(path)
    _path = path
    if not isinstance(_path, str):
        _path = _path.encode("utf-8")
    raise AssertionError(f'The path "{_path}" contains non-ascii characters.')
