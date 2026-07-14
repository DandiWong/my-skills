#!/usr/bin/env python3
"""Check runtime dependencies for the meeting-minutes skill."""

from __future__ import annotations

import importlib.metadata
import platform
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REQUIREMENTS = SKILL_DIR / "requirements.txt"


def main() -> int:
    print(f"python: OK ({platform.python_version()})")

    try:
        version = importlib.metadata.version("python-docx")
    except importlib.metadata.PackageNotFoundError:
        print("python-docx: MISSING")
        print("")
        print("Install the required Python library with:")
        print(f"  {sys.executable} -m pip install -r {REQUIREMENTS}")
        return 1

    print(f"python-docx: OK ({version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
