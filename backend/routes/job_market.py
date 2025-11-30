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
from services.gemini_service import GeminiService
from utils.database import db

logger = logging.getLogger(__name__)

class JobMarketResource(Resource):
    def __init__(self):
        self.gemini_service = GeminiService()
        self.parser = reqparse.RequestParser()
    
    def get(self):
        """Get job market analysis"""
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload:
            return {'error': 'Invalid token'}, 401
        
        # Get career field from query params or use default
        career_field = request.args.get('career_field', 'Technology')
        user_id = request.args.get('user_id')
        
        # Check if Gemini is available before trying to use it
        if not self.gemini_service.current_model:
            # Use fallback immediately if Gemini is not available
            fallback_analysis = self._get_fallback_analysis(career_field)
            return {
                'success': True,
                'career_field': career_field,
                'analysis': fallback_analysis,
                'timestamp': datetime.now().isoformat()
            }, 200
        
        # Get AI job market analysis with timeout (only if Gemini is available)
        try:
            # Use threading with timeout to prevent blocking
            result_queue = queue.Queue()
            exception_queue = queue.Queue()
            
            def get_analysis():
                try:
                    analysis = self.gemini_service.get_job_market_analysis(career_field)
                    result_queue.put(analysis)
                except Exception as e:
                    exception_queue.put(e)
            
            thread = threading.Thread(target=get_analysis)
            thread.daemon = True
            thread.start()
            thread.join(timeout=8)  # 8 second timeout
            
            if thread.is_alive():
                logger.warning("Gemini call timed out, using fallback")
                fallback_analysis = self._get_fallback_analysis(career_field)
                return {
                    'success': True,
                    'career_field': career_field,
                    'analysis': fallback_analysis,
                    'timestamp': datetime.now().isoformat()
                }, 200
            
            if not exception_queue.empty():
                raise exception_queue.get()
            
            if result_queue.empty():
                raise Exception("No analysis received")
            
            analysis = result_queue.get()
            
            # Check if analysis is empty (Gemini failed)
            if not analysis or analysis == {}:
                raise Exception("Gemini service returned empty analysis")
            
            # Transform Gemini response to match frontend expectations
            transformed_analysis = self._transform_job_market_analysis(analysis, career_field)
            
            # Store analysis in database for caching (non-blocking)
            try:
                self._store_analysis(career_field, transformed_analysis)
            except Exception as e:
                logger.warning(f"Failed to store analysis: {e}")
            
            return {
                'success': True,
                'career_field': career_field,
                'analysis': transformed_analysis,
                'timestamp': datetime.now().isoformat()
            }, 200
            
        except Exception as e:
            logger.warning(f"Gemini analysis failed, using fallback: {e}")
            # Fallback analysis
            fallback_analysis = self._get_fallback_analysis(career_field)
            
            return {
                'success': True,
                'career_field': career_field,
                'analysis': fallback_analysis,
                'timestamp': datetime.now().isoformat()
            }, 200
    
    def _transform_job_market_analysis(self, analysis, career_field):
        """Transform Gemini job market analysis to match frontend format"""
        # Ensure overall_trends structure
        if 'overall_trends' not in analysis or not isinstance(analysis['overall_trends'], dict):
            analysis['overall_trends'] = {
                'trend': analysis.get('trend', 'Up'),
                'description': analysis.get('market_trends', analysis.get('description', f'The {career_field} industry is experiencing growth.'))
            }
        
        # Ensure average_salary is a number
        if 'average_salary' not in analysis:
            # Try to extract from salary_range if available
            salary_range = analysis.get('salary_range', '')
            if isinstance(salary_range, str) and '$' in salary_range:
                # Try to extract number
                import re
                numbers = re.findall(r'\d+', salary_range.replace(',', ''))
                if numbers:
                    analysis['average_salary'] = int(sum([int(n) for n in numbers]) / len(numbers))
                else:
                    analysis['average_salary'] = 75000
            else:
                analysis['average_salary'] = 75000
        elif isinstance(analysis['average_salary'], str):
            # Convert string to number if needed
            import re
            numbers = re.findall(r'\d+', analysis['average_salary'].replace(',', ''))
            analysis['average_salary'] = int(numbers[0]) if numbers else 75000
        
        # Ensure industry_analysis is an array
        if 'industry_analysis' not in analysis or not isinstance(analysis['industry_analysis'], list):
            analysis['industry_analysis'] = []
        
        # Ensure top_locations is an array
        if 'top_locations' not in analysis or not isinstance(analysis['top_locations'], list):
            analysis['top_locations'] = []
        
        return analysis
    
    def _get_fallback_analysis(self, career_field):
        """Get fallback job market analysis"""
        return {
            'overall_trends': {
                'trend': 'Up',
                'description': f'The {career_field} industry is experiencing strong growth with increasing demand for skilled professionals.'
            },
            'average_salary': 75000,
            'industry_analysis': [
                {
                    'name': 'Software Development',
                    'trend': 'Up',
                    'growth': '15%',
                    'key_roles': ['Software Engineer', 'Full Stack Developer', 'DevOps Engineer']
                },
                {
                    'name': 'Data Science',
                    'trend': 'Up',
                    'growth': '20%',
                    'key_roles': ['Data Scientist', 'Data Analyst', 'Machine Learning Engineer']
                },
                {
                    'name': 'Cybersecurity',
                    'trend': 'Up',
                    'growth': '25%',
                    'key_roles': ['Security Analyst', 'Penetration Tester', 'Security Architect']
                }
            ],
            'top_locations': [
                {
                    'name': 'San Francisco',
                    'job_openings': 15000,
                    'average_salary': 120000
                },
                {
                    'name': 'New York',
                    'job_openings': 12000,
                    'average_salary': 110000
                },
                {
                    'name': 'Seattle',
                    'job_openings': 8000,
                    'average_salary': 105000
                }
            ]
        }
    
    def post(self):
        """Create job market entry (admin only)"""
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload or payload.get('role') != 'admin':
            return {'error': 'Admin access required'}, 403
        
        # Parse job market data
        self.parser.add_argument('career_field', type=str, required=True, help='Career field is required')
        self.parser.add_argument('market_trends', type=str, required=True)
        self.parser.add_argument('growth_rate', type=str, required=True)
        self.parser.add_argument('salary_range', type=str, required=True)
        self.parser.add_argument('job_availability', type=str, required=True)
        self.parser.add_argument('required_skills', type=list, location='json', required=True)
        self.parser.add_argument('geographic_hotspots', type=list, location='json')
        self.parser.add_argument('industry_insights', type=str)
        
        args = self.parser.parse_args()
        
        # Add timestamp
        args['created_at'] = datetime.now()
        args['updated_at'] = datetime.now()
        
        # Create job market entry
        try:
            result = db.job_market.insert_one(args)
            job_market_id = str(result.inserted_id)
            
            # Get created entry
            entry = db.job_market.find_one({'_id': result.inserted_id})
            if entry:
                entry['_id'] = str(entry['_id'])
            
            return {
                'message': 'Job market entry created successfully',
                'entry': entry
            }, 201
            
        except Exception as e:
            return {'error': f'Failed to create job market entry: {str(e)}'}, 500
    
    def put(self, entry_id=None):
        """Update job market entry (admin only)"""
        if not entry_id:
            return {'error': 'Entry ID required'}, 400
        
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload or payload.get('role') != 'admin':
            return {'error': 'Admin access required'}, 403
        
        # Parse update data
        self.parser.add_argument('career_field', type=str)
        self.parser.add_argument('market_trends', type=str)
        self.parser.add_argument('growth_rate', type=str)
        self.parser.add_argument('salary_range', type=str)
        self.parser.add_argument('job_availability', type=str)
        self.parser.add_argument('required_skills', type=list, location='json')
        self.parser.add_argument('geographic_hotspots', type=list, location='json')
        self.parser.add_argument('industry_insights', type=str)
        
        args = self.parser.parse_args()
        
        # Remove None values
        update_data = {k: v for k, v in args.items() if v is not None}
        
        if not update_data:
            return {'error': 'No data to update'}, 400
        
        # Add update timestamp
        update_data['updated_at'] = datetime.now()
        
        # Update entry
        try:
            from bson import ObjectId
            result = db.job_market.update_one(
                {'_id': ObjectId(entry_id)},
                {'$set': update_data}
            )
            
            if result.modified_count == 0:
                return {'error': 'Entry not found'}, 404
            
            # Get updated entry
            entry = db.job_market.find_one({'_id': ObjectId(entry_id)})
            if entry:
                entry['_id'] = str(entry['_id'])
            
            return {
                'message': 'Job market entry updated successfully',
                'entry': entry
            }, 200
            
        except Exception as e:
            return {'error': f'Failed to update job market entry: {str(e)}'}, 500
    
    def delete(self, entry_id=None):
        """Delete job market entry (admin only)"""
        if not entry_id:
            return {'error': 'Entry ID required'}, 400
        
        # Verify token
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        payload = self._verify_token(token)
        if not payload or payload.get('role') != 'admin':
            return {'error': 'Admin access required'}, 403
        
        # Delete entry
        try:
            from bson import ObjectId
            result = db.job_market.delete_one({'_id': ObjectId(entry_id)})
            
            if result.deleted_count == 0:
                return {'error': 'Entry not found'}, 404
            
            return {'message': 'Job market entry deleted successfully'}, 200
            
        except Exception as e:
            return {'error': f'Failed to delete job market entry: {str(e)}'}, 500
    
    def _store_analysis(self, career_field, analysis):
        """Store analysis in database for caching"""
        try:
            analysis_data = {
                'career_field': career_field,
                'analysis': analysis,
                'timestamp': datetime.now()
            }
            
            # Store in job_market_analysis collection
            db.job_market_analysis.insert_one(analysis_data)
            
        except Exception as e:
            print(f"Failed to store analysis: {e}")
    
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

