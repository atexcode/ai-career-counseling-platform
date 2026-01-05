from flask_restful import Resource, reqparse
from flask import request, jsonify
import jwt
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.user import UserModel
from utils.database import db

class UserResource(Resource):
    def __init__(self):
        self.user_model = UserModel(db)
        self.parser = reqparse.RequestParser()
    
    def get(self, user_id=None):
        """Get user profile(s)"""
        if user_id:
            # Get specific user
            user = self.user_model.get_user_by_id(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            
            # Remove password from response
            user.pop('password', None)
            return user, 200
        else:
            # Get all users (admin only)
            token = request.headers.get('Authorization')
            if not token:
                return {'error': 'Authorization token required'}, 401
            
            payload = self._verify_token(token)
            if not payload or payload.get('role') != 'admin':
                return {'error': 'Admin access required'}, 403
            
            users = self.user_model.get_all_users()
            # Remove passwords from response
            for user in users:
                user.pop('password', None)
            
            return users, 200
    
    def post(self):
        """Create user profile (registration handled by auth)"""
        return {'error': 'Use /api/auth/register for user registration'}, 400
    
    def put(self, user_id=None):
        """Update user profile"""
        # Check if user_id is provided as query parameter or get from token
        user_id = user_id or request.args.get('user_id')
        
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload:
            return {'error': 'Invalid token'}, 401
        
        # If no user_id provided, use the one from token
        if not user_id:
            user_id = payload.get('user_id')
        
        if not user_id:
            return {'error': 'User ID required'}, 400
        
        # Check if user can update this profile
        if payload.get('user_id') != user_id and payload.get('role') != 'admin':
            return {'error': 'Access denied'}, 403
        
        # Parse update data from request body
        try:
            update_data = request.get_json()
            if not update_data:
                return {'error': 'No data provided'}, 400
        except Exception as e:
            return {'error': 'Invalid JSON data'}, 400
        
        # System fields that should not be updated directly
        system_fields = {'password', '_id', 'created_at', 'updated_at', 'is_active'}
        
        # Remove None values, password, and system fields - allow all other dynamic fields
        update_data = {k: v for k, v in update_data.items() 
                      if v is not None and k not in system_fields}
        
        if not update_data:
            return {'error': 'No data to update'}, 400
        
        # Update user
        success = self.user_model.update_user(user_id, update_data)
        if not success:
            return {'error': 'Failed to update user'}, 500
        
        # Get updated user
        user = self.user_model.get_user_by_id(user_id)
        if not user:
            return {'error': 'Failed to retrieve updated user'}, 500
        
        # Remove password from response
        user.pop('password', None)
        
        return {
            'success': True,
            'message': 'User updated successfully',
            'user': user
        }, 200
    
    def delete(self, user_id=None):
        """Delete user (soft delete)"""
        if not user_id:
            return {'error': 'User ID required'}, 400
        
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload:
            return {'error': 'Invalid token'}, 401
        
        # Check if user can delete this profile
        if payload.get('user_id') != user_id and payload.get('role') != 'admin':
            return {'error': 'Access denied'}, 403
        
        # Delete user
        success = self.user_model.delete_user(user_id)
        if not success:
            return {'error': 'Failed to delete user'}, 500
        
        return {'message': 'User deleted successfully'}, 200
    
    def _verify_token(self, token):
        """Verify JWT token"""
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

