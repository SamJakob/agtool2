import os.path
from typing import Optional, Union


def _resolve_path(target: str, working_dir: Optional[str]) -> str:
    """
    Resolves the working directory to use for file operations.
    """

    # If the working directory is not specified, use the target directory,
    # otherwise, resolve the target relative to the working directory.
    path = target
    if working_dir is not None:
        path = os.path.join(working_dir, target)

    # Normalize the path.
    return os.path.normcase(os.path.normpath(path))


def read_file_as_string(file_path: str, working_dir: Optional[str] = None) -> str:
    """
    Reads the contents of a file as a string.
    """

    with open(_resolve_path(target=file_path, working_dir=working_dir), 'r') as file:
        return file.read()


def write_file_from_string(file_path: str, contents: str, working_dir: Optional[str] = None) -> None:
    """
    Writes a string to a file.
    """

    with open(_resolve_path(target=file_path, working_dir=working_dir), 'w') as file:
        file.write(contents)


def read_file_as_bytes(file_path: str, working_dir: Optional[str] = None) -> bytes:
    """
    Reads the contents of a file as a string.
    """

    with open(_resolve_path(target=file_path, working_dir=working_dir), 'rb') as file:
        return file.read()


def write_file_from_bytes(file_path: str, contents: bytes, working_dir: Optional[str] = None) -> None:
    """
    Writes bytes to a file.
    """

    with open(_resolve_path(target=file_path, working_dir=working_dir), 'wb') as file:
        file.write(contents)


def write_file_from_data(file_path: str, contents: Union[str, bytes], working_dir: Optional[str] = None) -> None:
    """
    Writes data to a file. (Data is either a string or bytes, the type of which
    is inferred from the type of the contents argument.)
    """

    if isinstance(contents, str):
        write_file_from_string(file_path, contents, working_dir=working_dir)
    elif isinstance(contents, bytes):
        write_file_from_bytes(file_path, contents, working_dir=working_dir)
    else:
        raise ValueError(f"Invalid file contents. It must be either a string (str) or bytes (bytes), "
                         f"but was \"{type(contents)}\".")


def replace_file_extension(filename: str, new_extension: str) -> str:
    """
    Replaces the file extension of a filename with a new extension.
    """

    return f"{os.path.splitext(filename)[0]}{os.extsep}{new_extension}"
