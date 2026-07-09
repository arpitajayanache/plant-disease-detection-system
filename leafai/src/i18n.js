import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import en from './locales/en/translation.json';
import hi from './locales/hi/translation.json';
import mr from './locales/mr/translation.json';
import kn from './locales/kn/translation.json';
import te from './locales/te/translation.json';
import ta from './locales/ta/translation.json';
import bn from './locales/bn/translation.json';
import gu from './locales/gu/translation.json';
import pa from './locales/pa/translation.json';
import fr from './locales/fr/translation.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      hi: { translation: hi },
      mr: { translation: mr },
      kn: { translation: kn },
      te: { translation: te },
      ta: { translation: ta },
      bn: { translation: bn },
      gu: { translation: gu },
      pa: { translation: pa },
      fr: { translation: fr },
    },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // react already safes from xss
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });

export default i18n;
