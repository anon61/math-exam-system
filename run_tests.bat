@echo off
Title Math Exam Engine - Master Test Suite
cls

echo ========================================================
echo   MATH EXAM ENGINE: SYSTEM VERIFICATION
echo ========================================================
echo.

:: 1. Database Integrity (The Librarian)
echo [1/4] Checking Knowledge Graph Integrity...
python scripts/check_integrity.py
if %errorlevel% neq 0 goto fail

:: 2. Backend Unit Tests (The Guardrails)
echo.
echo [2/4] Running Backend Unit Tests...
python tests/test_backend.py
if %errorlevel% neq 0 goto fail

:: 3. Stress Test (The Chaos Monkey)
echo.
echo [3/4] Running Stress Test (Data Injection/Deletion)...
python tests/test_stress.py
if %errorlevel% neq 0 goto fail

:: 4. Full Render Pass (The Smoke Test)
echo.
echo [4/4] Compiling Full Database Visualization...
typst compile --root . tests/full_render.typ
if %errorlevel% neq 0 goto fail

echo.
echo ========================================================
echo   ALL TESTS PASSED - SYSTEM IS STABLE
echo ========================================================
echo Output: tests/full_render.pdf
pause
exit /b 0

:fail
echo.
echo ========================================================
echo   TESTS FAILED - CHECK OUTPUT ABOVE
echo ========================================================
pause
exit /b 1
