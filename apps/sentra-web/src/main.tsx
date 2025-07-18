import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/base.css';
import './styles/theme.css';
import './styles/components.css';
// ...existing code...
import RootApp from './RootApp';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RootApp />
  </StrictMode>
);
