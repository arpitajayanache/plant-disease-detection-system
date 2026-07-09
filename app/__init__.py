from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'krishi-secret-2026')
    app.config['UPLOAD_FOLDER'] = 'uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints
    from .routes.detect import detect_bp
    from .routes.voice import voice_bp
    from .routes.translate import translate_bp
    from .routes.history import history_bp

    app.register_blueprint(detect_bp, url_prefix='/api')
    app.register_blueprint(voice_bp, url_prefix='/api')
    app.register_blueprint(translate_bp, url_prefix='/api')
    app.register_blueprint(history_bp, url_prefix='/api')

    return app
