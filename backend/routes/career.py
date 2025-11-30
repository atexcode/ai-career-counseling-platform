from flask_restful import Resource, reqparse
from flask import request, jsonify
import jwt
import os
from datetime import datetime
import sys
import logging
import threading
import queue
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.career import CareerModel
from models.user import UserModel
from services.gemini_service import GeminiService
from utils.database import db

logger = logging.getLogger(__name__)

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
        
        # Check if Gemini is available before trying to use it
        if not self.gemini_service.current_model:
            # Use fallback immediately if Gemini is not available
            return self._get_fallback_recommendations(user_id, user)
        
        # Get AI recommendations with timeout (only if Gemini is available)
        try:
            # Use threading with timeout to prevent blocking
            result_queue = queue.Queue()
            exception_queue = queue.Queue()
            
            def get_recommendations():
                try:
                    recommendations = self.gemini_service.get_career_recommendations(user)
                    result_queue.put(recommendations)
                except Exception as e:
                    exception_queue.put(e)
            
            thread = threading.Thread(target=get_recommendations)
            thread.daemon = True
            thread.start()
            thread.join(timeout=8)  # 8 second timeout
            
            if thread.is_alive():
                logger.warning("Gemini call timed out, using fallback")
                return self._get_fallback_recommendations(user_id, user)
            
            if not exception_queue.empty():
                raise exception_queue.get()
            
            if result_queue.empty():
                raise Exception("No recommendations received")
            
            recommendations = result_queue.get()
            
            # Check if recommendations is empty (Gemini failed)
            if not recommendations or recommendations == []:
                raise Exception("Gemini service returned empty recommendations")
            
            # Transform Gemini response to match frontend expectations
            transformed_recommendations = self._transform_recommendations(recommendations)
            
            return {
                'success': True,
                'user_id': user_id,
                'recommendations': transformed_recommendations,
                'timestamp': datetime.now().isoformat()
            }, 200
        except Exception as e:
            logger.warning(f"Gemini recommendations failed, using fallback: {e}")
            # Fallback to basic career recommendations
            return self._get_fallback_recommendations(user_id, user)
    
    def _transform_recommendations(self, recommendations):
        """Transform Gemini recommendations to match frontend format"""
        transformed = []
        for idx, rec in enumerate(recommendations):
            transformed.append({
                'id': rec.get('id', f'gemini_{idx}'),
                'title': rec.get('career_name', rec.get('title', 'Unknown Career')),
                'description': rec.get('reason', rec.get('description', '')),
                'industry': rec.get('industry', 'Technology'),
                'experience_level': rec.get('experience_level', 'Mid Level'),
                'salary_range': rec.get('salary_range', 'Not specified'),
                'work_type': rec.get('work_type', 'Full-time'),
                'required_skills': rec.get('required_skills', []),
                'match_score': rec.get('match_score', 75),
                'growth_potential': rec.get('growth_potential', 'medium'),
                'education_requirements': rec.get('education_requirements', '')
            })
        return transformed
    
    def _get_fallback_recommendations(self, user_id, user):
        """Get fallback career recommendations"""
        careers = self.career_model.get_all_careers(limit=5)
        recommendations = []
        
        # If database has careers, use them
        if careers:
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
        else:
            # Hardcoded fallback recommendations when database is empty
            user_skills = user.get('skills', [])
            user_interests = user.get('interests', [])
            
            fallback_careers = [
                {
                    'id': 'fallback_1',
                    'title': 'Software Developer',
                    'description': 'Develop and maintain software applications. Work on creating innovative solutions using programming languages and frameworks.',
                    'industry': 'Technology',
                    'experience_level': 'Mid Level',
                    'salary_range': '$70,000 - $120,000',
                    'work_type': 'Full-time',
                    'required_skills': ['Programming', 'Problem Solving', 'Software Development'],
                    'match_score': 85
                },
                {
                    'id': 'fallback_2',
                    'title': 'Data Scientist',
                    'description': 'Analyze complex data to help organizations make data-driven decisions. Use statistical methods and machine learning algorithms.',
                    'industry': 'Technology',
                    'experience_level': 'Mid Level',
                    'salary_range': '$90,000 - $150,000',
                    'work_type': 'Full-time',
                    'required_skills': ['Data Analysis', 'Machine Learning', 'Python', 'Statistics'],
                    'match_score': 80
                },
                {
                    'id': 'fallback_3',
                    'title': 'DevOps Engineer',
                    'description': 'Bridge the gap between development and operations. Automate deployment processes and manage cloud infrastructure.',
                    'industry': 'Technology',
                    'experience_level': 'Mid Level',
                    'salary_range': '$85,000 - $140,000',
                    'work_type': 'Full-time',
                    'required_skills': ['DevOps', 'Cloud Computing', 'Automation', 'CI/CD'],
                    'match_score': 75
                },
                {
                    'id': 'fallback_4',
                    'title': 'Full Stack Developer',
                    'description': 'Work on both frontend and backend development. Build complete web applications from user interface to server logic.',
                    'industry': 'Technology',
                    'experience_level': 'Entry Level',
                    'salary_range': '$60,000 - $100,000',
                    'work_type': 'Full-time',
                    'required_skills': ['JavaScript', 'React', 'Node.js', 'Database Management'],
                    'match_score': 82
                },
                {
                    'id': 'fallback_5',
                    'title': 'Product Manager',
                    'description': 'Lead product development from conception to launch. Work with cross-functional teams to deliver products that meet user needs.',
                    'industry': 'Technology',
                    'experience_level': 'Mid Level',
                    'salary_range': '$95,000 - $160,000',
                    'work_type': 'Full-time',
                    'required_skills': ['Product Management', 'Communication', 'Strategic Thinking', 'Project Management'],
                    'match_score': 78
                }
            ]
            
            recommendations = fallback_careers
        
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
