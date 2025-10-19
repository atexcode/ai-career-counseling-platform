from datetime import datetime
from bson import ObjectId

class SkillsModel:
    def __init__(self, db):
        self.collection = db.skills
    
    def _serialize_skill(self, skill):
        """Convert skill data to JSON-serializable format"""
        if skill:
            skill['_id'] = str(skill['_id'])
            if 'created_at' in skill and skill['created_at']:
                skill['created_at'] = skill['created_at'].isoformat()
            if 'updated_at' in skill and skill['updated_at']:
                skill['updated_at'] = skill['updated_at'].isoformat()
        return skill
    
    def _serialize_skills(self, skills):
        """Convert list of skills to JSON-serializable format"""
        for skill in skills:
            self._serialize_skill(skill)
        return skills
    
    def create_skill(self, skill_data):
        """Create a new skill entry"""
        skill_data['created_at'] = datetime.now()
        skill_data['updated_at'] = datetime.now()
        
        result = self.collection.insert_one(skill_data)
        return str(result.inserted_id)
    
    def get_skill_by_id(self, skill_id):
        """Get skill by ID"""
        try:
            skill = self.collection.find_one({'_id': ObjectId(skill_id)})
            return self._serialize_skill(skill)
        except Exception as e:
            return None
    
    def get_all_skills(self, limit=50, skip=0):
        """Get all skills"""
        skills = list(self.collection.find().skip(skip).limit(limit))
        return self._serialize_skills(skills)
    
    def search_skills(self, query, limit=20):
        """Search skills by name or description"""
        skills = list(self.collection.find({
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}},
                {'category': {'$regex': query, '$options': 'i'}}
            ]
        }).limit(limit))
        
        return self._serialize_skills(skills)
    
    def get_skills_by_category(self, category, limit=20):
        """Get skills by category"""
        skills = list(self.collection.find({
            'category': category
        }).limit(limit))
        
        return self._serialize_skills(skills)
    
    def update_skill(self, skill_id, update_data):
        """Update skill information"""
        update_data['updated_at'] = datetime.now()
        result = self.collection.update_one(
            {'_id': ObjectId(skill_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_skill(self, skill_id):
        """Delete skill"""
        result = self.collection.delete_one({'_id': ObjectId(skill_id)})
        return result.deleted_count > 0
    
    def get_popular_skills(self, limit=10):
        """Get most popular skills"""
        skills = list(self.collection.find().sort('demand_score', -1).limit(limit))
        return self._serialize_skills(skills)
    
    def get_skills_by_difficulty(self, difficulty, limit=20):
        """Get skills by difficulty level"""
        skills = list(self.collection.find({
            'difficulty_level': difficulty
        }).limit(limit))
        
        return self._serialize_skills(skills)