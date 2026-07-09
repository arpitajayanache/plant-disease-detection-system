import React, { useState, useRef, useEffect } from 'react';

const LANGUAGES = {
  'English': { code: 'en', speech: 'en-US' },
  'Hindi': { code: 'hi', speech: 'hi-IN' },
  'Marathi': { code: 'mr', speech: 'mr-IN' },
  'Kannada': { code: 'kn', speech: 'kn-IN' },
  'Telugu': { code: 'te', speech: 'te-IN' },
  'Tamil': { code: 'ta', speech: 'ta-IN' },
  'Gujarati': { code: 'gu', speech: 'gu-IN' },
  'Bengali': { code: 'bn', speech: 'bn-IN' },
  'Punjabi': { code: 'pa', speech: 'pa-IN' },
  'Odia': { code: 'or', speech: 'or-IN' },
  'Malayalam': { code: 'ml', speech: 'ml-IN' }
};

const VoiceAssistant = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [language, setLanguage] = useState('English');
  const [status, setStatus] = useState('Ready');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  // --- Voice Feedback ---
  const speakResponse = async (text) => {
    try {
      const response = await fetch('/api/voice/speak', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          language: LANGUAGES[language].code // Changed from language_code to language
        })
      });
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.play();
    } catch (err) {
      console.error("TTS Error:", err);
    }
  };

  // --- Recording Logic ---
  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorderRef.current = new MediaRecorder(stream);
    audioChunksRef.current = [];

    mediaRecorderRef.current.ondataavailable = (e) => {
      audioChunksRef.current.push(e.data);
    };

    mediaRecorderRef.current.onstop = async () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      sendAudioToBackend(audioBlob);
    };

    mediaRecorderRef.current.start();
    setIsRecording(true);
    setStatus('Listening...');
    startWaveform();
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setIsRecording(false);
    setStatus('Processing...');
    stopWaveform();
  };

  const sendAudioToBackend = async (blob) => {
    const formData = new FormData();
    formData.append('audio', blob);
    formData.append('lang', LANGUAGES[language].speech); // Changed from language_speech to lang

    try {
      const response = await fetch('/api/voice/transcribe', { // Changed from /api/voice/listen to /api/voice/transcribe
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (data.text) { // Changed from data.transcript to data.text
        setTranscript(data.text);
        setStatus('Analysis Complete');

        // Now ask Gemini for a query based on the transcript
        const queryRes = await fetch('/api/voice/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            transcript: data.text,
            language: language
          })
        });
        const queryData = await queryRes.json();
        const reply = queryData.response || "I couldn't get a response.";

        speakResponse(reply);
      }
    } catch (err) {
      setStatus('Error');
      console.error(err);
    }
  };

  // --- Waveform Animation ---
  const startWaveform = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#10B981';
      for (let i = 0; i < 5; i++) {
        const h = Math.random() * 20 + 5;
        ctx.fillRect(i * 12 + 10, 25 - h / 2, 8, h);
      }
      animationRef.current = requestAnimationFrame(draw);
    };
    draw();
  };

  const stopWaveform = () => {
    cancelAnimationFrame(animationRef.current);
    const ctx = canvasRef.current.getContext('2d');
    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
  };

  return (
    <div className="p-6 bg-white rounded-3xl shadow-xl border border-stone-100 max-w-md mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold text-emerald-800">Krishi Voice Assistant</h3>
        <span className={`text-[10px] font-bold uppercase px-2 py-1 rounded-full ${isRecording ? 'bg-red-100 text-red-600' : 'bg-emerald-100 text-emerald-600'}`}>
          {status}
        </span>
      </div>

      <div className="mb-6">
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="w-full p-3 rounded-xl border border-stone-200 text-sm outline-none focus:ring-2 focus:ring-emerald-500/20"
        >
          {Object.keys(LANGUAGES).map(lang => (
            <option key={lang} value={lang}>{lang}</option>
          ))}
        </select>
      </div>

      <div className="flex flex-col items-center gap-4">
        <canvas ref={canvasRef} width="80" height="50" className="mb-2" />

        <button
          onClick={isRecording ? stopRecording : startRecording}
          className={`w-20 h-20 rounded-full flex items-center justify-center shadow-lg transition-all transform active:scale-90 ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-emerald-600 hover:bg-emerald-700'}`}
        >
          <span className="material-symbols-outlined text-white text-4xl">
            {isRecording ? 'stop' : 'mic'}
          </span>
        </button>

        <p className="text-xs text-stone-400 font-medium italic">
          {isRecording ? 'Tap to stop' : 'Tap to speak'}
        </p>
      </div>

      {transcript && (
        <div className="mt-8 p-4 bg-emerald-50 rounded-2xl border border-emerald-100">
          <p className="text-[10px] font-bold text-emerald-600 uppercase mb-1">Transcript</p>
          <p className="text-sm text-stone-700 leading-relaxed italic">"{transcript}"</p>
        </div>
      )}
    </div>
  );
};

export default VoiceAssistant;
