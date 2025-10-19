from flask_restful import Resource, reqparse
from flask import request, jsonify
import jwt
import bcrypt
from datetime import datetime, timedelta
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.user import UserModel
from utils.database import db

class LoginResource(Resource):
    def __init__(self):
        self.user_model = UserModel(db)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', type=str, required=True, help='Email is required')
        self.parser.add_argument('password', type=str, required=True, help='Password is required')
    
    def post(self):
        """User login"""
        args = self.parser.parse_args()
        email = args['email']
        password = args['password']
        
        # Find user by email
        user = self.user_model.get_user_by_email(email)
        if not user:
            return {'error': 'Invalid email or password'}, 401
        
        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return {'error': 'Invalid email or password'}, 401
        
        # Check if user is active
        if not user.get('is_active', True):
            return {'error': 'Account is deactivated'}, 401
        
        # Generate JWT token
        token = self._generate_token(user['_id'])
        
        # Remove password from response
        user.pop('password', None)
        
        return {
            'message': 'Login successful',
            'token': token,
            'user': {
                '_id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
        }, 200
    
    def _generate_token(self, user_id):
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow()
        }
        
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

class RegisterResource(Resource):
    def __init__(self):
        self.user_model = UserModel(db)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=True, help='Name is required')
        self.parser.add_argument('email', type=str, required=True, help='Email is required')
        self.parser.add_argument('password', type=str, required=True, help='Password is required')
        self.parser.add_argument('role', type=str, default='student', help='User role')
    
    def post(self):
        """User registration"""
        args = self.parser.parse_args()
        email = args['email']
        password = args['password']
        name = args['name']
        role = args['role']
        
        # Check if user already exists
        existing_user = self.user_model.get_user_by_email(email)
        if existing_user:
            return {'error': 'User with this email already exists'}, 400
        
        # Validate required fields
        if not name:
            return {'error': 'Name is required'}, 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user data
        user_data = {
            'email': email,
            'password': hashed_password,
            'name': name,
            'role': role,
            'skills': [],
            'interests': [],
            'career_goals': [],
            'education_background': {},
            'experience_level': 'beginner',
            'preferred_industries': []
        }
        
        # Create user
        user_id = self.user_model.create_user(user_data)
        if not user_id:
            return {'error': 'Failed to create user'}, 500
        
        # Get created user
        user = self.user_model.get_user_by_id(user_id)
        if not user:
            return {'error': 'Failed to retrieve created user'}, 500
        
        # Generate JWT token
        token = self._generate_token(user_id)
        
        # Remove password from response
        user.pop('password', None)
        
        return {
            'message': 'Registration successful',
            'token': token,
            'user': {
                '_id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
        }, 201
    
    def _generate_token(self, user_id):
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow()
        }
        
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token