@echo off
REM Script per preparare e caricare il progetto su GitHub
REM Esegui questo script DOPO aver creato il repository su GitHub

echo ========================================
echo  Setup Repository GitHub
echo ========================================
echo.

REM Chiedi all'utente il repository GitHub
set /p GITHUB_REPO="Inserisci l'URL del tuo repository GitHub (es. https://github.com/username/repo.git): "

echo.
echo Verifico se git e' installato...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Git non e' installato!
    echo Scaricalo da: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo.
echo Inizializzo repository git locale...
if not exist .git (
    git init
    echo Repository git locale creato!
) else (
    echo Repository git gia' esistente.
)

echo.
echo Aggiungo tutti i file al repository...
git add .

echo.
echo Creo commit iniziale...
git commit -m "Initial commit: Prompt Engineering Analysis App" 2>nul
if errorlevel 1 (
    echo Nessuna modifica da committare o commit gia' esistente.
) else (
    echo Commit creato!
)

echo.
echo Collego il repository remoto GitHub...
git remote remove origin 2>nul
git remote add origin %GITHUB_REPO%
if errorlevel 1 (
    echo ERRORE: Impossibile collegare il repository remoto.
    echo Verifica che l'URL sia corretto.
    pause
    exit /b 1
)

echo.
echo Rinomino branch principale in "main"...
git branch -M main

echo.
echo Carico il codice su GitHub...
echo Potrebbero essere richieste le credenziali GitHub.
git push -u origin main
if errorlevel 1 (
    echo.
    echo ERRORE durante il push!
    echo Verifica:
    echo - Di aver creato il repository su GitHub
    echo - Di avere i permessi per scrivere nel repository
    echo - Di aver inserito le credenziali corrette
    pause
    exit /b 1
)

echo.
echo ========================================
echo  SUCCESSO! Codice caricato su GitHub
echo ========================================
echo.
echo Prossimi passi:
echo 1. Vai su https://share.streamlit.io/
echo 2. Accedi con GitHub
echo 3. Clicca "New app"
echo 4. Seleziona il tuo repository
echo 5. Imposta Main file: app.py
echo 6. Clicca "Deploy!"
echo.
echo L'app sara' online in pochi minuti!
echo.
pause
