@echo off
cd /d "%~dp0"

echo ========================================================
echo   STARTING MATH EXAM DASHBOARD
echo ========================================================
echo.
echo [INFO] Project Root: %CD%
echo [INFO] Launching Streamlit via Python Module...
echo.

:: This command bypasses the PATH issue by asking Python to run Streamlit directly
python -m streamlit run app.py

:: If it crashes, keep window open so we can see the error
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Streamlit crashed! See the message above.
    pause
)