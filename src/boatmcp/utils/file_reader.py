"""Simple file reading utilities."""

import os
from pathlib import Path

# Maximum file size to read (100KB)
MAX_FILE_SIZE = 100 * 1024

# Maximum number of files to read
MAX_FILES = 30


def read_file(file_path: str) -> str:
    """Read a single file.

    Args:
        file_path: Path to the file (absolute or relative to current working directory)

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If file doesn't exist
        IsADirectoryError: If path points to a directory
        ValueError: If file is too large
        UnicodeDecodeError: If file can't be decoded as text
    """
    # Try as absolute path first, then relative to current working directory
    path = Path(file_path)
    if not path.is_absolute():
        path = Path.cwd() / file_path

    path = path.resolve()

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if path.is_dir():
        raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")

    # Check file size
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large (max {MAX_FILE_SIZE // 1024}KB): {file_path}")

    # Read file content
    with open(path, encoding='utf-8') as f:
        return f.read()


def read_directory(directory_path: str) -> dict[str, str]:
    """Read all files in a directory (non-recursive).

    Args:
        directory_path: Path to the directory (absolute or relative to current working directory)

    Returns:
        Dictionary mapping relative file paths to their contents

    Raises:
        FileNotFoundError: If directory doesn't exist
        NotADirectoryError: If path is not a directory
    """
    # Try as absolute path first, then relative to current working directory
    path = Path(directory_path)
    if not path.is_absolute():
        path = Path.cwd() / directory_path

    path = path.resolve()

    if not path.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory_path}")

    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory_path}")

    files_content: dict[str, str] = {}
    files_read = 0

    for item in path.iterdir():
        if item.is_file() and files_read < MAX_FILES:
            try:
                # Skip files that are too large
                if item.stat().st_size > MAX_FILE_SIZE:
                    continue

                # Read file content
                with open(item, encoding='utf-8') as f:
                    content = f.read()
                    files_content[item.name] = content
                    files_read += 1

            except (UnicodeDecodeError, OSError):
                # Skip files that can't be read as text
                continue

    return files_content


def read_project_files(project_path: str) -> dict[str, str]:
    """Read all files in a directory tree recursively.

    Args:
        project_path: Path to the project root directory (absolute or relative to current working directory)

    Returns:
        Dictionary mapping relative file paths to their contents

    Raises:
        FileNotFoundError: If directory doesn't exist
        NotADirectoryError: If path is not a directory
    """
    # Try as absolute path first, then relative to current working directory
    path = Path(project_path)
    if not path.is_absolute():
        path = Path.cwd() / project_path

    path = path.resolve()

    if not path.exists():
        raise FileNotFoundError(f"Directory does not exist: {project_path}")

    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {project_path}")

    files_content: dict[str, str] = {}
    files_read = 0

    for root, _dirs, files in os.walk(path):
        root_path = Path(root)

        for file in files:
            if files_read >= MAX_FILES:
                break

            file_path = root_path / file

            try:
                # Skip files that are too large
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue

                # Read file content
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()

                # Use relative path as key
                relative_path = file_path.relative_to(path)
                files_content[str(relative_path)] = content
                files_read += 1

            except (UnicodeDecodeError, OSError):
                # Skip files that can't be read as text
                continue

        # Break outer loop if we've reached the file limit
        if files_read >= MAX_FILES:
            break

    return files_content
