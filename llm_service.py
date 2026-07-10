import os
import io
import json
import onnxruntime as ort
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings('ignore', category=FutureWarning, module='google.generativeai')
import google.genai as genai
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
IMG_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

class KrishiAIService:
    def __init__(self, model_path, label_map_path, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        # Load Labels
        with open(label_map_path, 'r') as f:
            self.label_map = json.load(f)
        self.class_names = [self.label_map[str(i)] for i in range(len(self.label_map))]
        self.num_classes = len(self.class_names)
        
        # Load ONNX model
        self.session = ort.InferenceSession(model_path)
        logger.info(f"ONNX model loaded from {model_path}")
        
        # Initialize Gemini client using google.genai SDK
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Google GenAI client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client: {e}")
                self.client = None
        else:
            self.client = None
            logger.warning("GEMINI_API_KEY not found. LLM services will be disabled.")
        # Backward compatibility: expose client as llm_model attribute
        self.llm_model = self.client

    def predict(self, image_bytes):
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Preprocess: resize, normalize, reorder to CHW, add batch dim
        img_resized = img.resize((IMG_SIZE, IMG_SIZE))
        arr = np.array(img_resized).astype(np.float32) / 255.0
        mean = np.array(IMAGENET_MEAN)
        std = np.array(IMAGENET_STD)
        arr = (arr - mean) / std
        arr = arr.transpose(2, 0, 1)
        input_array = np.expand_dims(arr, 0).astype(np.float32)

        # Run inference
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: input_array})[0][0]

        # Softmax (ONNX gives raw logits, so apply softmax manually)
        exp_scores = np.exp(outputs - np.max(outputs))
        probs = exp_scores / exp_scores.sum()

        # Get Top 3
        top_idxs = np.argsort(probs)[::-1][:3]

        predictions = []
        for idx in top_idxs:
            predictions.append({
                "class": self.class_names[int(idx)],
                "confidence": float(probs[idx])
            })

        return predictions[0]["class"], predictions[0]["confidence"], predictions

    def get_cure_report(self, disease_name, language="English", image_bytes=None):
        if not self.client:
            return {"error": "LLM not configured"}
            
        prompt = f"""
        You are Krishi AI, an expert agricultural pathologist.
        The CNN model thinks this plant has: {disease_name}.
        
        TASK:
        1. Look at the attached image (if provided).
        2. Verify if the diagnosis is correct. If you see a different disease, correct it.
        3. Generate a detailed management report in {language}.
        
        Return the result EXACTLY as a JSON object with these keys:
        - disease_name: The verified name of the disease in {language}
        - scientific_name: Latin name
        - description: 2-3 sentence description
        - severity: High/Medium/Low
        - treatment_steps: List of objects with 'step_number', 'title', 'detail' (each 'detail' MUST have a 2-3 sentence/line description explaining exactly how to execute the step)
        - prevention: List of 3-5 tips (each tip MUST have a 2-3 sentence/line description explaining the preventive action and why it helps)
        - recommended_pesticides: List of objects with 'name', 'type', 'dosage', 'application_method', 'safety_note', 'description' (each 'description' MUST have a 2-3 sentence/line detailed description of why it is recommended and how it helps)
        - organic_alternatives: List of 2-3 organic remedies, formatted as strings 'Name: 2-3 sentence/line description' (e.g. 'Neem Oil: Spray a 1% dilution on leaves...')
        - emergency_tip: One crucial thing to do right now
        
        Use simple, farmer-friendly language. Use native script for {language}.
        Return ONLY the JSON object.
        """
        
        try:
            content_parts = [prompt]
            if image_bytes:
                # Add image to the request
                img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                content_parts.append(img)
                
            if not self.client:
                logger.error("GenAI client not available; cannot generate cure report.")
                return {"error": "LLM not configured"}
            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=content_parts
            )
            raw_content = response.text.strip()
            # Log raw LLM response for debugging
            logger.debug(f"LLM raw response: {raw_content}")
            # Try to extract the JSON object from the response using regex
            json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    cure_data = json.loads(json_str)
                    # ---- concise summaries ----
                    steps = cure_data.get('treatment_steps', [])[:2]
                    cure_data['treatment_summary'] = '; '.join(
                        f"{s.get('title','')}: {s.get('detail','') }".strip() for s in steps if isinstance(s, dict)
                    )
                    cure_data['prevention_summary'] = ', '.join(cure_data.get('prevention', []))
                    return cure_data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error after extraction: {e}")
            # Fallback handling if extraction fails
            logger.warning("Failed to parse cure report JSON; returning fallback data.")
            cure = {
                "disease_name": disease_name,
                "description": f"Detailed report currently unavailable for {disease_name}.",
                "treatment_steps": [
                    {
                        "step_number": 1,
                        "title": "Remove affected leaves",
                        "detail": "Carefully prune away any visibly diseased foliage using sterilized tools to reduce physical spread. Dispose of the removed leaves immediately and far away from the crop area. Sanitize your hands and equipment before handling healthy crops."
                    },
                    {
                        "step_number": 2,
                        "title": "Apply fungicide",
                        "detail": "Select an appropriate copper-based fungicide and spray it weekly for 3 consecutive weeks. Ensure coverage of both upper and lower leaf surfaces during calm, dry weather. Follow all manufacturer instructions regarding dilution rates and safety equipment."
                    }
                ],
                "prevention": [
                    "Rotate crops: Periodically change your planting locations to break the soilborne disease cycle. Avoid planting susceptible crops in the same area for at least three seasons. This simple agricultural practice significantly lowers pathogen build-up in the soil.",
                    "Avoid overhead watering: Use drip irrigation or water at the soil level to keep the plant foliage dry. Wet leaves create an ideal damp environment that promotes rapid fungal spore germination. Ensuring dry leaves is a highly effective way to prevent outbreaks.",
                    "Use certified disease-free seeds: Always start with healthy, high-quality seeds from verified certified suppliers. Clean starting material prevents introducing pathogens to your field at the early growth stage. This is the first line of defense in successful disease management."
                ],
                "recommended_pesticides": [
                    {
                        "name": "Copper fungicide",
                        "type": "Systemic",
                        "dosage": "2 ml/L",
                        "application_method": "Spray",
                        "safety_note": "Wear gloves",
                        "description": "A copper-based systemic fungicide that protects leaves from fungal infections and reduces disease spread. Apply as a foliar spray covering both sides of leaves. Repeat application every 7-14 days depending on weather."
                    }
                ],
                "organic_alternatives": [
                    "Neem oil: Spray a 1% dilution of cold-pressed neem oil on leaves every 7-10 days as a preventative. It forms a protective barrier that prevents fungal spores from attaching and germinating. This organic remedy is completely safe for beneficial insects.",
                    "Compost tea: Apply actively aerated compost tea as a foliar spray or soil drench. It introduces beneficial microbes that compete with pathogens and boost the plant's immune system. This natural remedy enhances overall soil health and resistance."
                ],
                "emergency_tip": "Isolate the infected plant immediately.",
                "severity": "Medium",
                "scientific_name": "",
                "symptoms": []
            }
            # concise summaries for fallback data
            steps = cure.get('treatment_steps', [])[:2]
            cure['treatment_summary'] = '; '.join(
                f"{s.get('title','')}: {s.get('detail','') }".strip() for s in steps if isinstance(s, dict)
            )
            cure['prevention_summary'] = ', '.join(cure.get('prevention', []))
            return cure
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            cure = {
                "disease_name": disease_name,
                "description": f"Detailed report currently unavailable for {disease_name}.",
                "treatment_steps": [
                    {
                        "step_number": 1,
                        "title": "Remove affected leaves",
                        "detail": "Carefully prune away any visibly diseased foliage using sterilized tools to reduce physical spread. Dispose of the removed leaves immediately and far away from the crop area. Sanitize your hands and equipment before handling healthy crops."
                    },
                    {
                        "step_number": 2,
                        "title": "Apply fungicide",
                        "detail": "Select an appropriate copper-based fungicide and spray it weekly for 3 consecutive weeks. Ensure coverage of both upper and lower leaf surfaces during calm, dry weather. Follow all manufacturer instructions regarding dilution rates and safety equipment."
                    }
                ],
                "prevention": [
                    "Rotate crops: Periodically change your planting locations to break the soilborne disease cycle. Avoid planting susceptible crops in the same area for at least three seasons. This simple agricultural practice significantly lowers pathogen build-up in the soil.",
                    "Avoid overhead watering: Use drip irrigation or water at the soil level to keep the plant foliage dry. Wet leaves create an ideal damp environment that promotes rapid fungal spore germination. Ensuring dry leaves is a highly effective way to prevent outbreaks.",
                    "Use certified disease-free seeds: Always start with healthy, high-quality seeds from verified certified suppliers. Clean starting material prevents introducing pathogens to your field at the early growth stage. This is the first line of defense in successful disease management."
                ],
                "recommended_pesticides": [
                    {
                        "name": "Copper fungicide",
                        "type": "Systemic",
                        "dosage": "2 ml/L",
                        "application_method": "Spray",
                        "safety_note": "Wear gloves",
                        "description": "A copper-based systemic fungicide that protects leaves from fungal infections and reduces disease spread. Apply as a foliar spray covering both sides of leaves. Repeat application every 7-14 days depending on weather."
                    }
                ],
                "organic_alternatives": [
                    "Neem oil: Spray a 1% dilution of cold-pressed neem oil on leaves every 7-10 days as a preventative. It forms a protective barrier that prevents fungal spores from attaching and germinating. This organic remedy is completely safe for beneficial insects.",
                    "Compost tea: Apply actively aerated compost tea as a foliar spray or soil drench. It introduces beneficial microbes that compete with pathogens and boost the plant's immune system. This natural remedy enhances overall soil health and resistance."
                ],
                "emergency_tip": "Isolate the infected plant immediately.",
                "severity": "Medium",
                "scientific_name": "",
                "symptoms": []
            }
            # concise summaries for fallback data
            steps = cure.get('treatment_steps', [])[:2]
            cure['treatment_summary'] = '; '.join(
                f"{s.get('title','')}: {s.get('detail','') }".strip() for s in steps if isinstance(s, dict)
            )
            cure['prevention_summary'] = ', '.join(cure.get('prevention', []))
            return cure

    def predict_and_cure(self, image_bytes, language="English"):
        disease, confidence, top3 = self.predict(image_bytes)
        
        # Use Gemini Vision for ALL cases where confidence is low (< 85%) 
        # or if it's a specific crop that looks similar (Potato vs Tomato)
        low_confidence = confidence < 0.85
        
        # Refined healthy check based on class name
        diseased_keywords = ["scab", "rust", "blight", "spot", "virus", "mildew", "rot", "mold", "mites", "yellow"]
        is_healthy = not any(kw in disease.lower() for kw in diseased_keywords)
        
        if is_healthy and confidence > 0.9 and not low_confidence:
            cure = {
                "disease_name": "Healthy Leaf",
                "description": f"The {disease} appears to be healthy. Continue regular care and monitoring.",
                "treatment_steps": [],
                "prevention": ["Maintain proper irrigation", "Ensure good soil nutrition", "Monitor for pests weekly"],
                "recommended_pesticides": [],
                "organic_alternatives": ["Neem oil (as preventative)", "Compost tea"],
                "emergency_tip": "No emergency action needed. Your plant is doing well!"
            }
        else:
            # Use Gemini Vision to verify and generate cure
            # This will fix the "Potato vs Tomato" issue because Gemini will see the actual leaf shape
            cure = self.get_cure_report(disease, language, image_bytes)
        
        # Ensure all expected fields exist with sensible defaults
        _default_cure = {
            "treatment_steps": [],
            "prevention": [],
            "recommended_pesticides": [],
            "organic_alternatives": [],
            "emergency_tip": "",
            "severity": "",
            "scientific_name": "",
            "symptoms": [],
            "description": "",
            "disease_name": disease,
        }
        for _k, _v in _default_cure.items():
            cure.setdefault(_k, _v)
        
        # If Gemini corrected the disease name, update it
        if "disease_name" in cure and cure["disease_name"] != disease:
            logger.info(f"Gemini corrected {disease} to {cure['disease_name']}")
            disease = cure['disease_name']
        
        return {
            "disease": disease,
            "confidence": confidence,
            "top3": top3,
            "is_healthy": is_healthy,
            "model_used": "CNN + Gemini Vision (Verified)",
            "language": language,
            "cure": cure
        }