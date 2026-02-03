@echo off
REM Paper Reading Agent - One-Click Startup Script (Windows)
REM This script sets up and runs both backend and frontend servers

setlocal enabledelayedexpansion

echo ================================================
echo    Paper Reading Agent - Startup Script
echo ================================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

REM Step 1: Check prerequisites
echo [1/6] Checking prerequisites...

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed. Please install Python 3.12+
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 16+
    exit /b 1
)

for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION% found

where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm is not installed. Please install npm
    exit /b 1
)

for /f "tokens=1" %%i in ('npm --version') do set NPM_VERSION=%%i
echo [OK] npm %NPM_VERSION% found
echo.

REM Step 2: Check environment file
echo [2/6] Checking environment configuration...

if not exist "%BACKEND_DIR%\.env" (
    echo [ERROR] Backend .env file not found!
    echo Creating template .env file...
    (
        echo # Google Gemini API Key
        echo # Get your API key from: https://ai.google.dev/
        echo GOOGLE_API_KEY=your_api_key_here
    ) > "%BACKEND_DIR%\.env"
    echo [ERROR] Please edit backend\.env and add your GOOGLE_API_KEY
    echo   Get your API key from: https://ai.google.dev/
    exit /b 1
)

findstr /C:"your_api_key_here" "%BACKEND_DIR%\.env" >nul
if %ERRORLEVEL% EQU 0 (
    echo [ERROR] Please set your GOOGLE_API_KEY in backend\.env
    echo   Get your API key from: https://ai.google.dev/
    exit /b 1
)

echo [OK] Environment file configured
echo.

REM Step 3: Install backend dependencies
echo [3/6] Installing backend dependencies...
cd /d "%BACKEND_DIR%"

if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install backend dependencies
    exit /b 1
)

echo [OK] Backend dependencies installed
echo.

REM Step 4: Install frontend dependencies
echo [4/6] Installing frontend dependencies...
cd /d "%FRONTEND_DIR%"

if not exist "node_modules" (
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install frontend dependencies
        exit /b 1
    )
) else (
    echo Frontend dependencies already installed
)

echo [OK] Frontend dependencies ready
echo.

REM Step 5: Start servers
echo [5/6] Starting backend server...
cd /d "%BACKEND_DIR%"

start "Paper Reading Agent - Backend" cmd /c "venv\Scripts\activate.bat && python app.py"

timeout /t 3 /nobreak >nul

echo [OK] Backend started on http://localhost:5000
echo.

echo [6/6] Starting frontend server...
cd /d "%FRONTEND_DIR%"

start "Paper Reading Agent - Frontend" cmd /c "set BROWSER=none && npm start"

timeout /t 5 /nobreak >nul

echo.
echo ================================================
echo    Paper Reading Agent is running!
echo ================================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to open the application in your browser...
pause >nul

start http://localhost:3000

echo.
echo To stop the servers, close the backend and frontend windows.
echo.
