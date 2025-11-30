import os
import google.generativeai as genai
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        # Try different models in order of preference
        self.models = [
            'gemini-2.5-flash',
            'gemini-pro-vision'
        ]
        self.current_model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the first available model"""
        # Check if API key is available
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found, using fallback mode")
            self.current_model = None
            return
            
        genai.configure(api_key=self.api_key)
            
        for model_name in self.models:
            try:
                self.current_model = genai.GenerativeModel(model_name)
                logger.info(f"Initialized Gemini model: {model_name}")
                break
            except Exception as e:
                logger.warning(f"Failed to initialize model {model_name}: {e}")
                continue
        
        if not self.current_model:
            logger.warning("No Gemini models available, using fallback mode")
    
    def _switch_model(self):
        """Switch to the next available model"""
        current_index = self.models.index(self.current_model.model_name) if self.current_model else 0
        next_index = (current_index + 1) % len(self.models)
        
        try:
            self.current_model = genai.GenerativeModel(self.models[next_index])
            logger.info(f"Switched to Gemini model: {self.models[next_index]}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to model {self.models[next_index]}: {e}")
            return False
    
    def generate_text(self, prompt: str, max_retries: int = 3) -> str:
        """Generate text using Gemini API with fallback models"""
        if not self.current_model:
            raise Exception("No Gemini model available")
            
        for attempt in range(max_retries):
            try:
                response = self.current_model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    if not self._switch_model():
                        break
                else:
                    logger.error("All attempts failed")
                    raise e
        
        raise Exception("Failed to generate text after all retries")
    
    def get_career_recommendations(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get career recommendations based on user profile"""
        prompt = f"""
        Based on the following user profile, provide 5 career recommendations with detailed explanations:
        
        User Profile:
        - Skills: {', '.join(user_profile.get('skills', []))}
        - Interests: {', '.join(user_profile.get('interests', []))}
        - Career Goals: {', '.join(user_profile.get('career_goals', []))}
        - Education Background: {user_profile.get('education_background', {})}
        - Experience Level: {user_profile.get('experience_level', 'beginner')}
        - Preferred Industries: {', '.join(user_profile.get('preferred_industries', []))}
        
        Please provide recommendations in the following JSON format:
        [
            {{
                "career_name": "Career Name",
                "match_score": 85,
                "reason": "Why this career matches",
                "required_skills": ["skill1", "skill2"],
                "growth_potential": "high/medium/low",
                "salary_range": "range",
                "education_requirements": "requirements"
            }}
        ]
        """
        
        try:
            response = self.generate_text(prompt)
            # Parse JSON response (in a real implementation, you'd want better JSON parsing)
            return self._parse_career_recommendations(response)
        except Exception as e:
            logger.error(f"Failed to get career recommendations: {e}")
            return []
    
    def analyze_skills_gap(self, user_skills: List[str], target_career: str) -> Dict[str, Any]:
        """Analyze skills gap for a target career"""
        prompt = f"""
        Analyze the skills gap for someone with these skills: {', '.join(user_skills)}
        who wants to pursue a career in: {target_career}
        
        Please provide:
        1. Missing skills needed for this career
        2. Learning resources for each missing skill
        3. Priority level for each skill
        4. Estimated time to learn each skill
        
        Format as JSON:
        {{
            "missing_skills": [
                {{
                    "skill_name": "skill name",
                    "priority": "high/medium/low",
                    "time_to_learn": "estimated time",
                    "learning_resources": ["resource1", "resource2"]
                }}
            ],
            "existing_skills_match": ["skill1", "skill2"],
            "overall_gap_score": 75
        }}
        """
        
        try:
            response = self.generate_text(prompt)
            return self._parse_skills_gap(response)
        except Exception as e:
            logger.error(f"Failed to analyze skills gap: {e}")
            return {}
    
    def get_job_market_analysis(self, career_field: str) -> Dict[str, Any]:
        """Get job market analysis for a career field"""
        prompt = f"""
        Provide a comprehensive job market analysis for the career field: {career_field}
        
        Include:
        1. Current market trends
        2. Growth projections
        3. Salary ranges
        4. Job availability
        5. Required skills
        6. Geographic hotspots
        7. Industry insights
        
        Format as JSON:
        {{
            "market_trends": "trend description",
            "growth_rate": "percentage",
            "salary_range": "range",
            "job_availability": "high/medium/low",
            "required_skills": ["skill1", "skill2"],
            "geographic_hotspots": ["location1", "location2"],
            "industry_insights": "insights"
        }}
        """
        
        try:
            response = self.generate_text(prompt)
            return self._parse_job_market_analysis(response)
        except Exception as e:
            logger.error(f"Failed to get job market analysis: {e}")
            return {}
    
    def chat_response(self, message: str, context: str = "") -> str:
        """Generate chatbot response"""
        prompt = f"""
        You are a career counseling AI assistant. Respond to the user's question about career guidance.
        
        Context: {context}
        User Question: {message}
        
        Provide helpful, accurate, and personalized career advice. Keep responses concise but informative.
        """
        
        try:
            response = self.generate_text(prompt)
            if not response or response.strip() == "":
                raise Exception("Empty response from Gemini")
            return response
        except Exception as e:
            logger.error(f"Failed to generate chat response: {e}")
            raise e
    
    def _parse_career_recommendations(self, response: str) -> List[Dict[str, Any]]:
        """Parse career recommendations from AI response"""
        # This is a simplified parser - in production, you'd want more robust JSON parsing
        try:
            import json
            # Try to extract JSON from the response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse career recommendations: {e}")
        
        # Fallback: return empty list
        return []
    
    def _parse_skills_gap(self, response: str) -> Dict[str, Any]:
        """Parse skills gap analysis from AI response"""
        try:
            import json
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse skills gap: {e}")
        
        return {}
    
    def _parse_job_market_analysis(self, response: str) -> Dict[str, Any]:
        """Parse job market analysis from AI response"""
        try:
            import json
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse job market analysis: {e}")
        
        return {}

