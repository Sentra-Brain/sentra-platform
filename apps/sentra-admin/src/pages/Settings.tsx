import { useSettings } from '../hooks/useSettings';

export default function Settings() {
  const token = localStorage.getItem('jwt') || sessionStorage.getItem('jwt');
  const { settings, setSettings, save, loading, error } = useSettings(token || '');

  if (loading) return <p className="text-sm text-sentra-accent-light">Loading settings...</p>;
  if (error) return <p className="text-red-500 text-sm">{error}</p>;

  const handleSave = async () => {
    await save(settings!);
    alert('Settings saved!');
  };

  return (
    <section className="page-section">
      <h2 className="page-title">System Settings</h2>

      <div className="card">
        <label className="block mb-2 font-semibold">Workspace Name</label>
        <input
          className="card-input"
          value={settings.workspace_name}
          onChange={(e) => setSettings({ ...settings, workspace_name: e.target.value })}
        />

        <label className="block mb-2 font-semibold">License Type</label>
        <input className="card-input" value={settings.license_type} disabled />

        <div className="flex items-center gap-3 mb-4">
          <input
            type="checkbox"
            checked={settings.maintenance_mode}
            onChange={(e) => setSettings({ ...settings, maintenance_mode: e.target.checked })}
            className="accent-[var(--sentra-accent)]"
          />
          <label className="font-semibold">Maintenance Mode</label>
        </div>

        <label className="block mb-2 font-semibold">Default Language</label>
        <input
          className="card-input"
          value={settings.default_language}
          onChange={(e) => setSettings({ ...settings, default_language: e.target.value })}
        />

        <label className="block mb-2 font-semibold">Log Retention (days)</label>
        <input
          type="number"
          className="card-input"
          value={settings.log_retention_days}
          onChange={(e) => setSettings({ ...settings, log_retention_days: +e.target.value })}
        />

        <label className="block mb-2 font-semibold">Max Users</label>
        <input
          type="number"
          className="card-input"
          value={settings.max_users}
          onChange={(e) => setSettings({ ...settings, max_users: +e.target.value })}
        />

        <button className="card-button" onClick={handleSave}>
          Save Settings
        </button>
      </div>
    </section>
  );
}
