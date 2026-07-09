import { useState, useEffect, useRef, useCallback } from 'react';

const useSpeechRecognition = (lang) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError('Speech recognition not supported');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = lang === 'en' ? 'en-US' : 
                      lang === 'hi' ? 'hi-IN' : 
                      lang === 'mr' ? 'mr-IN' : 
                      lang === 'kn' ? 'kn-IN' : 
                      lang === 'te' ? 'te-IN' : 
                      lang === 'ta' ? 'ta-IN' : 
                      lang === 'bn' ? 'bn-IN' : 
                      lang === 'gu' ? 'gu-IN' : 
                      lang === 'pa' ? 'pa-IN' : 
                      lang === 'fr' ? 'fr-FR' : 'en-US';

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = (event) => setError(event.error);
    recognition.onresult = (event) => {
      const current = event.resultIndex;
      const result = event.results[current][0].transcript;
      setTranscript(result);
    };

    recognitionRef.current = recognition;
  }, [lang]);

  const startListening = useCallback(() => {
    if (recognitionRef.current) {
      setError(null);
      setTranscript('');
      try {
        recognitionRef.current.start();
      } catch (e) {
        console.error(e);
      }
    }
  }, []);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  return { isListening, transcript, error, startListening, stopListening };
};

export default useSpeechRecognition;
