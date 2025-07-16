
import React from 'react';

const TopBar: React.FC<{ onSettings: () => void }> = ({ onSettings }) => (
  <header className="topbar">
    <div className="app-name">Sentra Brain</div>
    <button className="settings-btn" onClick={onSettings} title="Settings">
      <span role="img" aria-label="settings">⚙️</span>
    </button>
  </header>
);

export default TopBar;
