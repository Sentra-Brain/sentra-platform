// src/i18n.ts
import en from '../locales/en.json';
import es from '../locales/es.json';

export type Locale = 'en' | 'es';
export const defaultLocale: Locale = 'en';

const translations = { en, es };

export function t(lang: Locale, key: string): string {

  const keys = key.split('.');
  let result: any = translations[lang];

  for (const k of keys) {
    result = result?.[k];
    if (result === undefined) break;
  }

  return typeof result === 'string' ? result : key;

}