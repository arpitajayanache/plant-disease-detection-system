import os
import io
import logging
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from gtts import gTTS

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not set for VoiceService")

    def transcribe_audio(self, audio_bytes: bytes, language_code: str = "en-US") -> str:
        """
        Transcribes audio using Gemini's multimodal capabilities.
        """
        if not self.model:
            return ""
        
        try:
            # Gemini 1.5 can process audio bytes directly if wrapped in a parts list
            prompt = f"Transcribe this audio. The speaker is likely speaking in {language_code}."
            response = self.model.generate_content([
                prompt,
                {"mime_type": "audio/webm", "data": audio_bytes}
            ])
            return response.text.strip()
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""

    def query_voice(self, transcript: str, context: dict, language: str) -> str:
        """
        Processes voice transcript with disease context and returns a response in the user's language.
        """
        if not self.model:
            return "Voice service unavailable."

        disease_info = context.get("disease", "No disease detected yet")
        cure_info = context.get("cure", {})
        
        prompt = f"""
        You are a professional Voice-Enabled Plant Doctor. 
        Always respond in a format suitable for text-to-speech. 
        AVOID all markdown symbols like **, ##, or bullet points. 
        Use short, clear, professional sentences.

        TASK:
        The user has described these symptoms: "{transcript}"
        Current Context from Scan: {disease_info}.
        Cure from Database: {cure_info.get('description', 'N/A')}.

        RESPONSE FORMAT:
        Disease Name: [name]
        Description: [one short clear sentence]
        Cure/Treatment: [list 2-3 items separated by commas]
        Doctor Visit: [yes or no, and why]

        Language: Respond ONLY in {language}.
        """

        try:
            response = self.model.generate_content(prompt)
            # Remove any residual markdown just in case
            clean_text = response.text.replace('*', '').replace('#', '').strip()
            return clean_text
        except Exception as e:
            logger.error(f"Voice query error: {e}")
            return "I encountered an error."

    def text_to_speech(self, text: str, lang_code: str = "en") -> bytes:
        """
        Converts text to speech bytes using gTTS.
        """
        try:
            tts = gTTS(text=text, lang=lang_code)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return b""
