import { useState, useCallback, useEffect } from 'react';

const useSpeechSynthesis = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMuted, setIsMuted] = useState(false);

  const speak = useCallback((text, lang) => {
    if (isMuted) return;

    // Cancel any existing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Map language codes to supported TTS locales
    const langMap = {
        'en': 'en-US',
        'hi': 'hi-IN',
        'mr': 'mr-IN',
        'kn': 'kn-IN',
        'te': 'te-IN',
        'ta': 'ta-IN',
        'bn': 'bn-IN',
        'gu': 'gu-IN',
        'pa': 'pa-IN',
        'fr': 'fr-FR'
    };
    
    utterance.lang = langMap[lang] || 'en-US';
    
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  }, [isMuted]);

  const cancel = useCallback(() => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, []);

  const toggleMute = useCallback(() => {
    if (!isMuted) cancel();
    setIsMuted(!isMuted);
  }, [isMuted, cancel]);

  useEffect(() => {
    return () => window.speechSynthesis.cancel();
  }, []);

  return { speak, cancel, isSpeaking, isMuted, toggleMute };
};

export default useSpeechSynthesis;
