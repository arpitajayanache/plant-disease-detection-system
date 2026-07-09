# Krishi AI: Precision Plant Disease Detection System

Krishi AI is a production-ready, AI-driven platform designed to empower farmers with real-time plant pathology diagnostics. Using a combination of Computer Vision (CNN) and Large Language Models (LLM), the system identifies diseases from leaf images and provides structured, multilingual treatment plans.

## Team Members
- **Arpita Jayanache**
- **Nikita Khandekar**
- **Priti Patil**

## Core Features
- 🌿 **CNN Disease Detection**: Custom PyTorch ResNet50 model trained on 30+ crop-disease pairs.
- 🤖 **LLM Cure Generation**: Gemini Pro integration for professional diagnostic reports.
- 🗣️ **Multilingual Voice Assistant**: Hands-free operation with support for 11 regional languages.
- 📊 **Scan History**: Persistent storage of diagnostics using MongoDB Atlas.
- 🎨 **Modern Dashboard**: Responsive React.js frontend with framer-motion animations.

## Tech Stack
- **Backend**: Flask (Python), PyTorch, PyMongo, gTTS, SpeechRecognition.
- **Frontend**: React.js, Tailwind CSS, Axios, React Dropzone.
- **Database**: MongoDB Atlas.
- **AI**: Google Gemini API, ResNet50 (Transfer Learning).

## Setup & Installation

### 1. Clone & Environment
```bash
git clone <repo-url>
cd vsproject
```
Create a `.env` file in the root:
```env
MONGODB_URI=your_mongodb_atlas_uri
GEMINI_API_KEY=your_google_gemini_key
FLASK_PORT=5000
```

### 2. Backend Setup
```bash
pip install -r requirements.txt
python run.py
```

### 3. Frontend Setup
```bash
cd leafai
npm install
npm start
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/detect` | Upload leaf image for AI diagnosis |
| `POST` | `/api/voice/listen` | Transcribe farmer's voice input |
| `POST` | `/api/voice/speak` | Read aloud treatment reports |
| `POST` | `/api/translate/cure` | Translate diagnostics to native languages |
| `GET`  | `/api/history` | Retrieve past scan results |

## Screenshots
*(Placeholder for UI screenshots: Scanner, History, Voice Assistant)*

---
© 2026 Krishi AI Team.
