import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api
from dotenv import load_dotenv
import logging
import sys

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')

# Enable CORS
CORS(app)

# Initialize Flask-RESTful API
api = Api(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database connection
from utils.database import db

# Import routes
from routes.auth import LoginResource, RegisterResource
from routes.user import UserResource
from routes.career import CareerResource
from routes.chatbot import ChatbotResource
from routes.skills import SkillsResource
from routes.job_market import JobMarketResource
from routes.notifications import NotificationsResource
from routes.admin import AdminStatsResource, AdminUsersResource, AdminUserResource
from routes.career_planning import CareerPlanResource, CareerGoalsResource, CareerGoalResource, CareerMilestonesResource, CareerMilestoneResource

# Register API routes
api.add_resource(LoginResource, '/api/auth/login')
api.add_resource(RegisterResource, '/api/auth/register')
api.add_resource(UserResource, '/api/users/profile', '/api/users/profile/<string:user_id>')
api.add_resource(CareerResource, '/api/career/recommendations', '/api/career/recommendations/<string:user_id>')
api.add_resource(ChatbotResource, '/api/chatbot/message')
api.add_resource(SkillsResource, '/api/skills/analysis', '/api/skills/analysis/<string:user_id>')
api.add_resource(JobMarketResource, '/api/job-market/analysis')
api.add_resource(NotificationsResource, '/api/notifications', '/api/notifications/<string:user_id>')

# Admin routes
api.add_resource(AdminStatsResource, '/api/admin/stats')
api.add_resource(AdminUsersResource, '/api/admin/users')
api.add_resource(AdminUserResource, '/api/admin/users/<string:user_id>')

# Career planning routes
api.add_resource(CareerPlanResource, '/api/career/plan')
api.add_resource(CareerGoalsResource, '/api/career/goals')
api.add_resource(CareerGoalResource, '/api/career/goals/<string:goal_id>')
api.add_resource(CareerMilestonesResource, '/api/career/milestones')
api.add_resource(CareerMilestoneResource, '/api/career/milestones/<string:milestone_id>')

@app.route('/')
def home():
    return jsonify({
        'message': 'AI-Powered Career Counseling Platform API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': 'connected' if db is not None else 'disconnected',
        'timestamp': str(datetime.now())
    })

if __name__ == '__main__':
    # Create database collections if they don't exist
    if db is not None:
        collections = ['users', 'careers', 'skills', 'job_market', 'feedback', 'notifications', 'career_plans']
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
