@echo off
REM Setup script for AI-Powered Career Counseling Platform (Windows)
REM This script sets up the project for first-time use

echo ========================================
echo AI-Powered Career Counseling Platform
echo Windows Setup Script
echo ========================================
echo.

REM Check for Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo [OK] Python is installed
echo.

REM Check for Node.js
echo [2/6] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
node --version
npm --version
echo [OK] Node.js is installed
echo.

REM Check for MongoDB
echo [3/6] Checking MongoDB installation...
mongod --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] MongoDB is not installed or not in PATH
    echo Please install MongoDB from https://www.mongodb.com/try/download/community
    echo The application may not work without MongoDB
    echo.
) else (
    mongod --version | findstr "version"
    echo [OK] MongoDB is installed
    echo.
    
    REM Check if MongoDB service is running
    sc query MongoDB | findstr "RUNNING" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [WARNING] MongoDB service is not running
        echo Attempting to start MongoDB service...
        net start MongoDB >nul 2>&1
        if %errorlevel% equ 0 (
            echo [OK] MongoDB service started
        ) else (
            echo [WARNING] Could not start MongoDB service automatically
            echo Please start it manually: net start MongoDB (as Administrator)
        )
        echo.
    ) else (
        echo [OK] MongoDB service is running
        echo.
    )
)

REM Create Python virtual environment
echo [4/6] Setting up Python virtual environment...
if not exist "backend\venv" (
    echo Creating virtual environment...
    cd backend
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Install Python dependencies
echo [5/6] Installing Python dependencies...
cd backend
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    cd ..
    pause
    exit /b 1
)
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    cd ..
    pause
    exit /b 1
)
echo [OK] Python dependencies installed
cd ..
echo.

REM Install Node.js dependencies
echo [6/6] Installing Node.js dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing npm packages (this may take a few minutes)...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install Node.js dependencies
        cd ..
        pause
        exit /b 1
    )
    echo [OK] Node.js dependencies installed
) else (
    echo [OK] Node.js dependencies already installed
)
cd ..
echo.

REM Create .env file if it doesn't exist
echo Creating environment file...
cd backend
if not exist ".env" (
    if exist "env_template.txt" (
        copy env_template.txt .env >nul
        echo [OK] Created .env file from template
        echo [IMPORTANT] Please edit backend\.env and add your GEMINI_API_KEY
    ) else (
        echo [WARNING] env_template.txt not found, creating basic .env file...
        (
            echo GEMINI_API_KEY=your_gemini_api_key_here
            echo JWT_SECRET_KEY=your_secret_key_here_change_this
            echo MONGODB_URI=mongodb://localhost:27017/career_counseling
        ) > .env
        echo [OK] Created basic .env file
        echo [IMPORTANT] Please edit backend\.env and add your GEMINI_API_KEY
    )
) else (
    echo [OK] .env file already exists
)
cd ..
echo.

REM Ask about database seeding
echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Would you like to seed the database with initial data? (Y/N)
set /p seed_choice="Enter choice: "
if /i "%seed_choice%"=="Y" (
    echo.
    echo Seeding database...
    cd backend
    call venv\Scripts\activate.bat
    python seed_database.py
    if %errorlevel% equ 0 (
        echo [OK] Database seeded successfully
    ) else (
        echo [WARNING] Database seeding failed, but you can run it later
    )
    cd ..
    echo.
)

echo.
echo ========================================
echo Setup Summary
echo ========================================
echo [OK] Python virtual environment created
echo [OK] Python dependencies installed
echo [OK] Node.js dependencies installed
echo [OK] Environment file created
echo.
echo Next Steps:
echo 1. Edit backend\.env and add your GEMINI_API_KEY
echo    Get it from: https://makersuite.google.com/app/apikey
echo 2. Run start.cmd to start the application
echo 3. Open http://localhost:3000 in your browser
echo.
echo Default login credentials (after seeding):
echo - Admin: admin@careercounseling.com / admin123
echo - User: john.student@email.com / student123
echo.
pause


