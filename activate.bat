@echo off

echo Setting up the development environment...

:: Check if backend/venv exists
if not exist backend\venv (
    echo Creating virtual environment...
    python -m venv backend\venv
)

:: Activate virtual environment
echo Activating virtual environment...
call backend\venv\Scripts\activate

:: Install backend dependencies
echo Installing backend dependencies...
pip install -r backend\requirements.txt
cd backend


echo Setup complete!
echo.
echo To start the servers:
echo Backend: cd backend && python app.py
echo.

:: Keep terminal open
cmd /k