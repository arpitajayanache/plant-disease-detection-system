import speech_recognition as sr
from gtts import gTTS
import io
import os
import tempfile
import logging
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe_audio(self, audio_bytes, language='en-IN'):
        # Save bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            # Convert to wav using pydub if needed
            audio = AudioSegment.from_file(tmp_path)
            wav_path = tmp_path.replace(".webm", ".wav")
            audio.export(wav_path, format="wav")
            
            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
            
            transcript = self.recognizer.recognize_google(audio_data, language=language)
            return transcript
        except Exception as e:
            logger.error(f"Transcription Error: {e}")
            return None
        finally:
            # Cleanup
            for p in [tmp_path, tmp_path.replace(".webm", ".wav")]:
                if os.path.exists(p):
                    os.unlink(p)

    def text_to_speech(self, text, language_code='en'):
        try:
            tts = gTTS(text=text, lang=language_code, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return None

# Global instance
voice_service = VoiceService()
