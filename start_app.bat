@echo off
echo ========================================
echo Garden Planner Pro - Démarrage Rapide
echo ========================================

echo.
echo 1. Vérification des dépendances...
python --version
node --version
npm --version

echo.
echo 2. Installation des dépendances Python...
pip install -r requirements.txt

echo.
echo 3. Installation des dépendances Node.js...
npm install

echo.
echo 4. Démarrage du backend...
start "Backend" cmd /k "cd app && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo 5. Attente du démarrage du backend...
timeout /t 3 /nobreak >nul

echo.
echo 6. Démarrage du frontend...
start "Frontend" cmd /k "npm run dev"

echo.
echo 7. Attente du démarrage du frontend...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Application démarrée !
echo ========================================
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo ========================================
echo.
echo Appuyez sur une touche pour fermer cette fenêtre...
pause >nul 