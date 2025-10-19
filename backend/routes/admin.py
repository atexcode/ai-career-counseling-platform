from flask_restful import Resource
from flask import request, jsonify
from models.user import UserModel
from models.career import CareerModel
from models.skills import SkillsModel
from utils.database import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AdminStatsResource(Resource):
    def get(self):
        """Get admin dashboard statistics"""
        try:
            # Get basic statistics
            total_users = db.users.count_documents({})
            total_careers = db.careers.count_documents({})
            total_skills = db.skills.count_documents({})
            
            # Get active sessions (users who logged in within last 24 hours)
            from datetime import datetime, timedelta
            yesterday = datetime.now() - timedelta(days=1)
            active_sessions = db.users.count_documents({
                'last_login': {'$gte': yesterday}
            })
            
            # Get user role distribution
            role_distribution = list(db.users.aggregate([
                {'$group': {'_id': '$role', 'count': {'$sum': 1}}}
            ]))
            
            # Get recent activity
            recent_users = list(db.users.find(
                {},
                {'name': 1, 'email': 1, 'role': 1, 'created_at': 1}
            ).sort('created_at', -1).limit(5))
            
            stats = {
                'total_users': total_users,
                'total_careers': total_careers,
                'total_skills': total_skills,
                'active_sessions': active_sessions,
                'role_distribution': role_distribution,
                'recent_users': recent_users
            }
            
            return jsonify({
                'success': True,
                'stats': stats
            })
            
        except Exception as e:
            logger.error(f"Error getting admin stats: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to get admin statistics'
            }), 500

class AdminUsersResource(Resource):
    def get(self):
        """Get all users for admin management"""
        try:
            users = list(db.users.find(
                {},
                {'password': 0}  # Exclude password from response
            ).sort('created_at', -1))
            
            # Convert ObjectId to string for JSON serialization
            for user in users:
                user['_id'] = str(user['_id'])
                if 'created_at' in user:
                    user['created_at'] = user['created_at'].isoformat()
                if 'updated_at' in user:
                    user['updated_at'] = user['updated_at'].isoformat()
            
            return jsonify({
                'success': True,
                'users': users
            })
            
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to get users'
            }), 500
    
    def post(self):
        """Create a new user (admin only)"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'email', 'password', 'role']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            # Check if user already exists
            existing_user = db.users.find_one({'email': data['email']})
            if existing_user:
                return jsonify({
                    'success': False,
                    'error': 'User with this email already exists'
                }), 400
            
            # Create user
            user_model = UserModel(db)
            user_id = user_model.create_user(
                name=data['name'],
                email=data['email'],
                password=data['password'],
                role=data['role']
            )
            
            return jsonify({
                'success': True,
                'user_id': str(user_id),
                'message': 'User created successfully'
            })
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to create user'
            }), 500

class AdminUserResource(Resource):
    def put(self, user_id):
        """Update a user (admin only)"""
        try:
            data = request.get_json()
            
            # Prepare update data
            update_data = {}
            if 'name' in data:
                update_data['name'] = data['name']
            if 'email' in data:
                update_data['email'] = data['email']
            if 'role' in data:
                update_data['role'] = data['role']
            if 'password' in data and data['password']:
                import bcrypt
                update_data['password'] = bcrypt.hashpw(
                    data['password'].encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
            
            update_data['updated_at'] = datetime.now()
            
            # Update user
            result = db.users.update_one(
                {'_id': user_id},
                {'$set': update_data}
            )
            
            if result.matched_count == 0:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'User updated successfully'
            })
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to update user'
            }), 500
    
    def delete(self, user_id):
        """Delete a user (admin only)"""
        try:
            result = db.users.delete_one({'_id': user_id})
            
            if result.deleted_count == 0:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'User deleted successfully'
            })
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to delete user'
            }), 500
