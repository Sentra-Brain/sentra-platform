import { useAuth } from "../context/useAuth";

const MODEL_OPTIONS = [
  { value: "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf", label: "TinyLLaMA 1.1B" },
  { value: "qwen2-coder-7b-instruct", label: "Qwen2 Coder 7B" },
  { value: "deepseek-coder-6.7b", label: "DeepSeek Coder 6.7B" },
];

export default function TopBar({ onSettings }: { onSettings: () => void }) {
  const { user } = useAuth();
  if (!user) throw new Error("AuthContext: user unexpectedly null");

  return (
    <header className="topbar">
      <div className="topbar-left"> 
        <select className="model-selector">
          {MODEL_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      <div className="topbar-right">
        <span className="user-info">Hi, {user.full_name || user.email}</span>
        <button className="settings-btn" onClick={onSettings} title="Settings">
          ⚙️
        </button>
      </div>
    </header>
  );
}
