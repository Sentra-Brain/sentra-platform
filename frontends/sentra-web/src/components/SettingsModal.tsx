import React from 'react';

const SettingsModal: React.FC<{ open: boolean; onClose: () => void }> = ({ open, onClose }) => {
  if (!open) return null;
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2>Settings</h2>
        <div>
          {/* Add settings fields here */}
          <p>Basic user settings will go here.</p>
        </div>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
};

export default SettingsModal;
