from flask import Blueprint, request, jsonify
from services.translation_service import TranslationService

translate_bp = Blueprint('translate', __name__)

def init_translate_routes(db):
    ts = TranslationService(db)

    @translate_bp.route("/api/translate", methods=["POST"])
    def translate():
        data = request.get_json(force=True)
        text = data.get("text")
        target_lang = data.get("language", "English")
        
        if not text:
            # Check if it's a cure object
            cure = data.get("cure")
            if cure:
                translated_cure = ts.translate_cure_data(cure, target_lang)
                return jsonify({"cure": translated_cure})
            return jsonify({"error": "Missing 'text' or 'cure' field."}), 400

        translation = ts.translate(text, target_lang)
        return jsonify({"translation": translation})

    return translate_bp
