from datetime import datetime
from bson import ObjectId

class CareerModel:
    def __init__(self, db):
        self.collection = db.careers
    
    def _serialize_career(self, career):
        """Convert career data to JSON-serializable format"""
        if career:
            career = career.copy()  # Create a copy to avoid modifying original
            career['_id'] = str(career['_id'])
            if 'created_at' in career and career['created_at']:
                career['created_at'] = career['created_at'].isoformat()
            if 'updated_at' in career and career['updated_at']:
                career['updated_at'] = career['updated_at'].isoformat()
        return career
    
    def _serialize_careers(self, careers):
        """Convert list of careers to JSON-serializable format"""
        return [self._serialize_career(career) for career in careers]
    
    def create_career(self, career_data):
        """Create a new career entry"""
        career_data['created_at'] = datetime.now()
        career_data['updated_at'] = datetime.now()
        
        result = self.collection.insert_one(career_data)
        return str(result.inserted_id)
    
    def get_career_by_id(self, career_id):
        """Get career by ID"""
        try:
            career = self.collection.find_one({'_id': ObjectId(career_id)})
            return self._serialize_career(career)
        except Exception as e:
            return None
    
    def get_all_careers(self, limit=50, skip=0):
        """Get all careers"""
        careers = list(self.collection.find().skip(skip).limit(limit))
        return self._serialize_careers(careers)
    
    def search_careers(self, query, limit=20):
        """Search careers by name or description"""
        careers = list(self.collection.find({
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}},
                {'required_skills': {'$regex': query, '$options': 'i'}}
            ]
        }).limit(limit))
        
        return self._serialize_careers(careers)
    
    def get_careers_by_skills(self, skills, limit=20):
        """Get careers that match given skills"""
        careers = list(self.collection.find({
            'required_skills': {'$in': skills}
        }).limit(limit))
        
        return self._serialize_careers(careers)
    
    def get_careers_by_industry(self, industry, limit=20):
        """Get careers by industry"""
        careers = list(self.collection.find({
            'industry': industry
        }).limit(limit))
        
        return self._serialize_careers(careers)
    
    def update_career(self, career_id, update_data):
        """Update career information"""
        update_data['updated_at'] = datetime.now()
        result = self.collection.update_one(
            {'_id': ObjectId(career_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_career(self, career_id):
        """Delete career"""
        result = self.collection.delete_one({'_id': ObjectId(career_id)})
        return result.deleted_count > 0
    
    def get_popular_careers(self, limit=10):
        """Get most popular careers"""
        careers = list(self.collection.find().sort('popularity', -1).limit(limit))
        return self._serialize_careers(careers)
    
    def get_emerging_careers(self, limit=10):
        """Get emerging careers"""
        careers = list(self.collection.find({
            'growth_rate': {'$gte': 10}
        }).sort('growth_rate', -1).limit(limit))
        
        return self._serialize_careers(careers)