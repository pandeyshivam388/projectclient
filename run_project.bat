@echo off
echo Starting Lawsuit Management System...
cd /d "%~dp0"
call venv\Scripts\activate
echo Virtual Environment Activated.
echo Opening Browser...
start http://127.0.0.1:8000/admin/
echo Starting Server...
python manage.py runserver
pause
