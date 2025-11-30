from flask_restful import Resource, reqparse
from flask import request, jsonify
import jwt
import os
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.user import UserModel
from services.gemini_service import GeminiService
from utils.database import db

class ChatbotResource(Resource):
    def __init__(self):
        self.user_model = UserModel(db)
        self.gemini_service = GeminiService()
        self.parser = reqparse.RequestParser()
    
    def post(self):
        """Handle chatbot messages"""
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload:
            return {'error': 'Invalid token'}, 401
        
        user_id = payload.get('user_id')
        
        # Parse message data from request body
        try:
            data = request.get_json()
            if not data:
                return {'error': 'No data provided'}, 400
            
            message = data.get('message')
            if not message:
                return {'error': 'Message is required'}, 400
            
            context = data.get('context', '')
            conversation_history = data.get('conversation_history', [])
            
        except Exception as e:
            return {'error': 'Invalid JSON data'}, 400
        
        # Get user profile for context
        user = self.user_model.get_user_by_id(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        
        # Build context string
        user_context = f"""
        User Profile:
        - Name: {user.get('name', 'Unknown')}
        - Skills: {', '.join(user.get('skills', []))}
        - Interests: {', '.join(user.get('interests', []))}
        - Career Goals: {', '.join(user.get('career_goals', []))}
        - Experience Level: {user.get('experience_level', 'beginner')}
        - Preferred Industries: {', '.join(user.get('preferred_industries', []))}
        """
        
        full_context = user_context + "\n" + context if context else user_context
        
        # Get AI response
        try:
            response = self.gemini_service.chat_response(message, full_context)
            
            # Store conversation in database (optional)
            self._store_conversation(user_id, message, response)
            
            return {
                'success': True,
                'message': message,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }, 200
            
        except Exception as e:
            # Fallback response based on user profile
            user_name = user.get('name', 'there')
            user_skills = user.get('skills', [])
            user_goals = user.get('career_goals', [])
            
            fallback_responses = [
                f"Hello {user_name}! I'd be happy to help you with career guidance. Based on your skills in {', '.join(user_skills[:3]) if user_skills else 'various areas'}, there are several career paths that might interest you.",
                f"Hi {user_name}! Career development is a journey, and I'm here to help guide you. Your goals of {', '.join(user_goals[:2]) if user_goals else 'career advancement'} are achievable with the right planning.",
                f"Hello {user_name}! I understand you're looking for career advice. With your background in {', '.join(user_skills[:2]) if user_skills else 'your field'}, you have great potential for growth.",
                f"Hi {user_name}! Career planning is crucial for success. Based on your interests and skills, I'd recommend focusing on areas that align with your goals.",
                f"Hello {user_name}! I'm here to help you navigate your career path. What specific aspect of career development would you like to explore?"
            ]
            
            import random
            fallback_response = random.choice(fallback_responses)
            
            return {
                'success': True,
                'message': message,
                'response': fallback_response,
                'exception': str(e),
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }, 200
    
    def get(self):
        """Get conversation history"""
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload:
            return {'error': 'Invalid token'}, 401
        
        user_id = payload.get('user_id')
        
        # Get conversation history from database
        try:
            conversations = self._get_conversation_history(user_id)
            return {
                'conversations': conversations,
                'user_id': user_id
            }, 200
            
        except Exception as e:
            return {'error': f'Failed to get conversation history: {str(e)}'}, 500
    
    def _store_conversation(self, user_id, message, response):
        """Store conversation in database"""
        try:
            conversation_data = {
                'user_id': user_id,
                'message': message,
                'response': response,
                'timestamp': datetime.now()
            }
            
            # Store in conversations collection
            db.conversations.insert_one(conversation_data)
            
        except Exception as e:
            print(f"Failed to store conversation: {e}")
    
    def _get_conversation_history(self, user_id, limit=50):
        """Get conversation history for user"""
        try:
            conversations = list(db.conversations.find(
                {'user_id': user_id}
            ).sort('timestamp', -1).limit(limit))
            
            for conv in conversations:
                conv['_id'] = str(conv['_id'])
            
            return conversations
            
        except Exception as e:
            print(f"Failed to get conversation history: {e}")
            return []
    
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

