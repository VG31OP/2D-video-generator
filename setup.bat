@echo off
REM =======================================================
REM Zack D. Films 3D Explainer & Instagram Auto-Publisher Setup
REM =======================================================

echo.
echo =======================================================
echo    ZACK D. FILMS 3D EXPLAINER - ONE-CLICK WINDOWS SETUP
echo =======================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

python setup.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Setup encountered an issue. Please review the output above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Setup finished successfully!
pause

