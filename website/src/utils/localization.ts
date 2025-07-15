// src/utils/localization.ts
export const supportedLocales = ['en', 'es'];

export const defaultLocale = 'en';

export function getLocalizedPaths() {
  return supportedLocales.map(lang => ({ params: { lang } }));
}
