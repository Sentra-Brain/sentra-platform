import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
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
    },
    server: {
      port: parseInt(env.VITE_PORT || '5173'),
      strictPort: true,
      host: true,     // required for Aspire to expose it externally
    },
  };
});
