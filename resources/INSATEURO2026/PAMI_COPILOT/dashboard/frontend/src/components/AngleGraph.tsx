import { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts';
import type { Telemetry } from '../types/telemetry';

interface AngleGraphProps {
  data: Telemetry[];
  isPaused: boolean;
  selectedIndex: number | null;
  onPause: () => void;
  onResume: () => void;
  onSelectIndex: (index: number | null) => void;
}

export function AngleGraph({
  data,
  isPaused,
  selectedIndex,
  onPause,
  onResume,
  onSelectIndex,
}: AngleGraphProps) {
  const chartData = useMemo(() => {
    const startTime = data[0]?.timestamp ?? 0;
    return data.map((d, i) => ({
      time: d.timestamp - startTime,
      theta: (d.th * 180) / Math.PI, // Convert to degrees
      aErr: (d.aErr * 180) / Math.PI,
      aPID: d.aPID,
      index: i,
      state: d.state,
    }));
  }, [data]);

  const latest = data[data.length - 1];
  const selected = selectedIndex !== null ? data[selectedIndex] : null;
  const displayPoint = selected || latest;

  const handleClick = (point: { activeTooltipIndex?: number }) => {
    if (isPaused && point?.activeTooltipIndex !== undefined) {
      onSelectIndex(point.activeTooltipIndex);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Angle Tuning (Theta / Error)</h3>
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
          <LineChart
            data={chartData}
            margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
            onClick={handleClick}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis
              dataKey="time"
              stroke="#888"
              tickFormatter={(v) => `${v.toFixed(1)}s`}
              label={{ value: 'Time (s)', position: 'bottom', fill: '#888' }}
            />
            <YAxis
              stroke="#888"
              domain={['auto', 'auto']}
              label={{ value: 'Degrees', angle: -90, position: 'left', fill: '#888' }}
            />
            <ReferenceLine y={0} stroke="#666" />
            <Tooltip
              content={({ payload }) => {
                if (!payload || payload.length === 0) return null;
                const p = payload[0].payload;
                return (
                  <div style={styles.tooltip}>
                    <div><strong>Angle Data</strong></div>
                    <div>Time: {p.time?.toFixed(2)}s</div>
                    <div>Theta: {p.theta?.toFixed(2)}°</div>
                    <div>Error: {p.aErr?.toFixed(2)}°</div>
                    <div>PID Out: {p.aPID?.toFixed(2)}</div>
                    <div>State: {p.state}</div>
                  </div>
                );
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="theta"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              name="Theta (°)"
            />
            <Line
              type="monotone"
              dataKey="aErr"
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
              name="Error (°)"
            />
            {selectedIndex !== null && (
              <ReferenceLine
                x={chartData[selectedIndex]?.time}
                stroke="#f59e0b"
                strokeWidth={2}
              />
            )}
          </LineChart>
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
          <span style={styles.infoLabel}>Theta:</span>
          <span style={styles.infoValue}>
            {displayPoint ? ((displayPoint.th * 180) / Math.PI).toFixed(2) : '--'}°
          </span>
        </div>
        <div style={styles.infoItem}>
          <span style={styles.infoLabel}>Angle Error:</span>
          <span style={styles.infoValue}>
            {displayPoint ? ((displayPoint.aErr * 180) / Math.PI).toFixed(2) : '--'}°
          </span>
        </div>
        <div style={styles.infoItem}>
          <span style={styles.infoLabel}>PID Output:</span>
          <span style={styles.infoValue}>{displayPoint?.aPID?.toFixed(2) ?? '--'}</span>
        </div>
        <div style={styles.infoItem}>
          <span style={styles.infoLabel}>State:</span>
          <span style={styles.infoValue}>{displayPoint?.state ?? '--'}</span>
        </div>
      </div>

      {displayPoint && (
        <div style={styles.pidDisplay}>
          <span>Angle PID: Kp={displayPoint.aKp} Ki={displayPoint.aKi} Kd={displayPoint.aKd}</span>
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
    accentColor: '#10b981',
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
    color: '#10b981',
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
