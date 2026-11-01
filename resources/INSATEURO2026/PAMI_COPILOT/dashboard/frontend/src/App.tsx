import { useCallback, useState } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { useTelemetry } from './hooks/useTelemetry';
import { DistanceGraph } from './components/DistanceGraph';
import { AngleGraph } from './components/AngleGraph';
import { ParameterPanel } from './components/ParameterPanel';
import { SettingsPanel } from './components/SettingsPanel';
import type { WSMessage } from './types/telemetry';

const WS_URL = `ws://${window.location.hostname}:8080/ws`;

export default function App() {
  const [historySeconds, setHistorySeconds] = useState(60);
  
  const telemetry = useTelemetry({ maxPoints: historySeconds * 10 });
  
  const handleMessage = useCallback((message: WSMessage) => {
    telemetry.handleMessage(message);
  }, [telemetry.handleMessage]);

  const { isConnected, status } = useWebSocket({
    url: WS_URL,
    onMessage: handleMessage,
  });

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <h1 style={styles.title}>🤖 PID Tuning Dashboard</h1>
        <div style={styles.connectionStatus}>
          <span style={{
            ...styles.statusDot,
            backgroundColor: isConnected ? '#10b981' : '#ef4444',
          }} />
          <span style={styles.statusText}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </header>

      <main style={styles.main}>
        <div style={styles.graphColumn}>
          <DistanceGraph
            data={telemetry.data}
            isPaused={telemetry.isPaused}
            selectedIndex={telemetry.selectedIndex}
            onPause={telemetry.pause}
            onResume={telemetry.resume}
            onSelectIndex={telemetry.setSelectedIndex}
          />
          
          <AngleGraph
            data={telemetry.data}
            isPaused={telemetry.isPaused}
            selectedIndex={telemetry.selectedIndex}
            onPause={telemetry.pause}
            onResume={telemetry.resume}
            onSelectIndex={telemetry.setSelectedIndex}
          />
        </div>

        <div style={styles.controlColumn}>
          <ParameterPanel
            latest={telemetry.latest}
            isConnected={status?.connected ?? false}
          />
          
          <SettingsPanel
            historySeconds={historySeconds}
            onHistoryChange={setHistorySeconds}
            isConnected={isConnected}
            esp32Status={status}
          />
        </div>
      </main>

      <footer style={styles.footer}>
        <span>Data points: {telemetry.data.length}</span>
        {telemetry.isPaused && (
          <span style={styles.pausedBadge}>⏸ PAUSED</span>
        )}
        <span>State: {telemetry.latest?.state ?? 'N/A'}</span>
      </footer>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#0f0f1a',
    color: '#fff',
    fontFamily: 'system-ui, -apple-system, sans-serif',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 24px',
    backgroundColor: '#1a1a2e',
    borderBottom: '1px solid #333',
  },
  title: {
    margin: 0,
    fontSize: 24,
  },
  connectionStatus: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: '50%',
  },
  statusText: {
    fontSize: 14,
    color: '#888',
  },
  main: {
    display: 'flex',
    gap: 24,
    padding: 24,
    maxWidth: 1600,
    margin: '0 auto',
  },
  graphColumn: {
    flex: 2,
    minWidth: 0,
  },
  controlColumn: {
    flex: 1,
    minWidth: 320,
    maxWidth: 400,
  },
  footer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 24,
    padding: '12px 24px',
    backgroundColor: '#1a1a2e',
    borderTop: '1px solid #333',
    fontSize: 12,
    color: '#666',
  },
  pausedBadge: {
    backgroundColor: '#f59e0b',
    color: '#000',
    padding: '4px 8px',
    borderRadius: 4,
    fontWeight: 'bold',
  },
};
