// public/js/redirect-by-language.js

const supportedLocales = ["en", "es"];

function redirectByLanguage(defaultLang = "en", delay = 50) {
  setTimeout(() => {
    const browserLang = navigator.language?.slice(0, 2).toLowerCase();
    const finalLang = supportedLocales.includes(browserLang) ? browserLang : defaultLang;

    const currentPath = window.location.pathname;
    const isAlreadyLocalized = supportedLocales.some((lang) =>
      currentPath.startsWith(`/${lang}/`)
    );

    if (!isAlreadyLocalized) {
      window.location.replace(`/${finalLang}/`);
    }
  }, delay);
}

window.redirectByLanguage = redirectByLanguage;
