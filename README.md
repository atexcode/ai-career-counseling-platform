# AI-Powered Career Counseling Platform

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

- Python 3.8 or higher
- Node.js 16 or higher
- MongoDB Community Server
- MongoDB Compass (optional GUI for database management)
- Git

## 🚀 Installation & Setup

### 1. MongoDB Installation

#### For Ubuntu/Linux:
```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Create list file for MongoDB
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Update package database
sudo apt-get update

# Install MongoDB
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify installation
mongod --version
```

#### For Windows:
1. Download MongoDB Community Server from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. Run the installer and follow the setup wizard
3. Add MongoDB to your system PATH
4. Start MongoDB service from Services or run `mongod` in command prompt

#### For macOS:
```bash
# Install using Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB service
brew services start mongodb/brew/mongodb-community
```

### 2. Project Setup

1. **Clone the repository:**
```bash
git clone https://github.com/atexcode/ai-career-counseling-platform.git
cd ai-career-counseling-platform
```

update ``backand\.env`` file and add you variables (keep default if it works)

1.1. **Seed Database**
```bash
python seed_database.py
```

2. **Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

3. **Frontend Setup:**
```bash
cd frontend
npm install
npm start
```

4. **Database Configuration:**
- MongoDB will run on `mongodb://localhost:27017`
- Database name: `career_counseling`
- Collections will be created automatically

5. **MongoDB Compass (Optional GUI):**
   - Download MongoDB Compass from [MongoDB Compass Download](https://www.mongodb.com/try/download/compass)
   - Install and connect to `mongodb://localhost:27017`
   - Provides a user-friendly GUI to view and manage your database
   - Useful for debugging, data inspection, and database administration

### 3. Environment Variables

Create a `.env` file in the backend directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
MONGODB_URI=mongodb://localhost:27017/career_counseling
```

## 🎯 Features

### Core Features:
1. **User Profile Management** - Create and manage user profiles
2. **Career Recommendations** - AI-powered career path suggestions
3. **Skills Gap Analysis** - Identify and bridge skill gaps
4. **Job Market Analysis** - Real-time market trends and insights
5. **Interactive Chatbot** - AI-powered career guidance
6. **Career Planning Tools** - Goal setting and progress tracking
7. **User Feedback System** - Improve recommendations
8. **Real-time Notifications** - Stay updated with relevant opportunities
9. **Multi-role Support** - Students, professionals, and admin roles

## 🛠️ Technology Stack

### Backend:
- Python 3.8+
- Flask
- PyMongo
- Google Gemini API
- JWT Authentication

### Frontend:
- React 18
- Material-UI
- Axios
- React Router
- Context API

### Database:
- MongoDB Community Server

## 📁 Project Structure

```
vu_fyp/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── public/
├── README.md
└── requirements_document.txt
```

## 🚀 Running the Application

1. **Start MongoDB:**
```bash
# Linux/Ubuntu
sudo systemctl start mongod

# Windows
net start MongoDB

# macOS
brew services start mongodb/brew/mongodb-community
```

2. **Start Backend:**
```bash
cd backend
python app.py
```

3. **Start Frontend:**
```bash
cd frontend
npm start
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📝 API Documentation

The API documentation will be available at `http://localhost:5000/api/docs` once the backend is running.

## 🤝 Contributing

This is a final year project. For any issues or suggestions, please contact the development team.

## 📄 License

This project is developed for educational purposes as part of a final year project.

## 🆘 Troubleshooting

### Common Issues:

1. **MongoDB Connection Error:**
   - Ensure MongoDB is running: `sudo systemctl status mongod`
   - Check if port 27017 is available
   - Verify MongoDB installation
   - Use MongoDB Compass to test connection: `mongodb://localhost:27017`

2. **Python Dependencies:**
   - Use virtual environment: `python -m venv venv`
   - Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
   - Install requirements: `pip install -r requirements.txt`

3. **Node.js Issues:**
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules and reinstall: `rm -rf node_modules && npm install`

4. **API Key Issues:**
   - Ensure Gemini API key is valid and has sufficient quota
   - Check .env file configuration

## 📞 Support

For technical support or questions about this project, please refer to the project documentation or contact the development team.
