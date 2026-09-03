@echo off
title BusEye - GPS Simulator (5 Buses)
echo.
echo  ======================================
echo   BusEye - Starting Bus GPS Simulator
echo  ======================================
echo.
echo  This will simulate 5 buses moving across Delhi
echo  sending detections (potholes, incidents, etc.)
echo  to the backend in real-time.
echo.

cd /d "%~dp0backend"
call venv\Scripts\activate

cd /d "%~dp0ai_engine"
echo  Deploying 5 buses... Watch the map!
echo.
python gps_simulator.py
pause
