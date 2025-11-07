@echo off
REM Set environment variables
set FLASK_APP=s_api_request.py
set FLASK_ENV=development

REM Start the Flask server
flask run

pause
