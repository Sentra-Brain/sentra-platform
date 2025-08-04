import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@features': path.resolve(__dirname, 'src/features'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@store': path.resolve(__dirname, 'src/store'),
      '@styles': path.resolve(__dirname, 'src/styles'),
      '@shared': path.resolve(__dirname, 'src/shared'),
      '@ui': path.resolve(__dirname, 'src/ui'),
      '@layout': path.resolve(__dirname, 'src/layout'),
      '@routes': path.resolve(__dirname, 'src/routes'),
    }
  }
});
