@echo off
echo INFO: Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH. Please install Python and try again.
    exit /b 1
)

echo INFO: Creating virtual environment...
if not exist venv (
    python -m venv venv
) else (
    echo INFO: Virtual environment already exists.
)

echo INFO: Activating virtual environment...
call venv\Scripts\activate

echo INFO: Installing dependencies...
pip install -r requirements.txt

echo SUCCESS: Setup complete.
echo INFO: You can now run the application using the run.bat script.
