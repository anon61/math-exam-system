@echo off
Title Math Exam Engine - One-Click Installer
cls

echo ========================================================
echo   MATH EXAM ENGINE: WINDOWS AUTO-SETUP
echo   (Using Windows Package Manager 'winget')
echo ========================================================
echo.

:: 1. Install Git
echo [Step 1/5] Checking Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    - Installing Git...
    winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements
) else (
    echo    - Git is already installed.
)
echo.

:: 2. Install VS Code
echo [Step 2/5] Checking VS Code...
code --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    - Installing VS Code...
    winget install -e --id Microsoft.VisualStudioCode --accept-source-agreements --accept-package-agreements
) else (
    echo    - VS Code is already installed.
)
echo.

:: 3. Install Typst
echo [Step 3/5] Checking Typst...
typst --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    - Installing Typst...
    winget install -e --id Typst.Typst --accept-source-agreements --accept-package-agreements
) else (
    echo    - Typst is already installed.
)
echo.

:: 4. Install Python
echo [Step 4/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    - Installing Python 3.11...
    winget install -e --id Python.Python.3.11 --scope machine --accept-source-agreements --accept-package-agreements
    
    echo.
    echo    -------------------------------------------------------
    echo    [ATTENTION] Python has just been installed.
    echo    Windows needs to refresh your system Path.
    echo    PLEASE CLOSE THIS WINDOW AND RUN 'install.bat' AGAIN.
    echo    -------------------------------------------------------
    pause
    exit
) else (
    echo    - Python is already installed.
)
echo.

:: 5. Install Project Dependencies
echo [Step 5/5] Installing Python Libraries (PyYAML)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo    [ERROR] Pip failed. You may need to restart your PC or this script.
    pause
    exit
)

echo.
echo ========================================================
echo   SETUP COMPLETE! RUNNING VERIFICATION...
echo ========================================================
python scripts/check_env.py

pause
