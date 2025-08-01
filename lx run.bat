@echo off
echo INFO: Activating virtual environment...
call venv\Scripts\activate

echo INFO: Starting Uvicorn server on port 8001...
echo INFO: Access the application at http://localhost:8001
echo INFO: Press Ctrl+C to stop the server.

uvicorn backend.main:app --host 0.0.0.0 --port 8001
