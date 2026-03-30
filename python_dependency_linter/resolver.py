from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path


class ImportCategory(Enum):
    STANDARD_LIBRARY = "standard_library"
    THIRD_PARTY = "third_party"
    LOCAL = "local"


def resolve_import(module: str, project_root: Path) -> ImportCategory:
    top_level = module.split(".")[0]

    if top_level in sys.stdlib_module_names:
        return ImportCategory.STANDARD_LIBRARY

    # Check if it exists as a local module/package
    if (project_root / top_level).is_dir() or (
        project_root / f"{top_level}.py"
    ).is_file():
        return ImportCategory.LOCAL

    return ImportCategory.THIRD_PARTY
