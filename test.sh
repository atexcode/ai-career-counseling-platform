#!/bin/bash

# Test script for AI-Powered Career Counseling Platform
# This script tests if all components are working correctly

echo "🧪 Testing AI-Powered Career Counseling Platform..."

# Test MongoDB connection
echo "📊 Testing MongoDB connection..."
if pgrep -x "mongod" > /dev/null; then
    echo "✅ MongoDB is running"
else
    echo "❌ MongoDB is not running"
    exit 1
fi

# Test backend
echo "🔧 Testing backend..."
cd backend
source venv/bin/activate

# Check if required packages are installed
python -c "import flask, pymongo, google.generativeai; print('✅ Backend dependencies are installed')" 2>/dev/null || {
    echo "❌ Backend dependencies are missing"
    exit 1
}

# Test if app.py can be imported
python -c "import app; print('✅ Backend app can be imported')" 2>/dev/null || {
    echo "❌ Backend app has import errors"
    exit 1
}

cd ..

# Test frontend
echo "🎨 Testing frontend..."
cd frontend

# Check if node_modules exists
if [ -d "node_modules" ]; then
    echo "✅ Frontend dependencies are installed"
else
    echo "❌ Frontend dependencies are missing"
    exit 1
fi

# Check if package.json exists
if [ -f "package.json" ]; then
    echo "✅ Frontend package.json exists"
else
    echo "❌ Frontend package.json is missing"
    exit 1
fi

cd ..

echo ""
echo "🎉 All tests passed!"
echo ""
echo "📋 To start the application:"
echo "   ./start.sh"
echo ""
echo "📖 For detailed setup instructions, see README.md"


