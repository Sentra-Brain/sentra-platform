import './styles/base.css';
import './styles/components.css';
import './styles/theme.css';
import { createRoot } from 'react-dom/client'
import { StrictMode } from 'react'
import RootApp from './RootApp';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RootApp />
  </StrictMode>
);
