@echo off
echo ================================================
echo   Prompt Engineering Analyzer - Setup
echo ================================================
echo.

echo [1/3] Verifica Python...
python --version
if errorlevel 1 (
    echo ERRORE: Python non trovato! Installa Python 3.8+ prima di continuare.
    pause
    exit /b 1
)

echo.
echo [2/3] Installazione dipendenze...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERRORE: Installazione fallita!
    pause
    exit /b 1
)

echo.
echo [3/3] Creazione file Excel di esempio...
python create_example_excel.py

echo.
echo ================================================
echo   Setup completato con successo!
echo ================================================
echo.
echo Per avviare l'applicazione, esegui:
echo   run_app.bat
echo.
pause
