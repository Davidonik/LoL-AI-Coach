@echo off
REM Change directory to the location of this script
cd /d "%~dp0"

REM Set environment variables
set FLASK_APP=s_api_request.py
set FLASK_ENV=development

REM Start the Flask server
flask run

pause
