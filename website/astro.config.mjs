// website/astro.config.mjs
// This is an Astro configuration file that sets up the site, integrates a sitemap, and config
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

import tailwindcss from '@tailwindcss/vite';


export default defineConfig({
  site: 'https://sentrabrain.com',

  integrations: [
        sitemap({
            i18n: {
                defaultLocale: 'en', // All urls that don't contain `es` or `fr` after `https://sentrabrain.com/` will be treated as default locale, i.e. `en`
                locales: {
                en: 'en-US', // The `defaultLocale` value must present in `locales` keys
                es: 'es-ES',
                fr: 'fr-CA',
                },
            },
            xslURL: '/sitemap.xsl',
            filenameBase: 'sitemap'
        }),
    ],
  vite: {
    plugins: [tailwindcss()],
  },
});