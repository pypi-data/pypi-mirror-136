import pathlib


def get_file_path(file: str) -> pathlib.Path:
    """
    Get path to passed in  file.
    Example get_file_path(__file__)
    """
    return pathlib.Path(file).parent.absolute()
