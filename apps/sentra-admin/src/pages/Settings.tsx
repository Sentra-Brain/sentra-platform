// src/pages/Settings.tsx
import { useSettings } from '../hooks/useSettings';

export default function Settings() {
  const token = localStorage.getItem('jwt') || sessionStorage.getItem('jwt');
  const { maxUsers, setMaxUsers, save, loading, error } = useSettings(token || '');

  if (loading) return <p>Loading settings...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  const handleSave = async () => {
    await save(maxUsers!);
    alert('Settings saved!');
  };

  return (
    <section className="page-section">
      <h2 className="page-title">Settings</h2>
      <div className="card">
        <label className="card-label">Max User Slots</label>
        <input
          type="number"
          value={maxUsers ?? ''}
          onChange={(e) => setMaxUsers(Number(e.target.value))}
          className="card-input"
        />
        <button onClick={handleSave} className="card-button">
          Save
        </button>
      </div>
    </section>
  );
}
