@echo off
REM Batch file for running end-to-end tests

echo ===================================
echo Bill Transformation - End-to-End Tests
echo ===================================

REM Set Python executable (modify if Python is not in PATH)
set PYTHON=python

REM Install required packages
echo Installing required packages...
%PYTHON% -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install required packages
    pause
    exit /b %ERRORLEVEL%
)

REM Run the end-to-end tests
echo Running end-to-end tests...
%PYTHON% test_end_to_end.py %*

REM Show test status
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================
    echo ✅ ALL TESTS PASSED
    echo ===================================
    echo.
    timeout /t 5
) else (
    echo.
    echo ===================================
    echo ❌ SOME TESTS FAILED
    echo ===================================
    echo.
    pause
)

exit /b %ERRORLEVEL%
