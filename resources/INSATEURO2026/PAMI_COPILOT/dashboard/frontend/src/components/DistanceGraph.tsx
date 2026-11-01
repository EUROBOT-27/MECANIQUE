import { useMemo } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { Telemetry } from '../types/telemetry';

interface DistanceGraphProps {
  data: Telemetry[];
  isPaused: boolean;
  selectedIndex: number | null;
  onPause: () => void;
  onResume: () => void;
  onSelectIndex: (index: number | null) => void;
}

export function DistanceGraph({
  data,
  isPaused,
  selectedIndex,
  onPause,
  onResume,
  onSelectIndex,
}: DistanceGraphProps) {
  const chartData = useMemo(() => {
    return data.map((d, i) => ({
      x: d.x,
      y: d.y,
      index: i,
      timestamp: d.timestamp,
      dErr: d.dErr,
      dPID: d.dPID,
      state: d.state,
    }));
  }, [data]);

  const latest = data[data.length - 1];
  const selected = selectedIndex !== null ? data[selectedIndex] : null;
  const displayPoint = selected || latest;

  const handleClick = (point: { index: number }) => {
    if (isPaused && point) {
      onSelectIndex(point.index);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Distance Tuning (X/Y Position)</h3>
        <div style={styles.controls}>
          {isPaused ? (
            <button onClick={onResume} style={styles.buttonResume}>
              ▶ Resume
            </button>
          ) : (
            <button onClick={onPause} style={styles.buttonPause}>
              ⏸ Pause
            </button>
          )}
        </div>
      </div>

      <div style={styles.chartContainer}>
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis
              dataKey="x"
              type="number"
              name="X"
              unit="mm"
              stroke="#888"
              domain={['auto', 'auto']}
            />
            <YAxis
              dataKey="y"
              type="number"
              name="Y"
              unit="mm"
              stroke="#888"
              domain={['auto', 'auto']}
            />
            <ReferenceLine x={0} stroke="#666" />
            <ReferenceLine y={0} stroke="#666" />
            <Tooltip
              content={({ payload }) => {
                if (!payload || payload.length === 0) return null;
                const p = payload[0].payload;
                return (
                  <div style={styles.tooltip}>
                    <div><strong>Position</strong></div>
                    <div>X: {p.x?.toFixed(2)} mm</div>
                    <div>Y: {p.y?.toFixed(2)} mm</div>
                    <div>Error: {p.dErr?.toFixed(2)} mm</div>
                    <div>PID Out: {p.dPID?.toFixed(2)}</div>
                    <div>State: {p.state}</div>
                  </div>
                );
              }}
            />
            <Scatter
              data={chartData}
              fill="#3b82f6"
              line={{ stroke: '#3b82f6', strokeWidth: 1 }}
              onClick={(_: unknown, entry: { index: number }) => handleClick(entry)}
              cursor={isPaused ? 'pointer' : 'default'}
            />
            {selected && (
              <Scatter
                data={[{ x: selected.x, y: selected.y }]}
                fill="#f59e0b"
                shape="diamond"
              />
            )}
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {isPaused && data.length > 0 && (
        <div style={styles.sliderContainer}>
          <input
            type="range"
            min={0}
            max={data.length - 1}
            value={selectedIndex ?? data.length - 1}
            onChange={(e) => onSelectIndex(Number(e.target.value))}
            style={styles.slider}
          />
          <span style={styles.sliderLabel}>
            Point {(selectedIndex ?? data.length - 1) + 1} / {data.length}
          </span>
        </div>
      )}

      <div style={styles.infoPanel}>
        <div style={styles.infoItem}>
          <span style={styles.infoLabel}>X:</span>
          <span style={styles.infoValue}>{displayPoint?.x?.toFixed(2) ?? '--'} mm</span>
        </div>
        <div style={styles.infoItem}>
          <span style={styles.infoLabel}>Y:</span>
          <span style={styles.infoValue}>{displayPoint?.y?.toFixed(2) ?? '--'} mm</span>
        </div>
        <div style={styles.infoItem}>
          <span style={styles.infoLabel}>Distance Error:</span>
          <span style={styles.infoValue}>{displayPoint?.dErr?.toFixed(2) ?? '--'} mm</span>
        </div>
        <div style={styles.infoItem}>
          <span style={styles.infoLabel}>PID Output:</span>
          <span style={styles.infoValue}>{displayPoint?.dPID?.toFixed(2) ?? '--'}</span>
        </div>
        <div style={styles.infoItem}>
          <span style={styles.infoLabel}>State:</span>
          <span style={styles.infoValue}>{displayPoint?.state ?? '--'}</span>
        </div>
      </div>

      {displayPoint && (
        <div style={styles.pidDisplay}>
          <span>Distance PID: Kp={displayPoint.dKp} Ki={displayPoint.dKi} Kd={displayPoint.dKd}</span>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: '#1a1a2e',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    color: '#fff',
    margin: 0,
    fontSize: 18,
  },
  controls: {
    display: 'flex',
    gap: 8,
  },
  buttonPause: {
    padding: '8px 16px',
    backgroundColor: '#f59e0b',
    color: '#000',
    border: 'none',
    borderRadius: 4,
    cursor: 'pointer',
    fontWeight: 'bold',
  },
  buttonResume: {
    padding: '8px 16px',
    backgroundColor: '#10b981',
    color: '#fff',
    border: 'none',
    borderRadius: 4,
    cursor: 'pointer',
    fontWeight: 'bold',
  },
  chartContainer: {
    backgroundColor: '#0f0f1a',
    borderRadius: 4,
    padding: 8,
  },
  sliderContainer: {
    marginTop: 12,
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  },
  slider: {
    flex: 1,
    accentColor: '#3b82f6',
  },
  sliderLabel: {
    color: '#888',
    fontSize: 12,
    minWidth: 100,
  },
  infoPanel: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 16,
    marginTop: 12,
    padding: 12,
    backgroundColor: '#0f0f1a',
    borderRadius: 4,
  },
  infoItem: {
    display: 'flex',
    gap: 8,
  },
  infoLabel: {
    color: '#888',
  },
  infoValue: {
    color: '#3b82f6',
    fontWeight: 'bold',
    fontFamily: 'monospace',
  },
  pidDisplay: {
    marginTop: 8,
    padding: 8,
    backgroundColor: '#0f0f1a',
    borderRadius: 4,
    color: '#888',
    fontSize: 12,
    fontFamily: 'monospace',
  },
  tooltip: {
    backgroundColor: '#1a1a2e',
    border: '1px solid #333',
    padding: 8,
    borderRadius: 4,
    color: '#fff',
    fontSize: 12,
  },
};
