from flask_restful import Resource, reqparse
from flask import request, jsonify
import jwt
import os
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.career import CareerModel
from models.user import UserModel
from services.gemini_service import GeminiService
from utils.database import db

class CareerResource(Resource):
    def __init__(self):
        self.career_model = CareerModel(db)
        self.user_model = UserModel(db)
        self.gemini_service = GeminiService()
        self.parser = reqparse.RequestParser()
    
    def get(self, user_id=None):
        """Get career recommendations"""
        # Check if user_id is provided as query parameter
        user_id = user_id or request.args.get('user_id')
        
        if user_id:
            # Get personalized recommendations for specific user
            return self._get_user_recommendations(user_id)
        else:
            # Get all careers or search careers
            return self._get_all_careers()
    
    def _get_user_recommendations(self, user_id):
        """Get personalized career recommendations for user"""
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
        
        # Get user profile
        user = self.user_model.get_user_by_id(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        
        # Get AI recommendations
        try:
            recommendations = self.gemini_service.get_career_recommendations(user)
            
            # Check if recommendations is empty (Gemini failed)
            if not recommendations or recommendations == []:
                raise Exception("Gemini service returned empty recommendations")
            
            return {
                'success': True,
                'user_id': user_id,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }, 200
        except Exception as e:
            # Fallback to basic career recommendations
            careers = self.career_model.get_all_careers(limit=5)
            recommendations = []
            for career in careers:
                recommendations.append({
                    'id': career['_id'],
                    'title': career.get('title', career.get('name', 'Unknown')),
                    'description': career.get('description', ''),
                    'industry': career.get('industry', ''),
                    'experience_level': career.get('experience_level', ''),
                    'salary_range': career.get('salary_range', ''),
                    'work_type': career.get('work_type', ''),
                    'required_skills': career.get('required_skills', []),
                    'match_score': 75  # Default match score
                })
            
            return {
                'success': True,
                'user_id': user_id,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }, 200
    
    def _get_all_careers(self):
        """Get all careers or search careers"""
        # Check for search query
        search_query = request.args.get('search')
        industry = request.args.get('industry')
        skills = request.args.get('skills')
        
        if search_query:
            careers = self.career_model.search_careers(search_query)
        elif industry:
            careers = self.career_model.get_careers_by_industry(industry)
        elif skills:
            skills_list = skills.split(',')
            careers = self.career_model.get_careers_by_skills(skills_list)
        else:
            careers = self.career_model.get_all_careers()
        
        return {
            'success': True,
            'careers': careers,
            'count': len(careers)
        }, 200
    
    def post(self):
        """Create new career entry (admin only)"""
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload or payload.get('role') != 'admin':
            return {'error': 'Admin access required'}, 403
        
        # Parse career data
        self.parser.add_argument('name', type=str, required=True, help='Career name is required')
        self.parser.add_argument('description', type=str, required=True, help='Description is required')
        self.parser.add_argument('required_skills', type=list, location='json', required=True)
        self.parser.add_argument('industry', type=str, required=True)
        self.parser.add_argument('salary_range', type=str)
        self.parser.add_argument('education_requirements', type=str)
        self.parser.add_argument('growth_rate', type=float, default=0)
        self.parser.add_argument('popularity', type=int, default=0)
        
        args = self.parser.parse_args()
        
        # Create career
        career_id = self.career_model.create_career(args)
        if not career_id:
            return {'error': 'Failed to create career'}, 500
        
        # Get created career
        career = self.career_model.get_career_by_id(career_id)
        if not career:
            return {'error': 'Failed to retrieve created career'}, 500
        
        return {
            'message': 'Career created successfully',
            'career': career
        }, 201
    
    def put(self, career_id=None):
        """Update career entry (admin only)"""
        if not career_id:
            return {'error': 'Career ID required'}, 400
        
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload or payload.get('role') != 'admin':
            return {'error': 'Admin access required'}, 403
        
        # Parse update data
        self.parser.add_argument('name', type=str)
        self.parser.add_argument('description', type=str)
        self.parser.add_argument('required_skills', type=list, location='json')
        self.parser.add_argument('industry', type=str)
        self.parser.add_argument('salary_range', type=str)
        self.parser.add_argument('education_requirements', type=str)
        self.parser.add_argument('growth_rate', type=float)
        self.parser.add_argument('popularity', type=int)
        
        args = self.parser.parse_args()
        
        # Remove None values
        update_data = {k: v for k, v in args.items() if v is not None}
        
        if not update_data:
            return {'error': 'No data to update'}, 400
        
        # Update career
        success = self.career_model.update_career(career_id, update_data)
        if not success:
            return {'error': 'Failed to update career'}, 500
        
        # Get updated career
        career = self.career_model.get_career_by_id(career_id)
        if not career:
            return {'error': 'Failed to retrieve updated career'}, 500
        
        return {
            'message': 'Career updated successfully',
            'career': career
        }, 200
    
    def delete(self, career_id=None):
        """Delete career entry (admin only)"""
        if not career_id:
            return {'error': 'Career ID required'}, 400
        
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload or payload.get('role') != 'admin':
            return {'error': 'Admin access required'}, 403
        
        # Delete career
        success = self.career_model.delete_career(career_id)
        if not success:
            return {'error': 'Failed to delete career'}, 500
        
        return {'message': 'Career deleted successfully'}, 200
    
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
