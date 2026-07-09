from flask import Blueprint, request, jsonify
from ..models.plant_model import plant_model
from ..services.llm_service import llm_service
from ..services.db_service import db_service
import os
import datetime

detect_bp = Blueprint('detect', __name__)

@detect_bp.route('/detect', methods=['POST'])
def detect_disease():
    if 'image' not in request.files:
        return jsonify({"error": "No image file"}), 400
        
    file = request.files['image']
    language = request.form.get('language', 'English')
    user_id = request.form.get('user_id', 'anonymous')
    
    try:
        image_bytes = file.read()
        
        # 1. Predict
        disease, confidence, top3 = plant_model.predict_disease(image_bytes)
        
        # 2. Get Cure from LLM
        cure_data = llm_service.get_cure(disease, language)
        
        # 3. Save to DB matching your screenshot schema
        detection_record = {
            "user_id": user_id,
            "name": request.form.get('user_name', 'System Test'),
            "email": request.form.get('user_email', 'test@example.com'),
            "photo-url": "saved_to_server", # placeholder for image path
            "disease_name": disease,
            "disease_cure": cure_data.get('description', 'Consult expert'),
            "accuracy": confidence,
            "language_used": language,
            "detected_at": datetime.datetime.utcnow()
        }
        db_service.save_detection(detection_record)
        
        return jsonify({
            "disease": disease,
            "confidence": confidence,
            "top3": top3,
            "cure": cure_data,
            "language": language
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
