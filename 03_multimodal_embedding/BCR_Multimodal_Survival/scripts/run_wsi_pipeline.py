"""Compatibility entry point for pathology-only processing."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import main

if __name__ == "__main__":
    arguments = sys.argv[1:]
    if "--stop-after" not in arguments:
        arguments.extend(["--stop-after", "mil"])
    main(arguments)
