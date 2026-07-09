from flask import Blueprint, request, jsonify
from ..services.translate_service import translate_service
import logging

logger = logging.getLogger(__name__)
translate_bp = Blueprint('translate', __name__)

@translate_bp.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text')
    target = data.get('target_language', 'en')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    try:
        translated = translate_service.translate_text(text, target)
        return jsonify({
            'translated': translated, 
            'language': target
        })
    except Exception as e:
        logger.error(f"Translate Route Error: {e}")
        return jsonify({"error": str(e)}), 500

@translate_bp.route('/translate/cure', methods=['POST'])
def translate_cure():
    data = request.json
    cure_dict = data.get('cure')
    target = data.get('target_language', 'en')
    
    if not cure_dict:
        return jsonify({"error": "No cure data provided"}), 400
        
    try:
        translated_cure = translate_service.translate_cure_response(cure_dict, target)
        return jsonify(translated_cure)
    except Exception as e:
        logger.error(f"Translate Cure Route Error: {e}")
        return jsonify({"error": str(e)}), 500
