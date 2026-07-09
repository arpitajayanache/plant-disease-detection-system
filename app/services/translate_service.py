import google.generativeai as genai
import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {
    'en': 'English', 'hi': 'Hindi', 'kn': 'Kannada',
    'mr': 'Marathi', 'te': 'Telugu', 'ta': 'Tamil'
}

class TranslateService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def translate_text(self, text, target_language_code):
        if not self.model or target_language_code == 'en':
            return text
            
        lang_name = LANGUAGE_NAMES.get(target_language_code, 'English')
        prompt = f"Translate the following text to {lang_name}. Return ONLY the translated text:\n\n{text}"
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Translation Error: {e}")
            return text

    def translate_cure_response(self, cure_dict, target_language_code):
        """Translate entire cure JSON object to target language using Gemini."""
        if not self.model or target_language_code == 'en':
            return cure_dict
            
        lang_name = LANGUAGE_NAMES.get(target_language_code, 'English')
        prompt = f"""
        Translate the following plant disease cure information to {lang_name}.
        Keep all JSON keys in English, only translate the values.
        Maintain the same JSON structure exactly.
        Input JSON: {json.dumps(cure_dict)}
        Return only valid JSON, no extra text.
        """
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            # Cleanup markdown if present
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"JSON Translation Error: {e}")
            return cure_dict

    def detect_language_from_audio(self, transcript):
        """Detect language from transcribed text using Gemini."""
        if not self.model:
            return 'en'
            
        prompt = f"Detect the language of this text and return only the 2-letter ISO code: {transcript}"
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip().lower()
        except Exception as e:
            logger.error(f"Language Detection Error: {e}")
            return 'en'

# Global instance
translate_service = TranslateService()
