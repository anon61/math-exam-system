@echo off
cd /d "%~dp0"

echo ============================================
echo   MATH EXAM SYSTEM - LAUNCHER
echo ============================================
echo.

:: 1. Run the "Deep Scan" first to ensure code is good
echo [1/2] Verifying System Logic...
python scripts/verify_full_stack.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ SYSTEM CHECK FAILED. FIX THE ERRORS ABOVE FIRST.
    pause
    exit /b
)

:: 2. Launch the Website (Using 'python -m' to bypass PATH bugs)
echo.
echo [2/2] Launching Dashboard...
echo       (Please wait for the browser to open)
echo.

python -m streamlit run app.py

:: 3. Catch crashes
if %errorlevel% neq 0 (
    echo.
    echo ❌ STREAMLIT CRASHED.
    echo    Read the error message above.
    pause
)