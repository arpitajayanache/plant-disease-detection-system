import google.generativeai as genai
import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def get_cure(self, disease_name, language='English'):
        if not self.model:
            return {"error": "Gemini API key not configured"}

        prompt = f"""
        Plant disease detected: {disease_name}
        Provide a structured response in {language} with:
        1. Disease description (2-3 sentences)
        2. Symptoms to look for
        3. Organic treatment steps (numbered list)
        4. Chemical treatment if needed
        5. Prevention tips
        Format as JSON with keys: description, symptoms, organic_treatment, chemical_treatment, prevention
        Use simple language. Return ONLY the JSON object.
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            # Basic cleanup
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            return json.loads(content)
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return {
                "description": f"Detailed report currently unavailable for {disease_name}.",
                "symptoms": [],
                "organic_treatment": [],
                "chemical_treatment": "Consult local expert.",
                "prevention": []
            }

# Global instance
llm_service = LLMService()
