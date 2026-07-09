import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import useSpeechRecognition from '../../hooks/useSpeechRecognition';
import useSpeechSynthesis from '../../hooks/useSpeechSynthesis';

const API_BASE = "http://localhost:5000/api";

const VoiceAssistant = ({ context, navigate }) => {
  const { t, i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [chat, setChat] = useState([]); // [{ type: 'user'|'bot', text: string }]
  const { isListening, transcript, error, startListening, stopListening } = useSpeechRecognition(i18n.language);
  const { speak, cancel, isSpeaking, isMuted, toggleMute } = useSpeechSynthesis();
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chat]);

  useEffect(() => {
    if (transcript) {
      handleQuery(transcript);
    }
  }, [transcript]);

  const handleQuery = async (text) => {
    setChat(prev => [...prev, { type: 'user', text }]);
    
    try {
      const response = await fetch(`${API_BASE}/voice/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transcript: text,
          context: context,
          language: i18n.language
        })
      });
      
      const data = await response.json();
      if (data.response) {
        setChat(prev => [...prev, { type: 'bot', text: data.response }]);
        speak(data.response, i18n.language);
        processIntent(text, data.response);
      }
    } catch (err) {
      console.error("Voice API Error:", err);
      const fallback = "I'm sorry, I couldn't reach my brain. Please try again.";
      setChat(prev => [...prev, { type: 'bot', text: fallback }]);
    }
  };

  const processIntent = (userText, botText) => {
    const text = userText.toLowerCase();
    if (text.includes('home') || text.includes('dashboard')) navigate('#/how-it-works');
    if (text.includes('scan')) navigate('#/scanner');
    if (text.includes('help')) setIsOpen(true);
  };

  const toggleAssistant = () => {
    if (isOpen) {
      stopListening();
      cancel();
    }
    setIsOpen(!isOpen);
  };

  return (
    <div className={`voice-assistant-wrapper ${isOpen ? 'open' : ''}`}>
      {isOpen && (
        <div className="voice-chat-window">
          <div className="voice-header">
            <h3>🎙️ {t('voice.title')}</h3>
            <div className="voice-header-actions">
              <button onClick={toggleMute} className={`icon-btn ${isMuted ? 'muted' : ''}`} title="Mute">
                {isMuted ? '🔇' : '🔊'}
              </button>
              <button onClick={() => setIsOpen(false)} className="icon-btn">✕</button>
            </div>
          </div>

          <div className="voice-messages">
            <div className="msg bot-msg">{t('voice.ready')}</div>
            {chat.map((msg, i) => (
              <div key={i} className={`msg ${msg.type}-msg animate-pop`}>
                {msg.text}
              </div>
            ))}
            {isListening && (
              <div className="msg user-msg listening-indicator">
                <span>.</span><span>.</span><span>.</span>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="voice-footer">
            <div className="voice-hints">
                <strong>{t('voice.try')}</strong> "{t('voice.cmd_scan')}", "{t('voice.cmd_home')}"
            </div>
            <button 
              className={`mic-button ${isListening ? 'listening' : ''}`} 
              onClick={isListening ? stopListening : startListening}
            >
              {isListening ? (
                <div className="pulse-rings">
                  <div className="ring" />
                  <div className="ring" />
                </div>
              ) : null}
              <span className="mic-icon">🎤</span>
            </button>
          </div>
        </div>
      )}

      <button 
        className={`floating-mic-btn ${isListening ? 'active-pulse' : ''} ${isOpen ? 'hidden' : ''}`}
        onClick={toggleAssistant}
        aria-label="Open Voice Assistant"
      >
        <span className="mic-icon">🎤</span>
        {isListening && <div className="mini-pulse" />}
      </button>
    </div>
  );
};

export default VoiceAssistant;
