import { useState } from 'react';

interface SettingsPanelProps {
  historySeconds: number;
  onHistoryChange: (seconds: number) => void;
  isConnected: boolean;
  esp32Status: {
    ip: string;
    connected: boolean;
  } | null;
}

export function SettingsPanel({
  historySeconds,
  onHistoryChange,
  isConnected,
  esp32Status,
}: SettingsPanelProps) {
  const [localHistory, setLocalHistory] = useState(historySeconds);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch('/api/buffer/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ history_seconds: localHistory }),
      });
      if (res.ok) {
        onHistoryChange(localHistory);
      }
    } catch (e) {
      console.error('Failed to save settings:', e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>Settings</h3>

      {/* Connection Status */}
      <div style={styles.section}>
        <h4 style={styles.sectionTitle}>Connection Status</h4>
        <div style={styles.statusRow}>
          <span style={styles.statusLabel}>WebSocket:</span>
          <span style={{ ...styles.statusValue, color: isConnected ? '#10b981' : '#ef4444' }}>
            {isConnected ? '● Connected' : '○ Disconnected'}
          </span>
        </div>
        <div style={styles.statusRow}>
          <span style={styles.statusLabel}>ESP32:</span>
          <span style={{ ...styles.statusValue, color: esp32Status?.connected ? '#10b981' : '#ef4444' }}>
            {esp32Status?.connected ? '● Connected' : '○ Disconnected'}
          </span>
        </div>
        {esp32Status && (
          <div style={styles.statusRow}>
            <span style={styles.statusLabel}>IP:</span>
            <span style={styles.statusValue}>{esp32Status.ip}</span>
          </div>
        )}
      </div>

      {/* Buffer Settings */}
      <div style={styles.section}>
        <h4 style={styles.sectionTitle}>Buffer Settings</h4>
        <div style={styles.settingRow}>
          <label style={styles.settingLabel}>History Duration:</label>
          <select
            value={localHistory}
            onChange={(e) => setLocalHistory(Number(e.target.value))}
            style={styles.select}
          >
            <option value={30}>30 seconds</option>
            <option value={60}>1 minute</option>
            <option value={120}>2 minutes</option>
            <option value={180}>3 minutes</option>
            <option value={300}>5 minutes</option>
          </select>
        </div>
        <button
          onClick={handleSave}
          style={styles.saveButton}
          disabled={saving || localHistory === historySeconds}
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>

      {/* Robot Commands */}
      <div style={styles.section}>
        <h4 style={styles.sectionTitle}>Robot Commands</h4>
        <div style={styles.commandGrid}>
          <CommandButton cmd="S" label="Stop" color="#ef4444" />
          <CommandButton cmd="H" label="Hold" color="#f59e0b" />
          <CommandButton cmd="R" label="Reset" color="#8b5cf6" />
          <CommandButton cmd="A" label="Angle Test" color="#10b981" />
          <CommandButton cmd="D" label="Dist Test" color="#3b82f6" />
        </div>
      </div>
    </div>
  );
}

function CommandButton({ cmd, label, color }: { cmd: string; label: string; color: string }) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      await fetch(`/api/command/${cmd}`, { method: 'POST' });
    } catch (e) {
      console.error('Command failed:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      style={{
        ...styles.commandButton,
        backgroundColor: color,
        opacity: loading ? 0.5 : 1,
      }}
    >
      {loading ? '...' : label}
    </button>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: '#1a1a2e',
    borderRadius: 8,
    padding: 16,
    marginTop: 16,
  },
  title: {
    color: '#fff',
    margin: '0 0 16px 0',
    fontSize: 18,
  },
  section: {
    backgroundColor: '#0f0f1a',
    borderRadius: 4,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    color: '#fff',
    margin: '0 0 12px 0',
    fontSize: 14,
  },
  statusRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  statusLabel: {
    color: '#888',
    fontSize: 14,
  },
  statusValue: {
    fontSize: 14,
    fontFamily: 'monospace',
  },
  settingRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
  },
  settingLabel: {
    color: '#888',
    fontSize: 14,
  },
  select: {
    flex: 1,
    padding: '8px 12px',
    backgroundColor: '#1a1a2e',
    border: '1px solid #333',
    borderRadius: 4,
    color: '#fff',
    fontSize: 14,
  },
  saveButton: {
    width: '100%',
    padding: '8px 16px',
    backgroundColor: '#3b82f6',
    color: '#fff',
    border: 'none',
    borderRadius: 4,
    cursor: 'pointer',
  },
  commandGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 8,
  },
  commandButton: {
    padding: '12px 8px',
    color: '#fff',
    border: 'none',
    borderRadius: 4,
    cursor: 'pointer',
    fontWeight: 'bold',
    fontSize: 12,
  },
};
