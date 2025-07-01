@echo off
title Face Recognition Attendance System - Tkinter GUI

echo ========================================
echo   Face Recognition Attendance System
echo             Tkinter GUI
echo ========================================
echo.

cd /d "%~dp0"

echo Starting GUI...
python run_tkinter_gui.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while running the application.
    echo Please check the error message above.
    echo.
    pause
)
