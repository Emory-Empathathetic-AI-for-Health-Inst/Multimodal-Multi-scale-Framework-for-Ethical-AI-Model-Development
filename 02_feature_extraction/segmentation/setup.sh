#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python -m pip install -r "${PROJECT_DIR}/requirements.txt"

if [[ ! -d "${PROJECT_DIR}/WSITools" ]]; then
    git clone https://github.com/smujiang/WSITools.git "${PROJECT_DIR}/WSITools"
fi
python -m pip install -e "${PROJECT_DIR}/WSITools"

if [[ ! -d "${PROJECT_DIR}/UNI" ]]; then
    git clone https://github.com/mahmoodlab/UNI.git "${PROJECT_DIR}/UNI"
fi
python -m pip install -e "${PROJECT_DIR}/UNI"

echo "Setup complete."
