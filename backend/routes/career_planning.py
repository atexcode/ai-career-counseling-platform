from flask_restful import Resource
from flask import request, jsonify
from utils.database import db
from datetime import datetime
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

class CareerPlanResource(Resource):
    def get(self):
        """Get user's career plan"""
        try:
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'User ID is required'
                }), 400
            
            # Get user's career plan
            plan = db.career_plans.find_one({'user_id': user_id})
            
            if not plan:
                # Create a default plan if none exists
                plan = {
                    'user_id': user_id,
                    'goals': [],
                    'milestones': [],
                    'learning_plan': [],
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                db.career_plans.insert_one(plan)
            
            # Convert ObjectId to string
            plan['_id'] = str(plan['_id'])
            if 'created_at' in plan:
                plan['created_at'] = plan['created_at'].isoformat()
            if 'updated_at' in plan:
                plan['updated_at'] = plan['updated_at'].isoformat()
            
            return jsonify({
                'success': True,
                'plan': plan
            })
            
        except Exception as e:
            logger.error(f"Error getting career plan: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to get career plan'
            }), 500

class CareerGoalsResource(Resource):
    def post(self):
        """Add a new career goal"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            goal_text = data.get('goal')
            
            if not user_id or not goal_text:
                return jsonify({
                    'success': False,
                    'error': 'User ID and goal are required'
                }), 400
            
            # Create goal
            goal = {
                'id': str(ObjectId()),
                'text': goal_text,
                'completed': False,
                'created_at': datetime.now()
            }
            
            # Add goal to user's career plan
            result = db.career_plans.update_one(
                {'user_id': user_id},
                {'$push': {'goals': goal}},
                upsert=True
            )
            
            return jsonify({
                'success': True,
                'goal_id': goal['id'],
                'message': 'Goal added successfully'
            })
            
        except Exception as e:
            logger.error(f"Error adding career goal: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to add career goal'
            }), 500

class CareerGoalResource(Resource):
    def put(self, goal_id):
        """Toggle goal completion status"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'User ID is required'
                }), 400
            
            # Find and update the specific goal
            plan = db.career_plans.find_one({'user_id': user_id})
            if not plan:
                return jsonify({
                    'success': False,
                    'error': 'Career plan not found'
                }), 404
            
            # Update goal completion status
            for goal in plan.get('goals', []):
                if goal['id'] == goal_id:
                    goal['completed'] = not goal.get('completed', False)
                    break
            
            # Update the plan
            db.career_plans.update_one(
                {'user_id': user_id},
                {'$set': {'goals': plan['goals'], 'updated_at': datetime.now()}}
            )
            
            return jsonify({
                'success': True,
                'message': 'Goal updated successfully'
            })
            
        except Exception as e:
            logger.error(f"Error updating career goal: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to update career goal'
            }), 500

class CareerMilestonesResource(Resource):
    def post(self):
        """Add a new career milestone"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'User ID is required'
                }), 400
            
            # Create milestone
            milestone = {
                'id': str(ObjectId()),
                'title': data.get('title', ''),
                'description': data.get('description', ''),
                'deadline': data.get('deadline', ''),
                'priority': data.get('priority', 'medium'),
                'completed': False,
                'created_at': datetime.now()
            }
            
            # Add milestone to user's career plan
            result = db.career_plans.update_one(
                {'user_id': user_id},
                {'$push': {'milestones': milestone}},
                upsert=True
            )
            
            return jsonify({
                'success': True,
                'milestone_id': milestone['id'],
                'message': 'Milestone added successfully'
            })
            
        except Exception as e:
            logger.error(f"Error adding career milestone: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to add career milestone'
            }), 500

class CareerMilestoneResource(Resource):
    def put(self, milestone_id):
        """Toggle milestone completion status"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'User ID is required'
                }), 400
            
            # Find and update the specific milestone
            plan = db.career_plans.find_one({'user_id': user_id})
            if not plan:
                return jsonify({
                    'success': False,
                    'error': 'Career plan not found'
                }), 404
            
            # Update milestone completion status
            for milestone in plan.get('milestones', []):
                if milestone['id'] == milestone_id:
                    milestone['completed'] = not milestone.get('completed', False)
                    break
            
            # Update the plan
            db.career_plans.update_one(
                {'user_id': user_id},
                {'$set': {'milestones': plan['milestones'], 'updated_at': datetime.now()}}
            )
            
            return jsonify({
                'success': True,
                'message': 'Milestone updated successfully'
            })
            
        except Exception as e:
            logger.error(f"Error updating career milestone: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to update career milestone'
            }), 500
