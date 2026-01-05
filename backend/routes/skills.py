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
        
        # Remove system fields from user profile for analysis
        user_profile = {k: v for k, v in user.items() if k not in ['_id', 'password', 'created_at', 'updated_at', 'is_active', 'token']}
        
        user_skills = user.get('skills', [])
        career_goals = user.get('career_goals', [])
        goals_text = user.get('goals', '')
        
        # Determine target career from user profile or query params
        target_career = request.args.get('career')
        if not target_career:
            if career_goals and len(career_goals) > 0:
                target_career = career_goals[0] if isinstance(career_goals, list) else str(career_goals)
            elif goals_text:
                # Extract first meaningful career mention (simplified)
                target_career = goals_text.split('.')[0][:50] if goals_text else 'Career Development'
            else:
                target_career = 'Career Development'
        
        # Check if Gemini is available before trying to use it
        if not self.gemini_service.current_model:
            # Use fallback immediately if Gemini is not available
            return self._get_fallback_skills_analysis(user_id, user_profile, target_career)
        
        # Get AI skills gap analysis with timeout (only if Gemini is available)
        try:
            # Use threading with timeout to prevent blocking
            result_queue = queue.Queue()
            exception_queue = queue.Queue()
            
            def get_analysis():
                try:
                    gap_analysis = self.gemini_service.analyze_skills_gap(user_profile, target_career)
                    result_queue.put(gap_analysis)
                except Exception as e:
                    exception_queue.put(e)
            
            thread = threading.Thread(target=get_analysis)
            thread.daemon = True
            thread.start()
            thread.join(timeout=15)  # Increased timeout to 15 seconds for more complex analysis
            
            if thread.is_alive():
                logger.warning("Gemini call timed out, using fallback")
                return self._get_fallback_skills_analysis(user_id, user_profile, target_career)
            
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
            return self._get_fallback_skills_analysis(user_id, user_profile, target_career)
    
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
    
    def _get_fallback_skills_analysis(self, user_id, user_profile, target_career):
        """Get fallback skills gap analysis based on user profile"""
        user_skills = user_profile.get('skills', [])
        experience_level = user_profile.get('experience_level', 'beginner')
        career_goals = user_profile.get('career_goals', [])
        interests = user_profile.get('interests', [])
        
        # Generate skills based on target career and user profile
        # This is a smart fallback that adapts to user data
        career_skill_map = {
            'software developer': ['Python', 'JavaScript', 'Git', 'SQL', 'Problem Solving', 'Algorithms', 'Data Structures'],
            'data scientist': ['Python', 'R', 'SQL', 'Machine Learning', 'Statistics', 'Data Analysis', 'Pandas'],
            'web developer': ['JavaScript', 'HTML', 'CSS', 'React', 'Node.js', 'Git', 'REST APIs'],
            'mobile developer': ['Java', 'Kotlin', 'Swift', 'React Native', 'Git', 'Mobile UI/UX'],
            'devops engineer': ['Linux', 'Docker', 'Kubernetes', 'CI/CD', 'Cloud Computing', 'Scripting', 'Monitoring'],
            'ui/ux designer': ['Figma', 'Adobe XD', 'User Research', 'Prototyping', 'Design Systems', 'HTML/CSS'],
            'project manager': ['Project Management', 'Agile', 'Scrum', 'Communication', 'Leadership', 'Risk Management'],
            'business analyst': ['SQL', 'Data Analysis', 'Requirements Gathering', 'Documentation', 'Stakeholder Management'],
        }
        
        # Try to match target career to skill map (case-insensitive)
        target_lower = target_career.lower()
        required_skills = None
        
        for career_key, skills in career_skill_map.items():
            if career_key in target_lower or any(keyword in target_lower for keyword in career_key.split()):
                required_skills = skills
                break
        
        # If no match, use skills based on user interests or default
        if not required_skills:
            if interests:
                # Use generic tech skills if user has tech interests
                tech_keywords = ['technology', 'coding', 'programming', 'software', 'tech', 'computer', 'web', 'app']
                if any(keyword in ' '.join(interests).lower() for keyword in tech_keywords):
                    required_skills = ['Python', 'JavaScript', 'Git', 'Problem Solving', 'Communication']
                else:
                    required_skills = ['Communication', 'Problem Solving', 'Teamwork', 'Project Management', 'Critical Thinking']
            else:
                required_skills = ['Communication', 'Problem Solving', 'Teamwork', 'Project Management', 'Leadership']
        
        # Adjust required skills based on experience level
        if experience_level == 'beginner':
            # Focus on foundational skills
            required_skills = [s for s in required_skills if s not in ['Algorithms', 'Machine Learning', 'Kubernetes', 'CI/CD']]
        elif experience_level == 'advanced' or experience_level == 'expert':
            # Add advanced skills
            if 'Python' in required_skills:
                required_skills.extend(['System Design', 'Architecture', 'Performance Optimization'])
        
        # Remove duplicates and find missing skills
        required_skills = list(dict.fromkeys(required_skills))  # Preserve order while removing duplicates
        missing_skills = [skill for skill in required_skills if skill not in user_skills]
        
        # Generate learning recommendations
        learning_recommendations = []
        for skill in missing_skills[:5]:  # Limit to 5 recommendations
            learning_recommendations.append({
                'skill': skill,
                'description': f'Learn {skill} to advance your career in {target_career}. Essential for {experience_level} level professionals.',
                'resources': [
                    f'Online {skill} courses (Coursera, Udemy, edX)',
                    f'{skill} official documentation',
                    f'{skill} practice projects and tutorials',
                    'Join online communities and forums'
                ],
                'projects': [
                    f'Build a {skill} project',
                    f'Complete {skill} exercises and challenges',
                    f'Create a portfolio showcasing {skill}'
                ]
            })
        
        fallback_analysis = {
            'user_skills': user_skills,
            'required_skills_for_goals': required_skills,
            'skills_gap': missing_skills,
            'learning_recommendations': learning_recommendations
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

