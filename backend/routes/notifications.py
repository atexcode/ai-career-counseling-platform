from flask_restful import Resource, reqparse
from flask import request, jsonify, Response
import jwt
import os
from datetime import datetime
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.user import UserModel
from services.gemini_service import GeminiService
from utils.database import db

class NotificationsResource(Resource):
    def __init__(self):
        self.user_model = UserModel(db)
        self.gemini_service = GeminiService()
        self.parser = reqparse.RequestParser()
    
    def get(self, user_id=None):
        """Get notifications or SSE stream"""
        if user_id:
            # Get notifications for specific user
            return self._get_user_notifications(user_id)
        else:
            # Get all notifications (admin only)
            return self._get_all_notifications()
    
    def _get_user_notifications(self, user_id):
        """Get notifications for user"""
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload:
            return {'error': 'Invalid token'}, 401
        
        # Check if user can access this data
        if payload.get('user_id') != user_id and payload.get('role') != 'admin':
            return {'error': 'Access denied'}, 403
        
        # Get notifications from database
        try:
            notifications = list(db.notifications.find(
                {'user_id': user_id}
            ).sort('timestamp', -1).limit(50))
            
            for notification in notifications:
                notification['_id'] = str(notification['_id'])
            
            return {
                'notifications': notifications,
                'user_id': user_id,
                'count': len(notifications)
            }, 200
            
        except Exception as e:
            return {'error': f'Failed to get notifications: {str(e)}'}, 500
    
    def _get_all_notifications(self):
        """Get all notifications (admin only)"""
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload or payload.get('role') != 'admin':
            return {'error': 'Admin access required'}, 403
        
        # Get all notifications
        try:
            notifications = list(db.notifications.find().sort('timestamp', -1).limit(100))
            
            for notification in notifications:
                notification['_id'] = str(notification['_id'])
            
            return {
                'notifications': notifications,
                'count': len(notifications)
            }, 200
            
        except Exception as e:
            return {'error': f'Failed to get notifications: {str(e)}'}, 500
    
    def post(self):
        """Create notification or send SSE notification"""
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload:
            return {'error': 'Invalid token'}, 401
        
        # Parse notification data
        self.parser.add_argument('user_id', type=str, required=True, help='User ID is required')
        self.parser.add_argument('title', type=str, required=True, help='Title is required')
        self.parser.add_argument('message', type=str, required=True, help='Message is required')
        self.parser.add_argument('type', type=str, default='info', help='Notification type')
        self.parser.add_argument('priority', type=str, default='medium', help='Priority level')
        
        args = self.parser.parse_args()
        
        # Check if user can send notifications
        if payload.get('user_id') != args['user_id'] and payload.get('role') != 'admin':
            return {'error': 'Access denied'}, 403
        
        # Create notification
        try:
            notification_data = {
                'user_id': args['user_id'],
                'title': args['title'],
                'message': args['message'],
                'type': args['type'],
                'priority': args['priority'],
                'is_read': False,
                'timestamp': datetime.now()
            }
            
            result = db.notifications.insert_one(notification_data)
            notification_id = str(result.inserted_id)
            
            # Get created notification
            notification = db.notifications.find_one({'_id': result.inserted_id})
            if notification:
                notification['_id'] = str(notification['_id'])
            
            return {
                'message': 'Notification created successfully',
                'notification': notification
            }, 201
            
        except Exception as e:
            return {'error': f'Failed to create notification: {str(e)}'}, 500
    
    def put(self, notification_id=None):
        """Mark notification as read"""
        if not notification_id:
            return {'error': 'Notification ID required'}, 400
        
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload:
            return {'error': 'Invalid token'}, 401
        
        # Mark notification as read
        try:
            from bson import ObjectId
            result = db.notifications.update_one(
                {'_id': ObjectId(notification_id)},
                {'$set': {'is_read': True, 'read_at': datetime.now()}}
            )
            
            if result.modified_count == 0:
                return {'error': 'Notification not found'}, 404
            
            return {'message': 'Notification marked as read'}, 200
            
        except Exception as e:
            return {'error': f'Failed to update notification: {str(e)}'}, 500
    
    def delete(self, notification_id=None):
        """Delete notification"""
        if not notification_id:
            return {'error': 'Notification ID required'}, 400
        
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload:
            return {'error': 'Invalid token'}, 401
        
        # Delete notification
        try:
            from bson import ObjectId
            result = db.notifications.delete_one({'_id': ObjectId(notification_id)})
            
            if result.deleted_count == 0:
                return {'error': 'Notification not found'}, 404
            
            return {'message': 'Notification deleted successfully'}, 200
            
        except Exception as e:
            return {'error': f'Failed to delete notification: {str(e)}'}, 500
    
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

