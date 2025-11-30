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
from models.skills import SkillsModel
from models.user import UserModel
from services.gemini_service import GeminiService
from utils.database import db

logger = logging.getLogger(__name__)

class SkillsResource(Resource):
    def __init__(self):
        self.skills_model = SkillsModel(db)
        self.user_model = UserModel(db)
        self.gemini_service = GeminiService()
        self.parser = reqparse.RequestParser()
    
    def get(self, user_id=None):
        """Get skills gap analysis or all skills"""
        # Check if user_id is provided as query parameter
        user_id = user_id or request.args.get('user_id')
        
        if user_id:
            # Get skills gap analysis for specific user
            return self._get_skills_gap_analysis(user_id)
        else:
            # Get all skills or search skills
            return self._get_all_skills()
    
    def _get_skills_gap_analysis(self, user_id):
        """Get skills gap analysis for user"""
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
        
        # Get target career from query params or use default
        target_career = request.args.get('career', 'Software Developer')
        user_skills = user.get('skills', [])
        
        # Check if Gemini is available before trying to use it
        if not self.gemini_service.current_model:
            # Use fallback immediately if Gemini is not available
            return self._get_fallback_skills_analysis(user_id, user_skills, target_career)
        
        # Get AI skills gap analysis with timeout (only if Gemini is available)
        try:
            # Use threading with timeout to prevent blocking
            result_queue = queue.Queue()
            exception_queue = queue.Queue()
            
            def get_analysis():
                try:
                    gap_analysis = self.gemini_service.analyze_skills_gap(user_skills, target_career)
                    result_queue.put(gap_analysis)
                except Exception as e:
                    exception_queue.put(e)
            
            thread = threading.Thread(target=get_analysis)
            thread.daemon = True
            thread.start()
            thread.join(timeout=8)  # 8 second timeout
            
            if thread.is_alive():
                logger.warning("Gemini call timed out, using fallback")
                return self._get_fallback_skills_analysis(user_id, user_skills, target_career)
            
            if not exception_queue.empty():
                raise exception_queue.get()
            
            if result_queue.empty():
                raise Exception("No analysis received")
            
            gap_analysis = result_queue.get()
            
            # Check if analysis is empty (Gemini failed)
            if not gap_analysis or gap_analysis == {}:
                raise Exception("Gemini service returned empty analysis")
            
            # Transform Gemini response to match frontend expectations
            transformed_analysis = self._transform_skills_analysis(gap_analysis, user_skills, target_career)
            
            return {
                'success': True,
                'user_id': user_id,
                'target_career': target_career,
                'user_skills': user_skills,
                'analysis': transformed_analysis,
                'timestamp': datetime.now().isoformat()
            }, 200
            
        except Exception as e:
            logger.warning(f"Gemini skills analysis failed, using fallback: {e}")
            # Fallback analysis
            return self._get_fallback_skills_analysis(user_id, user_skills, target_career)
    
    def _transform_skills_analysis(self, gap_analysis, user_skills, target_career):
        """Transform Gemini skills analysis to match frontend format"""
        # Extract missing skills as array of strings
        missing_skills_list = []
        if 'missing_skills' in gap_analysis:
            missing_skills_list = [skill.get('skill_name', skill.get('skill', '')) for skill in gap_analysis['missing_skills']]
        
        # Extract required skills
        required_skills = gap_analysis.get('required_skills', [])
        if 'existing_skills_match' in gap_analysis:
            # Combine existing match and missing skills to get all required
            required_skills = list(set(gap_analysis.get('existing_skills_match', []) + missing_skills_list))
        
        # Transform learning recommendations
        learning_recommendations = []
        if 'missing_skills' in gap_analysis:
            for skill_obj in gap_analysis['missing_skills'][:5]:  # Limit to 5
                learning_recommendations.append({
                    'skill': skill_obj.get('skill_name', skill_obj.get('skill', '')),
                    'description': skill_obj.get('description', f"Learn {skill_obj.get('skill_name', '')} to improve your career prospects in {target_career}"),
                    'resources': skill_obj.get('learning_resources', ['Online courses', 'Documentation', 'Practice projects', 'Tutorials']),
                    'projects': skill_obj.get('projects', [f"Build a {skill_obj.get('skill_name', '')} project", f"Practice {skill_obj.get('skill_name', '')} exercises"])
                })
        
        return {
            'user_skills': user_skills,
            'required_skills_for_goals': required_skills if required_skills else missing_skills_list + user_skills,
            'skills_gap': missing_skills_list,
            'learning_recommendations': learning_recommendations if learning_recommendations else []
        }
    
    def _get_fallback_skills_analysis(self, user_id, user_skills, target_career):
        """Get fallback skills gap analysis"""
        common_skills = ['Python', 'JavaScript', 'SQL', 'Git', 'Problem Solving', 'Communication', 'Teamwork', 'Project Management']
        missing_skills = [skill for skill in common_skills if skill not in user_skills]
        
        fallback_analysis = {
            'user_skills': user_skills,
            'required_skills_for_goals': common_skills,
            'skills_gap': missing_skills,
            'learning_recommendations': [
                {
                    'skill': skill,
                    'description': f'Learn {skill} to improve your career prospects in {target_career}',
                    'resources': ['Online courses', 'Documentation', 'Practice projects', 'Tutorials'],
                    'projects': [f'Build a {skill} project', f'Practice {skill} exercises', f'Create a {skill} portfolio']
                } for skill in missing_skills[:3]
            ]
        }
        
        return {
            'success': True,
            'user_id': user_id,
            'target_career': target_career,
            'analysis': fallback_analysis,
            'timestamp': datetime.now().isoformat()
        }, 200
    
    def _get_all_skills(self):
        """Get all skills or search skills"""
        # Check for search query
        search_query = request.args.get('search')
        category = request.args.get('category')
        
        if search_query:
            skills = self.skills_model.search_skills(search_query)
        elif category:
            skills = self.skills_model.get_skills_by_category(category)
        else:
            skills = self.skills_model.get_all_skills()
        
        return {
            'skills': skills,
            'count': len(skills)
        }, 200
    
    def post(self):
        """Create new skill entry (admin only)"""
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload or payload.get('role') != 'admin':
            return {'error': 'Admin access required'}, 403
        
        # Parse skill data
        self.parser.add_argument('name', type=str, required=True, help='Skill name is required')
        self.parser.add_argument('description', type=str, required=True, help='Description is required')
        self.parser.add_argument('category', type=str, required=True, help='Category is required')
        self.parser.add_argument('learning_resources', type=list, location='json')
        self.parser.add_argument('demand_score', type=int, default=0)
        self.parser.add_argument('difficulty_level', type=str, default='beginner')
        
        args = self.parser.parse_args()
        
        # Create skill
        skill_id = self.skills_model.create_skill(args)
        if not skill_id:
            return {'error': 'Failed to create skill'}, 500
        
        # Get created skill
        skill = self.skills_model.get_skill_by_id(skill_id)
        if not skill:
            return {'error': 'Failed to retrieve created skill'}, 500
        
        return {
            'message': 'Skill created successfully',
            'skill': skill
        }, 201
    
    def put(self, skill_id=None):
        """Update skill entry (admin only)"""
        if not skill_id:
            return {'error': 'Skill ID required'}, 400
        
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
        self.parser.add_argument('category', type=str)
        self.parser.add_argument('learning_resources', type=list, location='json')
        self.parser.add_argument('demand_score', type=int)
        self.parser.add_argument('difficulty_level', type=str)
        
        args = self.parser.parse_args()
        
        # Remove None values
        update_data = {k: v for k, v in args.items() if v is not None}
        
        if not update_data:
            return {'error': 'No data to update'}, 400
        
        # Update skill
        success = self.skills_model.update_skill(skill_id, update_data)
        if not success:
            return {'error': 'Failed to update skill'}, 500
        
        # Get updated skill
        skill = self.skills_model.get_skill_by_id(skill_id)
        if not skill:
            return {'error': 'Failed to retrieve updated skill'}, 500
        
        return {
            'message': 'Skill updated successfully',
            'skill': skill
        }, 200
    
    def delete(self, skill_id=None):
        """Delete skill entry (admin only)"""
        if not skill_id:
            return {'error': 'Skill ID required'}, 400
        
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload or payload.get('role') != 'admin':
            return {'error': 'Admin access required'}, 403
        
        # Delete skill
        success = self.skills_model.delete_skill(skill_id)
        if not success:
            return {'error': 'Failed to delete skill'}, 500
        
        return {'message': 'Skill deleted successfully'}, 200
    
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

