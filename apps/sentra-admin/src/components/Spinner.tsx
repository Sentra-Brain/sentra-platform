// src/components/Spinner.tsx
import React from 'react';

const Spinner: React.FC<{ size?: number; color?: string }> = ({ size = 40, color = 'var(--sentra-accent)' }) => {
  return (
    <div
      style={{
        width: size,
        height: size,
        border: `${size * 0.12}px solid rgba(255, 255, 255, 0.2)`,
        borderTopColor: color,
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
        margin: 'auto',
      }}
    />
  );
};

export default Spinner;
