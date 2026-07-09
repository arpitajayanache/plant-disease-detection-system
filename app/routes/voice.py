from flask import Blueprint, request, jsonify, send_file, Response
from ..services.voice_service import voice_service
import logging

logger = logging.getLogger(__name__)
voice_bp = Blueprint('voice', __name__)

@voice_bp.route('/voice/listen', methods=['POST'])
def voice_listen():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400
        
    audio_file = request.files['audio']
    language_speech = request.form.get('language_speech', 'en-IN')
    
    try:
        audio_bytes = audio_file.read()
        transcript = voice_service.transcribe_audio(audio_bytes, language=language_speech)
        
        if not transcript:
            return jsonify({"error": "Transcription failed"}), 400
            
        return jsonify({
            "transcript": transcript,
            "detected_language": language_speech
        })
    except Exception as e:
        logger.error(f"Listen Error: {e}")
        return jsonify({"error": str(e)}), 500

@voice_bp.route('/voice/speak', methods=['POST'])
def voice_speak():
    data = request.json
    text = data.get('text')
    language_code = data.get('language_code', 'en')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    try:
        audio_buffer = voice_service.text_to_speech(text, language_code=language_code)
        if not audio_buffer:
            return jsonify({"error": "TTS failed"}), 500
            
        return send_file(
            audio_buffer,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="speech.mp3"
        )
    except Exception as e:
        logger.error(f"Speak Error: {e}")
        return jsonify({"error": str(e)}), 500
