# AI-Powered Career Counseling Platform - Windows Setup Guide

A comprehensive career counseling platform that uses Artificial Intelligence to provide personalized career recommendations, skills gap analysis, and job market insights.

## 🎯 Project Overview

This platform helps students and professionals make informed career decisions by:
- Creating detailed user profiles with skills and interests
- Providing AI-powered career path recommendations
- Analyzing skills gaps and suggesting learning resources
- Offering interactive career guidance through a chatbot
- Providing job market analysis and trends
- Supporting career planning with goal setting and tracking

## 🏗️ System Architecture

- **Backend**: Python Flask with RESTful APIs
- **Frontend**: React.js with Material-UI
- **Database**: MongoDB (locally installed)
- **AI Integration**: Google Gemini API
- **Real-time**: Server-Sent Events (SSE)

## 📋 Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.8 or higher** - Download from [python.org](https://www.python.org/downloads/)
- **Node.js 16 or higher** - Download from [nodejs.org](https://nodejs.org/)
- **MongoDB Community Server** - Download from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
- **MongoDB Compass** (Optional) - GUI for database management from [MongoDB Compass](https://www.mongodb.com/try/download/compass)
- **Git** - Download from [git-scm.com](https://git-scm.com/download/win)

## 🚀 Quick Setup (Automated)

### Option 1: Using Setup Script (Recommended)

1. **Open Command Prompt or PowerShell** in the project directory
2. **Run the setup script:**
   ```cmd
   setup.cmd
   ```
3. **Follow the on-screen instructions**

The setup script will:
- Check for required software
- Create Python virtual environment
- Install backend dependencies
- Install frontend dependencies
- Create environment file template
- Seed the database with initial data

### Option 2: Manual Setup

Follow the detailed steps below if you prefer manual setup.

## 📦 Manual Installation Steps

### 1. MongoDB Installation

1. **Download MongoDB Community Server:**
   - Visit [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - Select Windows as your platform
   - Download the MSI installer

2. **Install MongoDB:**
   - Run the downloaded MSI installer
   - Choose "Complete" installation
   - Select "Install MongoDB as a Service"
   - Keep default settings (Service Name: MongoDB, Data Directory: C:\Program Files\MongoDB\Server\[version]\data)
   - Install MongoDB Compass (optional but recommended)

3. **Verify Installation:**
   - Open Command Prompt
   - Run: `mongod --version`
   - You should see MongoDB version information

4. **Start MongoDB Service:**
   - MongoDB should start automatically as a Windows service
   - If not, open Services (services.msc) and start "MongoDB" service
   - Or run: `net start MongoDB` in Command Prompt (as Administrator)

5. **Connect with MongoDB Compass (Optional):**
   - Open MongoDB Compass
   - Connect to: `mongodb://localhost:27017`
   - You should see the default databases

### 2. Python Setup

1. **Install Python:**
   - Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
   - **Important**: Check "Add Python to PATH" during installation
   - Verify installation: `python --version`

2. **Create Virtual Environment:**
   ```cmd
   cd backend
   python -m venv venv
   ```

3. **Activate Virtual Environment:**
   ```cmd
   venv\Scripts\activate
   ```

4. **Install Dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

### 3. Node.js Setup

1. **Install Node.js:**
   - Download from [nodejs.org](https://nodejs.org/)
   - Run the installer with default settings
   - Verify installation: `node --version` and `npm --version`

2. **Install Frontend Dependencies:**
   ```cmd
   cd frontend
   npm install
   ```

### 4. Environment Configuration

1. **Create `.env` file in the `backend` directory:**
   ```cmd
   cd backend
   copy env_template.txt .env
   ```

2. **Edit `.env` file and add your configuration:**
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   JWT_SECRET_KEY=your_secret_key_here
   MONGODB_URI=mongodb://localhost:27017/career_counseling
   ```

   **To get Gemini API Key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy and paste it in the `.env` file

### 5. Database Seeding

1. **Seed the database with initial data:**
   ```cmd
   cd backend
   venv\Scripts\activate
   python seed_database.py
   ```

   This will create:
   - Default admin user (admin@careercounseling.com / admin123)
   - Sample user accounts
   - Sample career data
   - Sample skills data

## 🚀 Starting the Application

### Option 1: Using Start Script (Recommended)

1. **Open Command Prompt** in the project directory
2. **Run the start script:**
   ```cmd
   start.cmd
   ```

The script will:
- Check if MongoDB is running
- Start the backend server on http://localhost:5000
- Start the frontend server on http://localhost:3000
- Open the application in your default browser

### Option 2: Manual Start

1. **Start Backend:**
   ```cmd
   cd backend
   venv\Scripts\activate
   python app.py
   ```

2. **Start Frontend (in a new terminal):**
   ```cmd
   cd frontend
   npm start
   ```

3. **Access the Application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## 🔧 Troubleshooting

### MongoDB Issues

**Problem**: MongoDB service won't start
- **Solution**: Run Command Prompt as Administrator and execute: `net start MongoDB`

**Problem**: Cannot connect to MongoDB
- **Solution**: 
  - Check if MongoDB service is running: `sc query MongoDB`
  - Verify port 27017 is not blocked by firewall
  - Try connecting with MongoDB Compass: `mongodb://localhost:27017`

**Problem**: MongoDB Compass cannot connect
- **Solution**: 
  - Ensure MongoDB service is running
  - Check connection string: `mongodb://localhost:27017`
  - Try restarting MongoDB service

### Python Issues

**Problem**: `python` command not found
- **Solution**: 
  - Reinstall Python and check "Add Python to PATH"
  - Or use `py` instead of `python` on Windows
  - Add Python to PATH manually

**Problem**: Virtual environment activation fails
- **Solution**: 
  - Ensure you're in the `backend` directory
  - Use: `venv\Scripts\activate` (not `venv/Scripts/activate`)
  - If PowerShell, use: `venv\Scripts\Activate.ps1`

**Problem**: `pip install` fails
- **Solution**: 
  - Upgrade pip: `python -m pip install --upgrade pip`
  - Use: `python -m pip install -r requirements.txt`

### Node.js Issues

**Problem**: `npm` command not found
- **Solution**: 
  - Reinstall Node.js
  - Restart Command Prompt after installation
  - Verify installation: `npm --version`

**Problem**: `npm install` fails
- **Solution**: 
  - Clear npm cache: `npm cache clean --force`
  - Delete `node_modules` and `package-lock.json`
  - Run `npm install` again

**Problem**: Port 3000 already in use
- **Solution**: 
  - Close other applications using port 3000
  - Or change port in `frontend/package.json`: `"start": "set PORT=3001 && react-scripts start"`

### Backend Issues

**Problem**: Backend won't start
- **Solution**: 
  - Check if port 5000 is available
  - Verify `.env` file exists and has correct values
  - Check MongoDB is running
  - Review error messages in terminal

**Problem**: API returns 401 Unauthorized
- **Solution**: 
  - Check if JWT_SECRET_KEY is set in `.env`
  - Verify token in browser localStorage
  - Try logging in again

### Frontend Issues

**Problem**: Frontend shows connection errors
- **Solution**: 
  - Verify backend is running on http://localhost:5000
  - Check browser console for errors
  - Verify CORS is enabled in backend

**Problem**: Blank screen or errors
- **Solution**: 
  - Clear browser cache
  - Check browser console for errors
  - Verify all dependencies are installed: `npm install`

## 📝 Default Login Credentials

After seeding the database, you can use these credentials:

- **Admin User:**
  - Email: `admin@careercounseling.com`
  - Password: `admin123`

- **Regular User:**
  - Email: `john.student@email.com`
  - Password: `student123`

## 🔐 Environment Variables

Create a `.env` file in the `backend` directory with:

```
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET_KEY=your_secret_key_here_change_this
MONGODB_URI=mongodb://localhost:27017/career_counseling
```

## 📚 Project Structure

```
vu_fyp/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── .env                # Environment variables (create this)
│   ├── models/             # Database models
│   ├── routes/             # API routes
│   ├── services/           # Business logic services
│   └── utils/              # Utility functions
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── context/       # React context providers
│   │   └── utils/          # Utility functions
│   └── package.json       # Node.js dependencies
├── setup.cmd              # Windows setup script
├── start.cmd              # Windows start script
└── win_readme.md          # This file
```

## 🆘 Getting Help

If you encounter issues:

1. Check the Troubleshooting section above
2. Review error messages in terminal/console
3. Verify all prerequisites are installed correctly
4. Ensure MongoDB service is running
5. Check that ports 3000 and 5000 are not in use

## 📄 License

This project is part of a Final Year Project (FYP).

---

**Happy Coding! 🚀**


