#!/usr/bin/env python3
"""
Database Seeder for AI Career Counseling Platform
Creates default users, careers, skills, and job market data
"""

import os
import sys
import bcrypt
import jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def get_database():
    """Connect to MongoDB and return database instance"""
    client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/career_counseling'))
    return client.career_counseling

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_default_users(db):
    """Create default users for testing"""
    print("Creating default users...")
    
    users_data = [
        {
            'name': 'Admin User',
            'email': 'admin@careercounseling.com',
            'password': hash_password('admin123'),
            'role': 'admin',
            'skills': ['Leadership', 'Management', 'Strategic Planning', 'Team Building'],
            'interests': ['Technology', 'Education', 'Career Development'],
            'experience': '10+ years in management and career counseling',
            'education': 'MBA in Business Administration',
            'goals': 'Help professionals achieve their career goals',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'name': 'John Student',
            'email': 'john.student@email.com',
            'password': hash_password('student123'),
            'role': 'student',
            'skills': ['Python', 'JavaScript', 'React', 'Problem Solving'],
            'interests': ['Software Development', 'Web Development', 'AI/ML'],
            'experience': 'Recent graduate with internship experience',
            'education': 'Bachelor of Computer Science',
            'goals': 'Become a full-stack developer',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'name': 'Sarah Professional',
            'email': 'sarah.professional@email.com',
            'password': hash_password('professional123'),
            'role': 'professional',
            'skills': ['Project Management', 'Data Analysis', 'Communication', 'Leadership'],
            'interests': ['Business Analytics', 'Management', 'Consulting'],
            'experience': '5 years in business analysis and project management',
            'education': 'Master of Business Administration',
            'goals': 'Transition to senior management role',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'name': 'Mike Career Changer',
            'email': 'mike.changer@email.com',
            'password': hash_password('changer123'),
            'role': 'career_changer',
            'skills': ['Sales', 'Customer Service', 'Communication', 'Marketing'],
            'interests': ['Digital Marketing', 'Content Creation', 'Social Media'],
            'experience': '8 years in sales and customer service',
            'education': 'Bachelor of Marketing',
            'goals': 'Transition to digital marketing career',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    ]
    
    users_collection = db.users
    for user in users_data:
        # Check if user already exists
        existing_user = users_collection.find_one({'email': user['email']})
        if not existing_user:
            users_collection.insert_one(user)
            print(f"Created user: {user['name']} ({user['email']})")
        else:
            print(f"User already exists: {user['name']} ({user['email']})")

def create_career_data(db):
    """Create sample career data"""
    print("Creating career data...")
    
    careers_data = [
        {
            'title': 'Software Engineer',
            'description': 'Design, develop, and maintain software applications and systems.',
            'industry': 'Technology',
            'experience_level': 'Mid Level',
            'salary_range': '$75k-$100k',
            'work_type': 'Full-time',
            'required_skills': ['Programming', 'Problem Solving', 'Software Development', 'Debugging', 'Version Control'],
            'preferred_skills': ['Python', 'JavaScript', 'React', 'Node.js', 'Database Design'],
            'job_responsibilities': [
                'Write clean, maintainable code',
                'Collaborate with cross-functional teams',
                'Debug and fix software issues',
                'Participate in code reviews',
                'Design software architecture'
            ],
            'growth_prospects': 'High demand with excellent growth opportunities',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'title': 'Data Scientist',
            'description': 'Analyze complex data to help organizations make informed decisions.',
            'industry': 'Technology',
            'experience_level': 'Mid Level',
            'salary_range': '$100k-$150k',
            'work_type': 'Full-time',
            'required_skills': ['Statistics', 'Machine Learning', 'Data Analysis', 'Python', 'SQL'],
            'preferred_skills': ['R', 'TensorFlow', 'Pandas', 'Scikit-learn', 'Data Visualization'],
            'job_responsibilities': [
                'Collect and analyze large datasets',
                'Build predictive models',
                'Create data visualizations',
                'Present findings to stakeholders',
                'Develop machine learning algorithms'
            ],
            'growth_prospects': 'Rapidly growing field with high demand',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'title': 'Product Manager',
            'description': 'Lead product development from conception to launch.',
            'industry': 'Technology',
            'experience_level': 'Mid Level',
            'salary_range': '$100k-$150k',
            'work_type': 'Full-time',
            'required_skills': ['Product Management', 'Strategic Planning', 'Communication', 'Leadership', 'Analytics'],
            'preferred_skills': ['Agile', 'User Research', 'Market Analysis', 'Project Management', 'Stakeholder Management'],
            'job_responsibilities': [
                'Define product strategy and roadmap',
                'Collaborate with engineering teams',
                'Conduct market research',
                'Manage product launches',
                'Analyze product performance'
            ],
            'growth_prospects': 'Strong growth potential in tech companies',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'title': 'UX Designer',
            'description': 'Design user experiences for digital products and services.',
            'industry': 'Design',
            'experience_level': 'Mid Level',
            'salary_range': '$75k-$100k',
            'work_type': 'Full-time',
            'required_skills': ['User Experience Design', 'User Interface Design', 'Prototyping', 'User Research', 'Design Thinking'],
            'preferred_skills': ['Figma', 'Sketch', 'Adobe Creative Suite', 'Usability Testing', 'Information Architecture'],
            'job_responsibilities': [
                'Create user personas and journey maps',
                'Design wireframes and prototypes',
                'Conduct user research and testing',
                'Collaborate with development teams',
                'Iterate on designs based on feedback'
            ],
            'growth_prospects': 'Growing demand for user-centered design',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'title': 'Digital Marketing Manager',
            'description': 'Develop and execute digital marketing strategies to drive business growth.',
            'industry': 'Marketing',
            'experience_level': 'Mid Level',
            'salary_range': '$60k-$90k',
            'work_type': 'Full-time',
            'required_skills': ['Digital Marketing', 'SEO', 'Social Media Marketing', 'Analytics', 'Content Marketing'],
            'preferred_skills': ['Google Analytics', 'Facebook Ads', 'Email Marketing', 'PPC', 'Marketing Automation'],
            'job_responsibilities': [
                'Develop digital marketing strategies',
                'Manage social media campaigns',
                'Optimize website for SEO',
                'Analyze marketing performance',
                'Create content marketing plans'
            ],
            'growth_prospects': 'High demand as businesses go digital',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    ]
    
    careers_collection = db.careers
    for career in careers_data:
        # Check if career already exists
        existing_career = careers_collection.find_one({'title': career['title']})
        if not existing_career:
            careers_collection.insert_one(career)
            print(f"Created career: {career['title']}")
        else:
            print(f"Career already exists: {career['title']}")

def create_skills_data(db):
    """Create sample skills data"""
    print("Creating skills data...")
    
    skills_data = [
        {
            'name': 'Python',
            'category': 'Programming Languages',
            'description': 'High-level programming language for general-purpose programming',
            'difficulty_level': 'Intermediate',
            'demand_level': 'High',
            'related_careers': ['Software Engineer', 'Data Scientist', 'Backend Developer'],
            'learning_resources': [
                'Python.org official tutorial',
                'Codecademy Python course',
                'Real Python tutorials'
            ],
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'name': 'JavaScript',
            'category': 'Programming Languages',
            'description': 'Programming language for web development and beyond',
            'difficulty_level': 'Intermediate',
            'demand_level': 'High',
            'related_careers': ['Frontend Developer', 'Full-stack Developer', 'Web Developer'],
            'learning_resources': [
                'MDN JavaScript Guide',
                'JavaScript.info',
                'FreeCodeCamp JavaScript course'
            ],
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'name': 'Project Management',
            'category': 'Soft Skills',
            'description': 'Planning, organizing, and managing resources to achieve specific goals',
            'difficulty_level': 'Intermediate',
            'demand_level': 'High',
            'related_careers': ['Project Manager', 'Product Manager', 'Team Lead'],
            'learning_resources': [
                'PMI Project Management courses',
                'Coursera Project Management specialization',
                'Agile and Scrum methodologies'
            ],
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'name': 'Data Analysis',
            'category': 'Analytics',
            'description': 'Process of inspecting, cleaning, and modeling data to discover useful information',
            'difficulty_level': 'Intermediate',
            'demand_level': 'High',
            'related_careers': ['Data Analyst', 'Data Scientist', 'Business Analyst'],
            'learning_resources': [
                'Kaggle Learn courses',
                'DataCamp data analysis track',
                'Google Analytics Academy'
            ],
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'name': 'User Experience Design',
            'category': 'Design',
            'description': 'Design process focused on creating meaningful user experiences',
            'difficulty_level': 'Intermediate',
            'demand_level': 'High',
            'related_careers': ['UX Designer', 'UI Designer', 'Product Designer'],
            'learning_resources': [
                'Nielsen Norman Group articles',
                'UX Mastery courses',
                'Interaction Design Foundation'
            ],
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    ]
    
    skills_collection = db.skills
    for skill in skills_data:
        # Check if skill already exists
        existing_skill = skills_collection.find_one({'name': skill['name']})
        if not existing_skill:
            skills_collection.insert_one(skill)
            print(f"Created skill: {skill['name']}")
        else:
            print(f"Skill already exists: {skill['name']}")

def create_job_market_data(db):
    """Create sample job market data"""
    print("Creating job market data...")
    
    job_market_data = [
        {
            'industry': 'Technology',
            'job_title': 'Software Engineer',
            'demand_trend': 'High',
            'salary_trend': 'Increasing',
            'remote_work_percentage': 75,
            'growth_rate': 15,
            'top_locations': ['San Francisco', 'Seattle', 'New York', 'Austin', 'Boston'],
            'required_skills': ['Programming', 'Problem Solving', 'Software Development'],
            'market_insights': 'High demand for software engineers across all industries',
            'future_outlook': 'Continued growth expected with AI and cloud computing',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'industry': 'Healthcare',
            'job_title': 'Data Analyst',
            'demand_trend': 'High',
            'salary_trend': 'Stable',
            'remote_work_percentage': 60,
            'growth_rate': 12,
            'top_locations': ['Boston', 'Philadelphia', 'Chicago', 'Atlanta', 'Denver'],
            'required_skills': ['Data Analysis', 'Statistics', 'Healthcare Knowledge'],
            'market_insights': 'Growing need for data-driven healthcare decisions',
            'future_outlook': 'Strong growth with digital health transformation',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        },
        {
            'industry': 'Finance',
            'job_title': 'Financial Analyst',
            'demand_trend': 'Medium',
            'salary_trend': 'Stable',
            'remote_work_percentage': 40,
            'growth_rate': 8,
            'top_locations': ['New York', 'Chicago', 'Boston', 'San Francisco', 'Charlotte'],
            'required_skills': ['Financial Analysis', 'Excel', 'Financial Modeling'],
            'market_insights': 'Steady demand with focus on fintech innovation',
            'future_outlook': 'Moderate growth with automation impact',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    ]
    
    job_market_collection = db.job_market
    for job in job_market_data:
        # Check if job market data already exists
        existing_job = job_market_collection.find_one({
            'industry': job['industry'],
            'job_title': job['job_title']
        })
        if not existing_job:
            job_market_collection.insert_one(job)
            print(f"Created job market data: {job['job_title']} in {job['industry']}")
        else:
            print(f"Job market data already exists: {job['job_title']} in {job['industry']}")

def main():
    """Main seeder function"""
    print("Starting database seeding...")
    
    try:
        # Connect to database
        db = get_database()
        print("Connected to MongoDB successfully!")
        
        # Create collections if they don't exist
        collections = ['users', 'careers', 'skills', 'job_market', 'feedback', 'notifications']
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"Created collection: {collection_name}")
        
        # Seed data
        create_default_users(db)
        create_career_data(db)
        create_skills_data(db)
        create_job_market_data(db)
        
        print("\nDatabase seeding completed successfully!")
        print("\nDefault users created:")
        print("- admin@careercounseling.com (password: admin123)")
        print("- john.student@email.com (password: student123)")
        print("- sarah.professional@email.com (password: professional123)")
        print("- mike.changer@email.com (password: changer123)")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

