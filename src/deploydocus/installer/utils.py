from pathlib import Path
from typing import Any

from camel_converter import to_snake


def snake_keyed_dict(obj_dict: dict[str, Any]) -> dict[str, Any]:
    """

    Args:
        obj_dict:

    Returns:

    """
    return {to_snake(k): v for k, v in obj_dict.items()}


def settings_file_path(module_path: Path | str, json_filename: str) -> Path:
    """A utility to lo locate the settings file (release.json or pkg.json) is located

    Args:
        module_path: Must be sent as __file__ from the __init__ module of the Pkg
        json_filename: must be either "release.json" or "pkg.json"

    Returns:
        The absolute path to the release.json or pkg.json
    """
    _module_path: Path = (
        module_path if isinstance(module_path, Path) else Path(module_path)
    ).resolve()

    _dir = _module_path if _module_path.is_dir() else _module_path.parent
    return _dir / json_filename
