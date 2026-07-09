from flask import Blueprint, request, jsonify, send_file
import io
from services.voice_service import VoiceService

voice_bp = Blueprint('voice', __name__)
vs = VoiceService()

@voice_bp.route("/api/voice/query", methods=["POST"])
def voice_query():
    from flask import session
    from bson import ObjectId
    from app import db # Import db from main app
    
    data = request.get_json(force=True)
    transcript = data.get("transcript")
    language = data.get("language", "English")
    
    # Try to get context from session/DB if not in request
    context = data.get("context", {})
    if not context.get("disease") and "user_id" in session:
        user_id = session["user_id"]
        if db != "MOCK":
            last_scan = db.scans.find_one({"user_id": user_id}, sort=[("scanned_at", -1)])
            if last_scan:
                context = {
                    "disease": last_scan.get("disease"),
                    "cure": last_scan.get("cure", {})
                }

    if not transcript:
        return jsonify({"error": "Missing 'transcript' field."}), 400

    response_text = vs.query_voice(transcript, context, language)
    return jsonify({"response": response_text})

@voice_bp.route("/api/voice/speak", methods=["POST"])
def voice_speak():
    data = request.get_json(force=True)
    text = data.get("text")
    language = data.get("language", "en") # e.g. 'en', 'hi', 'mr'

    if not text:
        return jsonify({"error": "No text provided"}), 400

    audio_bytes = vs.text_to_speech(text, language)
    return send_file(
        io.BytesIO(audio_bytes),
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name="speech.mp3"
    )

@voice_bp.route("/api/voice/transcribe", methods=["POST"])
def voice_transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400
    
    audio_file = request.files['audio']
    lang_code = request.form.get("lang", "en-US")
    
    transcript = vs.transcribe_audio(audio_file.read(), lang_code)
    return jsonify({"text": transcript})
