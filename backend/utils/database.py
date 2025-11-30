import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_database():
    """Get MongoDB database connection"""
    try:
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        db = client.career_counseling
        return db
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None

# Global database instance
db = get_database()


