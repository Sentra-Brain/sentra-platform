// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{astro,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'sentra-primary': 'var(--sentra-primary)',
        'sentra-text': 'var(--sentra-text)',
      },
    },
  },
};
