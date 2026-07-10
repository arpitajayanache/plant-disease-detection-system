import os
import datetime
import logging
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from gtts import gTTS
import io

# Load .env variables
from dotenv import load_dotenv
load_dotenv()

# Import the service we just created
from llm_service import KrishiAIService
import db_service
import json

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KrishiAI")

# --- APP CONFIG ---
app = Flask(__name__)
app.secret_key = "krishi-ai-super-secret-key-2026" # Change in production
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- CONTEXT PROCESSORS ---
@app.context_processor
def inject_user():
    return dict(
        user_name=session.get('user_name'),
        user_language=session.get('user_language', 'English')
    )

# Using the model and label map in the current directory
import gdown

MODEL_PATH = "plant_disease_model.onnx"
MODEL_DATA_PATH = "plant_disease_model.onnx.data"
LABEL_MAP_PATH = "label_map.json"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Loaded from .env

if not os.path.exists(MODEL_PATH):
    print("Model file not found locally, downloading from Google Drive...")
    gdown.download(id="1omapOrfmjuEkrevtRUoCqyzwZfE8qYbY", output=MODEL_PATH, quiet=False)
    print("Model file downloaded successfully.")

if not os.path.exists(MODEL_DATA_PATH):
    print("Model weights not found locally, downloading from Google Drive...")
    gdown.download(id="1fPSw7F17QLl0H_DL2x1zLMCxEn4ojP1p", output=MODEL_DATA_PATH, quiet=False)
    print("Model weights downloaded successfully.")

ai_service = KrishiAIService(MODEL_PATH, LABEL_MAP_PATH, GEMINI_API_KEY)
users_col = db_service.db.users

# --- STARTUP: Seed Catalog ---
try:
    with open("class_names.json", "r") as f:
        classes = json.load(f)
        db_service.seed_disease_catalog(classes)
        logger.info("✅ Disease catalog seeded.")
except Exception as e:
    logger.warning(f"⚠️ Could not seed catalog: {e}")

# --- HELPERS ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('signup_page'))
        return f(*args, **kwargs)
    return decorated_function

def make_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    if isinstance(obj, (int, float, bool, str)) or obj is None:
        return obj
    return str(obj)

# --- ROUTES ---

