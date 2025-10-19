from datetime import datetime
from bson import ObjectId

class UserModel:
    def __init__(self, db):
        self.collection = db.users
    
    def _serialize_user(self, user):
        """Convert user data to JSON-serializable format"""
        if user:
            user['_id'] = str(user['_id'])
            if 'created_at' in user and user['created_at']:
                user['created_at'] = user['created_at'].isoformat()
            if 'updated_at' in user and user['updated_at']:
                user['updated_at'] = user['updated_at'].isoformat()
        return user
    
    def _serialize_users(self, users):
        """Convert list of users to JSON-serializable format"""
        for user in users:
            self._serialize_user(user)
        return users
    
    def create_user(self, user_data):
        """Create a new user profile"""
        user_data['created_at'] = datetime.now()
        user_data['updated_at'] = datetime.now()
        user_data['is_active'] = True
        
        # Set default values
        user_data.setdefault('skills', [])
        user_data.setdefault('interests', [])
        user_data.setdefault('career_goals', [])
        user_data.setdefault('education_background', {})
        user_data.setdefault('experience_level', 'beginner')
        user_data.setdefault('preferred_industries', [])
        user_data.setdefault('experience', '')
        user_data.setdefault('education', '')
        user_data.setdefault('goals', '')
        
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            return self._serialize_user(user)
        except Exception as e:
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        user = self.collection.find_one({'email': email})
        return self._serialize_user(user)
    
    def update_user(self, user_id, update_data):
        """Update user profile"""
        update_data['updated_at'] = datetime.now()
        result = self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_user(self, user_id):
        """Delete user (soft delete)"""
        result = self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'is_active': False, 'updated_at': datetime.now()}}
        )
        return result.modified_count > 0
    
    def get_all_users(self, limit=50, skip=0):
        """Get all active users"""
        users = list(self.collection.find(
            {'is_active': True}
        ).skip(skip).limit(limit))
        
        return self._serialize_users(users)
    
    def add_skill(self, user_id, skill):
        """Add skill to user profile"""
        result = self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$addToSet': {'skills': skill}, '$set': {'updated_at': datetime.now()}}
        )
        return result.modified_count > 0
    
    def add_interest(self, user_id, interest):
        """Add interest to user profile"""
        result = self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$addToSet': {'interests': interest}, '$set': {'updated_at': datetime.now()}}
        )
        return result.modified_count > 0
    
    def add_career_goal(self, user_id, goal):
        """Add career goal to user profile"""
        result = self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$addToSet': {'career_goals': goal}, '$set': {'updated_at': datetime.now()}}
        )
        return result.modified_count > 0

