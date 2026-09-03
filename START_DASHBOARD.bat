@echo off
title BusEye - Dashboard (Streamlit + Folium)
echo.
echo  ======================================
echo   BusEye - Starting Streamlit Dashboard
echo  ======================================
echo.

cd /d "%~dp0backend"

:: Use backend venv (has all packages)
if not exist "venv" (
    echo  [1/3] Creating Python environment...
    python -m venv venv
)

call venv\Scripts\activate

:: Install dashboard packages
echo  [2/3] Installing Streamlit + Folium packages...
pip install streamlit streamlit-folium folium plotly pandas boto3 python-dotenv -q

:: Run Streamlit
echo  [3/3] Starting dashboard...
echo.
echo  Open your browser at: http://localhost:8501
echo  Press Ctrl+C to stop
echo.
cd /d "%~dp0dashboard"
set PYTHONIOENCODING=utf-8
streamlit run app.py --server.port 8501 --server.headless false --theme.base dark
pause
