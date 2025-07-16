
import React from 'react';

const SERVER_INFO = {
  model: 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf',
};

const TopBar: React.FC<{ onSettings: () => void }> = ({ onSettings }) => {
  // Placeholder for user state
  const user = null; // Replace with real user state
  return (
    <header className="topbar" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 1.5rem', height: 56, background: 'var(--sentra-primary)', borderBottom: '1px solid var(--sentra-primary-dark)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        <span className="app-name" style={{ fontWeight: 700, fontSize: '1.2rem', color: 'var(--sentra-accent)' }}>Sentra Brain</span>
        <span className="model-info" style={{ color: 'var(--sentra-accent-light)', fontSize: '1rem' }}>Model: {SERVER_INFO.model}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {user ? (
          <span className="user-info" style={{ color: 'var(--sentra-text)' }}>Hi, {user.name}</span>
        ) : (
          <button className="login-btn" style={{ background: 'var(--sentra-accent)', color: '#fff', border: 'none', borderRadius: 6, padding: '0.4rem 1rem', fontSize: '1rem', cursor: 'pointer' }}>Login</button>
        )}
        <button className="settings-btn" onClick={onSettings} title="Settings" style={{ background: 'none', border: 'none', color: 'var(--sentra-accent)', fontSize: '1.4rem', cursor: 'pointer' }}>
          <span role="img" aria-label="settings">⚙️</span>
        </button>
      </div>
    </header>
  );
};

export default TopBar;