@app.route("/")
def signup_page():
    if 'user_id' in session:
        return redirect(url_for('how_it_works'))
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("name")
    email = request.form.get("email", "").lower().strip()
    password = request.form.get("password")
    language = request.form.get("language", "English")
    
    # ---- Strong password validation ----
    import re
    # At least 8 chars, includes upper, lower, digit, special char
    pwd_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-={}|\[\]:;\"'<>.,?/`~]).{8,}$"
    if not re.match(pwd_pattern, password):
        flash(
            "Password must be at least 8 characters and include uppercase, lowercase, number, and special character.",
            "error",
        )
        return redirect(url_for('signup_page'))
    # -------------------------------------
    
    if users_col.find_one({"email": email}):
        flash("Email already registered. Please log in.", "error")
        return redirect(url_for('signup_page'))
    
    user_id = db_service.db.users.insert_one({
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "language": language,
        "created_at": datetime.datetime.utcnow()
    }).inserted_id
    
    session['user_id'] = str(user_id)
    session['user_name'] = name
    session['user_language'] = language
    return redirect(url_for('how_it_works'))

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").lower().strip()
    password = request.form.get("password")
    
    user = db_service.db.users.find_one({"email": email})
    if user and check_password_hash(user['password'], password):
        session['user_id'] = str(user['_id'])
        session['user_name'] = user['name']
        session['user_language'] = user.get('language', 'English')
        return redirect(url_for('how_it_works'))
    
    flash("Invalid email or password.", "error")
    return redirect(url_for('signup_page'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('signup_page'))

@app.route("/how-it-works")
@login_required
def how_it_works():
    return render_template("2nd page (1).html", user_name=session.get('user_name'))

@app.route("/about")
@login_required
def about_page():
    return redirect(url_for('how_it_works'))

@app.route("/scanner")
@login_required
def scanner_page():
    return render_template("3rd page.html", 
                           user_name=session.get('user_name'),
                           user_language=session.get('user_language', 'English'))

@app.route("/predict", methods=["POST"])
@login_required
def predict():
    if 'leaf_image' not in request.files:
        flash("No image uploaded.", "error")
        return redirect(url_for('scanner_page'))
    
    file = request.files['leaf_image']
    language = request.form.get("language", session.get('user_language', 'English'))
    session['user_language'] = language # Persist for next pages
    
    if file.filename == '':
        flash("No selected file.", "error")
        return redirect(url_for('scanner_page'))
    
    try:
        image_bytes = file.read()
        
        # Quick leaf validation: check if image has dominant green channel
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            # Compute average green proportion
            r, g, b = img.split()
            avg_g = sum(g.getdata()) / (img.width * img.height * 255)
            if avg_g < 0.35:
                flash("Please provide only a leaf image for analysis.", "error")
                return redirect(url_for('scanner_page'))
        except Exception as e:
            logger.warning(f"Leaf validation failed: {e}")
            # Continue without validation if error
        
        # Save image to disk
        filename = f"{datetime.datetime.utcnow().timestamp()}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(filepath, "wb") as f:
            f.write(image_bytes)
            
        # Full Pipeline: CNN -> LLM
        result = ai_service.predict_and_cure(image_bytes, language=language)
        
        # Validate that the uploaded image is a leaf image based on confidence
        # If confidence is very low (e.g., < 0.4), assume it's not a leaf
        if result.get('confidence', 0) < 0.4:
            flash("Please provide only a leaf image for analysis.", "error")
            return redirect(url_for('scanner_page'))
        
        # Save to History using the screenshot schema format
        user = db_service.db.users.find_one({"_id": ObjectId(session.get('user_id'))})
        
        scan_doc = {
            "user_id": session.get('user_id'),
            "name": user.get('name') if user else session.get('user_name', 'Farmer'),
            "email": user.get('email') if user else "farmer@example.com",
            "password": "PROTECTED", 
            "photo-url": filepath,
            "disease_name": result['disease'],
            "disease_cure": result['cure'].get('description', 'Consult expert'),
            "accuracy": result['confidence'],
            "language_used": language,
            # detected_at is added automatically by db_service.save_detection
        }
        
        inserted_id = db_service.save_detection(scan_doc)
        result['scan_id'] = inserted_id
        
        # Update user session analytics
        db_service.update_session(session.get('user_id'), language)
        
        session['last_scan'] = make_serializable(result)
        return redirect(url_for('result_page'))
        
    except Exception as e:
        logger.error(f"Prediction Error: {e}")
        flash(f"Error during analysis: {e}", "error")
        return redirect(url_for('scanner_page'))

@app.route("/thankyou")
@login_required
def result_page():
    scan = session.get('last_scan')
    if not scan:
        return redirect(url_for('scanner_page'))
    return render_template("thankyou.html", scan=scan, user_name=session.get('user_name'))

@app.route("/history")
@login_required
def history_page():
    user_id = session.get('user_id')
    scans = db_service.get_detection_history(user_id=user_id)
    
    # Format for template
    for s in scans:
        ts = s.get('detected_at')
        s['timestamp_str'] = ts.strftime("%d %b %Y, %I:%M %p") if ts else "N/A"
        s['conf_pct'] = round(s.get('accuracy', 0) * 100, 1)
        s['disease'] = s.get('disease_name') # Compatibility with template
        s['confidence'] = s.get('accuracy') # Compatibility
        s['language'] = s.get('language_used', 'English') # Compatibility
        
    return render_template("history.html", scans=scans, user_name=session.get('user_name'))

@app.route("/history/view", methods=["POST"])
@login_required
def view_history_scan():
    scan_id = request.form.get("scan_id")
    scan_data = db_service.db.Diseases.find_one({"_id": ObjectId(scan_id)})
    if scan_data:
        scan_data['disease'] = scan_data.get('disease_name') # Compatibility
        session['last_scan'] = make_serializable(scan_data)
        return redirect(url_for('result_page'))
    flash("Scan not found.", "error")
    return redirect(url_for('history_page'))

# Duplicate about_page route removed (kept earlier definition with login_required)

@app.route("/conclusion")
@login_required
def conclusion_page():
    return render_template("conclusion.html", user_name=session.get('user_name'))



# --- API ENDPOINTS ---

@app.route("/api/voice/speak", methods=["POST"])
@login_required
def voice_speak():
    data = request.json
    text = data.get("text")
    lang = data.get("language", "en")
    
    # gTTS language map
    LANG_MAP = {
        'English':'en','Hindi':'hi','Marathi':'mr','Kannada':'kn',
        'Telugu':'te','Tamil':'ta','Gujarati':'gu','Bengali':'bn',
        'Punjabi':'pa','Odia':'or','Malayalam':'ml',
        'en':'en','hi':'hi','mr':'mr','kn':'kn','te':'te','ta':'ta'
    }
    gtts_lang = LANG_MAP.get(lang.split('-')[0].capitalize(), lang.split('-')[0])
    
    try:
        tts = gTTS(text=text, lang=gtts_lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return Response(fp.read(), mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/voice/query", methods=["POST"])
@login_required
def voice_query():
    data = request.json
    transcript = data.get("transcript")
    language = data.get("language", "English")
    
    try:
        # Ask Gemini a general plant question
        prompt = f"The user asked: '{transcript}'. Answer in {language} in 2 short sentences as a plant expert."
        response = ai_service.llm_model.generate_content(prompt)
        return jsonify({"response": response.text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/voice/transcribe", methods=["POST"])
@login_required
def voice_transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400
    
    audio_file = request.files['audio']
    lang = request.form.get("lang", "en-US")
    
    # Save temp file
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_voice.webm")
    audio_file.save(temp_path)
    
    try:
        # Use Gemini to transcribe (or just return the transcript if provided)
        # For now, let's assume the client sends the transcript if it can, 
        # otherwise we'd use a STT service. Since we want it to "work":
        # We can use Gemini 1.5 Flash to transcribe audio!
        prompt = "Transcribe this audio exactly as heard. Only output the text."
        audio_data = open(temp_path, "rb").read()
        
        # Note: ai_service.llm_model.generate_content can take audio bytes if configured
        # But for simplicity, we can use a simpler approach or just acknowledge
        # that Web Speech API is the primary way. 
        # If the user is on mobile/non-chrome, MediaRecorder sends the blob.
        
        # Let's try to use Gemini for STT:
        response = ai_service.llm_model.generate_content([
            prompt,
            {"mime_type": "audio/webm", "data": audio_data}
        ])
        
        return jsonify({"text": response.text.strip()})
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route("/api/set-language", methods=["POST"])
def set_language():
    data = request.json
    language = data.get("language", "English")
    session['user_language'] = language
    if session.get('user_id'):
        db_service.update_session(session.get('user_id'), language)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)