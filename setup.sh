#!/bin/bash

# AI-Powered Career Counseling Platform Setup Script
# This script helps set up the development environment

echo "🚀 Setting up AI-Powered Career Counseling Platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check if MongoDB is installed
if ! command -v mongod &> /dev/null; then
    echo "❌ MongoDB is not installed. Please install MongoDB Community Server."
    echo "📖 Follow the instructions in README.md for MongoDB installation."
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Create virtual environment for backend
echo "📦 Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env_template.txt .env
    echo "⚠️  Please update the .env file with your Gemini API key!"
fi

cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install

cd ..

echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update backend/.env with your Gemini API key"
echo "2. Start MongoDB service: sudo systemctl start mongod"
echo "3. Start backend: cd backend && source venv/bin/activate && python app.py"
echo "4. Start frontend: cd frontend && npm start"
echo ""
echo "🌐 The application will be available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5000"
echo ""
echo "📖 For detailed setup instructions, see README.md"


