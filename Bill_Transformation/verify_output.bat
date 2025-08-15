@echo off
REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

echo ===================================
echo Bill Transformation - Output Verification
echo ===================================

REM Set Python executable (use 'python' if it's in PATH, or provide full path)
set PYTHON=python

REM Verify Python is available
%PYTHON% --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not found or not in PATH
    echo Please ensure Python is installed and in your system's PATH
    pause
    exit /b 1
)

REM Run the verification script
echo Running verification...
%PYTHON% "%SCRIPT_DIR%verify_output.py" %*

REM Keep the window open only if there was an error
if %ERRORLEVEL% NEQ 0 pause

exit /b %ERRORLEVEL%
