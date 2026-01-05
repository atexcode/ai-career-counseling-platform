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
    
    def analyze_skills_gap(self, user_profile: Dict[str, Any], target_career: str = None) -> Dict[str, Any]:
        """Analyze skills gap based on user profile and target career"""
        user_skills = user_profile.get('skills', [])
        career_goals = user_profile.get('career_goals', [])
        goals_text = user_profile.get('goals', '')
        experience_level = user_profile.get('experience_level', 'beginner')
        interests = user_profile.get('interests', [])
        preferred_industries = user_profile.get('preferred_industries', [])
        education = user_profile.get('education', '')
        experience = user_profile.get('experience', '')
        
        # Determine target career from user profile if not provided
        if not target_career:
            if career_goals:
                target_career = career_goals[0] if isinstance(career_goals, list) else str(career_goals)
            elif goals_text:
                # Extract career mention from goals text (simplified)
                target_career = goals_text[:100]  # Use first part of goals as context
            else:
                target_career = "general career development"
        
        prompt = f"""
        Analyze the skills gap for a user with the following profile who wants to pursue: {target_career}
        
        User Profile:
        - Current Skills: {', '.join(user_skills) if user_skills else 'None listed'}
        - Career Goals: {', '.join(career_goals) if career_goals else 'Not specified'}
        - Goals Description: {goals_text[:500] if goals_text else 'Not provided'}
        - Experience Level: {experience_level}
        - Interests: {', '.join(interests) if interests else 'Not specified'}
        - Preferred Industries: {', '.join(preferred_industries) if preferred_industries else 'Not specified'}
        - Education Background: {education[:300] if education else 'Not provided'}
        - Work Experience: {experience[:300] if experience else 'Not provided'}
        
        Based on this profile and target career "{target_career}", provide a comprehensive skills gap analysis:
        1. Identify missing skills needed for this career path
        2. Analyze which existing skills are relevant and match the target career
        3. Provide learning resources for each missing skill
        4. Assign priority levels (high/medium/low) based on career relevance
        5. Estimate time to learn each skill based on user's experience level
        
        Format as JSON:
        {{
            "missing_skills": [
                {{
                    "skill_name": "skill name",
                    "priority": "high/medium/low",
                    "time_to_learn": "estimated time (e.g., 2-3 months)",
                    "description": "brief description of why this skill is important",
                    "learning_resources": ["resource1", "resource2", "resource3"],
                    "projects": ["project idea 1", "project idea 2"]
                }}
            ],
            "existing_skills_match": ["skill1", "skill2"],
            "required_skills": ["all required skills for the career"],
            "overall_gap_score": 75
        }}
        
        Make sure the analysis is personalized to the user's experience level ({experience_level}), interests, and career goals.
        """
        
        try:
            response = self.generate_text(prompt)
            return self._parse_skills_gap(response)
        except Exception as e:
            logger.error(f"Failed to analyze skills gap: {e}")
            return {}
    
    def get_job_market_analysis(self, user_profile: Dict[str, Any] = None, career_field: str = None, 
                                 industry: str = None, location: str = None, experience_level: str = None) -> Dict[str, Any]:
        """Get job market analysis based on user profile and filters"""
        # Determine career field from user profile if not provided
        if not career_field:
            if user_profile:
                career_goals = user_profile.get('career_goals', [])
                goals_text = user_profile.get('goals', '')
                if career_goals and len(career_goals) > 0:
                    career_field = career_goals[0] if isinstance(career_goals, list) else str(career_goals)
                elif goals_text:
                    career_field = goals_text.split('.')[0][:50] if goals_text else 'Technology'
                else:
                    career_field = user_profile.get('preferred_industries', ['Technology'])[0] if user_profile.get('preferred_industries') else 'Technology'
            else:
                career_field = 'Technology'
        
        # Build context from user profile
        user_context = ""
        if user_profile:
            user_skills = user_profile.get('skills', [])
            interests = user_profile.get('interests', [])
            preferred_industries = user_profile.get('preferred_industries', [])
            user_exp_level = user_profile.get('experience_level', experience_level or 'beginner')
            
            user_context = f"""
            User Profile Context:
            - Skills: {', '.join(user_skills) if user_skills else 'Not specified'}
            - Interests: {', '.join(interests) if interests else 'Not specified'}
            - Preferred Industries: {', '.join(preferred_industries) if preferred_industries else 'Not specified'}
            - Experience Level: {user_exp_level}
            """
        
        # Build filter context
        filter_context = ""
        if industry:
            filter_context += f"- Filtered Industry: {industry}\n"
        if location:
            filter_context += f"- Filtered Location: {location}\n"
        if experience_level:
            filter_context += f"- Filtered Experience Level: {experience_level}\n"
        
        prompt = f"""
        Provide a comprehensive, personalized job market analysis based on the following:
        
        Career Field/Industry: {career_field}
        {user_context}
        {filter_context}
        
        Provide analysis that includes:
        1. Current market trends specific to this career/industry
        2. Growth projections and future outlook
        3. Salary ranges (adjusted for experience level if specified)
        4. Job availability and demand
        5. Required skills for this field
        6. Top geographic locations for opportunities{" (focus on " + location + " if provided)" if location else ""}
        7. Industry-specific insights
        
        {"Focus the analysis on: " + industry if industry else ""}
        {"Focus on location: " + location if location else ""}
        {"Adjust for experience level: " + experience_level if experience_level else ""}
        
        Format as JSON:
        {{
            "market_trends": "detailed trend description",
            "growth_rate": "percentage or growth indicator",
            "salary_range": "salary range (e.g., $60,000 - $120,000)",
            "average_salary": 85000,
            "job_availability": "high/medium/low",
            "required_skills": ["skill1", "skill2", "skill3"],
            "geographic_hotspots": [
                {{"name": "location1", "job_openings": 5000, "average_salary": 95000}},
                {{"name": "location2", "job_openings": 3000, "average_salary": 90000}}
            ],
            "industry_insights": "detailed insights about the industry",
            "industry_analysis": [
                {{
                    "name": "industry/role name",
                    "trend": "Up/Down/Stable",
                    "growth": "percentage",
                    "key_roles": ["role1", "role2"]
                }}
            ],
            "overall_trends": {{
                "trend": "Up/Down/Stable",
                "description": "comprehensive market overview"
            }}
        }}
        
        Make the analysis personalized and relevant to the user's profile and filters. Include specific data points and actionable insights.
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

