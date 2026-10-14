$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e WSITools
Write-Host "Setup complete. Run: python main.py --data-dir 'C:\path\to\existing\data'"
