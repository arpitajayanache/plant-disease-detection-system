import os
import logging
from typing import Dict, Any
import google.generativeai as genai
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self, db=None):
        self.db = db
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set for TranslationService")

    def translate(self, text: str, target_lang: str) -> str:
        if not text or target_lang.lower() == "english":
            return text

        # Check cache
        if self.db and self.db != "MOCK":
            cached = self.db.translations.find_one({"text": text, "lang": target_lang})
            if cached:
                return cached["translation"]

        if not self.model:
            return text

        try:
            prompt = f"Translate the following text to {target_lang}. Return only the translated text and nothing else.\n\nText: {text}"
            response = self.model.generate_content(prompt)
            translation = response.text.strip()

            # Cache the result
            if self.db and self.db != "MOCK":
                self.db.translations.insert_one({
                    "text": text,
                    "lang": target_lang,
                    "translation": translation
                })

            return translation
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    def translate_cure_data(self, cure_data: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        """Translates the structured cure data (description, steps, etc.)."""
        if target_lang.lower() == "english":
            return cure_data

        translated_data = cure_data.copy()
        
        # Translate description
        translated_data["description"] = self.translate(cure_data.get("description", ""), target_lang)
        
        # Translate treatment steps
        if "treatment_steps" in cure_data:
            translated_steps = []
            for step in cure_data["treatment_steps"]:
                translated_steps.append({
                    "step_number": step.get("step_number"),
                    "title": self.translate(step.get("title", ""), target_lang),
                    "detail": self.translate(step.get("detail", ""), target_lang)
                })
            translated_data["treatment_steps"] = translated_steps

        # Translate prevention
        if "prevention" in cure_data:
            translated_data["prevention"] = [self.translate(p, target_lang) for p in cure_data["prevention"]]

        # Translate pesticides
        if "recommended_pesticides" in cure_data:
            translated_pesticides = []
            for p in cure_data["recommended_pesticides"]:
                if isinstance(p, dict):
                    translated_pesticides.append({
                        "name": self.translate(p.get("name", ""), target_lang),
                        "type": self.translate(p.get("type", ""), target_lang),
                        "dosage": self.translate(p.get("dosage", ""), target_lang),
                        "application_method": self.translate(p.get("application_method", ""), target_lang),
                        "safety_note": self.translate(p.get("safety_note", ""), target_lang),
                        "description": self.translate(p.get("description", ""), target_lang)
                    })
                else:
                    translated_pesticides.append(self.translate(p, target_lang))
            translated_data["recommended_pesticides"] = translated_pesticides

        # Translate organic alternatives
        if "organic_alternatives" in cure_data:
            translated_data["organic_alternatives"] = [self.translate(a, target_lang) for a in cure_data["organic_alternatives"]]

        return translated_data
