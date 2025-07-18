import { useAuth } from '../context/useAuth';
import { MoreVertical, Settings, LayoutDashboard, Archive, Flag, Trash2 } from 'lucide-react';
import './TopBar.css';
import { useState } from 'react';

const MODEL_OPTIONS = [
  { value: 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf', label: 'TinyLLaMA 1.1B' },
  { value: 'qwen2-coder-7b-instruct', label: 'Qwen2 Coder 7B' },
  { value: 'deepseek-coder-6.7b', label: 'DeepSeek Coder 6.7B' },
];

export default function TopBar() {
  const { user } = useAuth();
  if (!user) throw new Error("AuthContext: user unexpectedly null");

  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="topbar">
      <div className="topbar-left">
        <select className="model-selector">
          {MODEL_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="topbar-right">
        <div className="menu-container">
          <button className="menu-toggle-btn" onClick={() => setMenuOpen(!menuOpen)} title="Menu">
            <MoreVertical size={20} />
          </button>

          {menuOpen && (
            <div className="topbar-menu">
              <button>
                <LayoutDashboard size={16} /> Manage Sentra
              </button>
              <button>
                <Settings size={16} /> Settings
              </button>
              <button>
                <Archive size={16} /> Archive
              </button>
              <button>
                <Flag size={16} /> Report
              </button>
              <button className="danger">
                <Trash2 size={16} /> Delete
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
