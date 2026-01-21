@echo off
REM compile.bat - Compila e tiene solo il .exe
chcp 65001 > nul
echo ========================================
echo COMPILATORE PULITO PYTHON -> .EXE
echo ========================================

REM 1. Verifica che sia stato passato un file
if "%~1"=="" (
    echo.
    echo Errore: Specifica un file .py
    echo Esempio: compile.bat mio_script.py
    echo.
    pause
    exit /b 1
)

REM 2. Estrai nome file senza estensione
set SCRIPT_PATH=%~1
set SCRIPT_NAME=%~n1
set SCRIPT_DIR=%~dp1

echo.
echo Script: %SCRIPT_PATH%
echo Nome: %SCRIPT_NAME%
echo Cartella: %SCRIPT_DIR%
echo.

REM 3. Crea cartella temporanea
set TEMP_DIR=%TEMP%\pyinstaller_%RANDOM%
mkdir "%TEMP_DIR%" > nul 2>&1

REM 4. Installa PyInstaller se necessario
echo [1/5] Verifica PyInstaller...
python -m pip install pyinstaller --quiet > nul 2>&1

REM 5. Compila nella cartella temporanea
echo [2/5] Compilazione in corso...
pyinstaller --onefile --noconsole ^
            --distpath "%TEMP_DIR%" ^
            --workpath "%TEMP_DIR%\build" ^
            --specpath "%TEMP_DIR%" ^
            "%SCRIPT_PATH%"

if errorlevel 1 (
    echo ❌ Errore nella compilazione
    rmdir /s /q "%TEMP_DIR%" > nul 2>&1
    pause
    exit /b 1
)

echo [3/5] Compilazione completata!

REM 6. Trova e sposta il .exe
echo [4/5] Spostamento .exe...
if exist "%TEMP_DIR%\%SCRIPT_NAME%.exe" (
    set EXE_SRC=%TEMP_DIR%\%SCRIPT_NAME%.exe
) else (
    REM Cerca qualsiasi .exe nella temp
    for /f "delims=" %%i in ('dir /b "%TEMP_DIR%\*.exe" 2^>nul') do (
        set EXE_SRC=%TEMP_DIR%\%%i
    )
)

if not exist "%EXE_SRC%" (
    echo ❌ .exe non trovato
    rmdir /s /q "%TEMP_DIR%" > nul 2>&1
    pause
    exit /b 1
)

REM Sposta nella stessa cartella dello script
set EXE_DEST=%SCRIPT_DIR%%SCRIPT_NAME%.exe

REM Se esiste già, aggiungi numero
set COUNTER=1
:check_exists
if exist "%EXE_DEST%" (
    set EXE_DEST=%SCRIPT_DIR%%SCRIPT_NAME%_%COUNTER%.exe
    set /a COUNTER+=1
    goto check_exists
)

move "%EXE_SRC%" "%EXE_DEST%" > nul

REM 7. Pulisci
echo [5/5] Pulizia file temporanei...
rmdir /s /q "%TEMP_DIR%" > nul 2>&1

REM 8. Mostra risultato
echo.
echo ========================================
echo ✅ COMPILAZIONE COMPLETATA!
echo.
echo 📁 .exe creato:
echo    %EXE_DEST%
echo.
echo 🧹 Nessun altro file residuo
echo ========================================
echo.

REM 9. Chiedi se aprire la cartella
choice /c sn /m "Vuoi aprire la cartella contenente il .exe?"
if errorlevel 2 goto end
explorer /select,"%EXE_DEST%"

:end
pause
