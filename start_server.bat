@echo off
title WattWise Energy Optimization System
echo ====================================================================
echo Starting WattWise IoT + DNN + GenAI Server...
echo ====================================================================
echo.
echo Checking Python environment...
python --version
echo.
echo Launching Flask Backend on http://localhost:5000 ...
start http://localhost:5000
python app.py
pause
