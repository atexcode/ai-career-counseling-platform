@echo off
REM Start script for AI-Powered Career Counseling Platform (Windows)
REM This script starts both backend and frontend services

echo ========================================
echo AI-Powered Career Counseling Platform
echo Starting Services...
echo ========================================
echo.

REM Check if MongoDB is running
echo [1/3] Checking MongoDB service...
sc query MongoDB | findstr "RUNNING" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] MongoDB service is not running
    echo Attempting to start MongoDB service...
    net start MongoDB >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] MongoDB service started
        timeout /t 3 /nobreak >nul
    ) else (
        echo [ERROR] Could not start MongoDB service
        echo Please start it manually: net start MongoDB (as Administrator)
        echo Or start MongoDB manually and run this script again
        pause
        exit /b 1
    )
) else (
    echo [OK] MongoDB service is running
)
echo.

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo [ERROR] Virtual environment not found
    echo Please run setup.cmd first to set up the project
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist "backend\.env" (
    echo [WARNING] .env file not found
    echo Creating basic .env file...
    cd backend
    (
        echo GEMINI_API_KEY=your_gemini_api_key_here
        echo JWT_SECRET_KEY=your_secret_key_here_change_this
        echo MONGODB_URI=mongodb://localhost:27017/career_counseling
    ) > .env
    cd ..
    echo [OK] Created basic .env file
    echo [IMPORTANT] Please edit backend\.env and add your GEMINI_API_KEY
    echo.
)

REM Start backend server
echo [2/3] Starting backend server...
cd backend
start "Backend Server" cmd /k "venv\Scripts\activate.bat && python app.py"
cd ..
timeout /t 3 /nobreak >nul
echo [OK] Backend server starting on http://localhost:5000
echo.

REM Start frontend server
echo [3/3] Starting frontend server...
cd frontend
start "Frontend Server" cmd /k "npm start"
cd ..
echo [OK] Frontend server starting on http://localhost:3000
echo.

echo ========================================
echo Services Started!
echo ========================================
echo.
echo Application URLs:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:5000
echo.
echo Two new command windows have opened:
echo   - Backend Server (Flask)
echo   - Frontend Server (React)
echo.
echo To stop the services:
echo   1. Close the Backend Server window
echo   2. Close the Frontend Server window
echo   3. Or press Ctrl+C in each window
echo.
echo The application will open in your default browser shortly...
echo.
timeout /t 5 /nobreak >nul
start http://localhost:3000
echo.
pause


