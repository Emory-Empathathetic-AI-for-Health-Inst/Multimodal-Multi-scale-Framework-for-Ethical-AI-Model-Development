#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e WSITools
echo "Setup complete. Run: python main.py --data-dir /path/to/existing/data"
