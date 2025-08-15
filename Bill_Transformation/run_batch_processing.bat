@echo off
REM Batch file for running the bill transformation batch processor

echo ===================================
echo Bill Transformation - Batch Processor
echo ===================================

REM Set Python executable (modify if Python is not in PATH)
set PYTHON=python

REM Create output directory if it doesn't exist
if not exist "batch_processing_output" mkdir batch_processing_output

REM Run the batch processor
echo.
echo Starting batch processing...
echo Output will be saved to: %CD%\batch_processing_output
echo.

%PYTHON% batch_processor.py --input-dir test_files --output-dir batch_processing_output

REM Display completion message
echo.
echo ===================================
echo Batch processing completed!
echo Check the log file for details: test_batch_processing.log
echo ===================================

REM Keep the window open
pause
