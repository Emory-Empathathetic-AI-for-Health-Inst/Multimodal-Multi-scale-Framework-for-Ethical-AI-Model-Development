#!/bin/bash
pip install -r requirements.txt
# Clone external tools if they don't exist
[ ! -d "WSITools" ] && git clone https://github.com/smujiang/WSITools.git && cd WSITools && python setup.py install && cd ..
[ ! -d "UNI" ] && git clone https://github.com/mahmoodlab/UNI.git && cd UNI && pip install -e . && cd ..
echo "✅ Setup Complete"