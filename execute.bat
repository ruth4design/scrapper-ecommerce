@echo off
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
python .\src\main.py %*
call venv\Scripts\deactivate.bat
