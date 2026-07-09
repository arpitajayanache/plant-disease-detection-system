import React, { createContext, useState, useContext, useEffect } from 'react';

const SUPPORTED_LANGS = [
  {code:'en', name:'English', flag:'🇬🇧'},
  {code:'hi', name:'हिंदी', flag:'🇮🇳'},
  {code:'kn', name:'ಕನ್ನಡ', flag:'🇮🇳'},
  {code:'mr', name:'मराठी', flag:'🇮🇳'},
  {code:'te', name:'తెలుగు', flag:'🇮🇳'},
  {code:'ta', name:'தமிழ்', flag:'🇮🇳'}
];

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [currentLang, setCurrentLang] = useState(() => {
    return localStorage.getItem('krishi_lang') || 'en';
  });

  useEffect(() => {
    localStorage.setItem('krishi_lang', currentLang);
  }, [currentLang]);

  const changeLanguage = (code) => {
    setCurrentLang(code);
  };

  return (
    <LanguageContext.Provider value={{ currentLang, changeLanguage, SUPPORTED_LANGS }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);

export const LanguageSelector = () => {
  const { currentLang, changeLanguage, SUPPORTED_LANGS } = useLanguage();

  return (
    <div className="flex gap-2 p-2 bg-stone-50 rounded-2xl border border-stone-200">
      {SUPPORTED_LANGS.map((lang) => (
        <button
          key={lang.code}
          onClick={() => changeLanguage(lang.code)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
            currentLang === lang.code 
              ? 'bg-emerald-700 text-white shadow-md scale-105' 
              : 'bg-white text-stone-600 hover:bg-emerald-50'
          }`}
        >
          <span>{lang.flag}</span>
          <span className="hidden md:inline">{lang.name}</span>
        </button>
      ))}
    </div>
  );
};
