import os
import torch
from app.models.plant_model import plant_model
from app.services.llm_service import llm_service
from app.services.db_service import db_service
from app.services.voice_service import voice_service
from app.services.translate_service import translate_service
import json
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntegrationTest")

def run_test():
    print("\n--- Krishi AI Integration Test ---")
    
    # 1. Model Loading
    try:
        print(f"1. Loading Model: {plant_model.num_classes} classes found... PASS")
    except Exception as e:
        print(f"1. Loading Model... FAIL: {e}")
        return

    # 2. Prediction Test (using a dummy zero tensor if no image provided)
    try:
        # Simulate image bytes
        dummy_img = torch.zeros((1, 3, 224, 224)).to(plant_model.device)
        with torch.no_grad():
            outputs = plant_model.model(dummy_img)
            idx = torch.argmax(outputs, dim=1).item()
            disease = plant_model.class_names[idx]
        print(f"2. Prediction: Detected '{disease}'... PASS")
    except Exception as e:
        print(f"2. Prediction... FAIL: {e}")

    # 3. Gemini Cure Fetch (Kannada)
    try:
        print("3. Fetching cure in Kannada from Gemini...")
        cure = llm_service.get_cure(disease, language="Kannada")
        if cure and 'description' in cure:
            print(f"3. Gemini Cure... PASS (Length: {len(str(cure))})")
        else:
            print("3. Gemini Cure... FAIL: Empty response")
    except Exception as e:
        print(f"3. Gemini Cure... FAIL: {e}")

    # 4. MongoDB Save
    try:
        scan_id = db_service.save_detection({
            "name": "Integration Test",
            "email": "test@krishi.ai",
            "disease_name": disease,
            "disease_cure": cure.get('description', 'Test'),
            "accuracy": 0.99,
            "language_used": "Kannada"
        })
        print(f"4. MongoDB Save: ID {scan_id}... PASS")
    except Exception as e:
        print(f"4. MongoDB Save... FAIL: {e}")

    # 5. TTS Test
    try:
        audio = voice_service.text_to_speech("ಪ್ರತಿ ಪರೀಕ್ಷೆ ಪೂರ್ಣಗೊಂಡಿದೆ", language_code="kn")
        if audio:
            print("5. TTS Conversion (Kannada)... PASS")
        else:
            print("5. TTS Conversion... FAIL")
    except Exception as e:
        print(f"5. TTS Conversion... FAIL: {e}")

    print("\n--- Integration Test Finished ---\n")

if __name__ == "__main__":
    run_test()
