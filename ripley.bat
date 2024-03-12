@echo off
CALL .\installer.bat
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
python .\src\main.py --ripley
call venv\Scripts\deactivate.bat
