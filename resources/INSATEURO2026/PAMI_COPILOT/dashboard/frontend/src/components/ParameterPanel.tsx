import { useState, useEffect } from 'react';
import { PARAM_BOUNDS } from '../types/telemetry';
import type { AnglePIDParams, DistancePIDParams, Telemetry } from '../types/telemetry';

interface ParameterPanelProps {
  latest: Telemetry | null;
  isConnected: boolean;
}

type ParamKey = 'kp' | 'ki' | 'kd';

export function ParameterPanel({ latest, isConnected }: ParameterPanelProps) {
  // Applied values (from telemetry)
  const [appliedAngle, setAppliedAngle] = useState<AnglePIDParams>({ kp: 120, ki: 0, kd: 1.5 });
  const [appliedDistance, setAppliedDistance] = useState<DistancePIDParams>({ kp: 1, ki: 0, kd: 0 });
  
  // Pending values (user input)
  const [pendingAngle, setPendingAngle] = useState<AnglePIDParams>({ kp: 120, ki: 0, kd: 1.5 });
  const [pendingDistance, setPendingDistance] = useState<DistancePIDParams>({ kp: 1, ki: 0, kd: 0 });
  
  // Loading states
  const [loadingAngle, setLoadingAngle] = useState(false);
  const [loadingDistance, setLoadingDistance] = useState(false);
  
  // Error messages
  const [errorAngle, setErrorAngle] = useState<string | null>(null);
  const [errorDistance, setErrorDistance] = useState<string | null>(null);
  
  // Success feedback
  const [successAngle, setSuccessAngle] = useState(false);
  const [successDistance, setSuccessDistance] = useState(false);

  // Update applied values from telemetry
  useEffect(() => {
    if (latest) {
      const newAngle = { kp: latest.aKp, ki: latest.aKi, kd: latest.aKd };
      const newDistance = { kp: latest.dKp, ki: latest.dKi, kd: latest.dKd };
      setAppliedAngle(newAngle);
      setAppliedDistance(newDistance);
    }
  }, [latest]);

  const hasAngleChanges = 
    pendingAngle.kp !== appliedAngle.kp ||
    pendingAngle.ki !== appliedAngle.ki ||
    pendingAngle.kd !== appliedAngle.kd;

  const hasDistanceChanges = 
    pendingDistance.kp !== appliedDistance.kp ||
    pendingDistance.ki !== appliedDistance.ki ||
    pendingDistance.kd !== appliedDistance.kd;

  const submitAngle = async () => {
    setLoadingAngle(true);
    setErrorAngle(null);
    setSuccessAngle(false);
    
    try {
      const res = await fetch('/api/params/angle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pendingAngle),
      });
      
      const data = await res.json();
      
      if (!res.ok || !data.success) {
        setErrorAngle(data.detail || data.message || 'Failed to update');
      } else {
        setSuccessAngle(true);
        setTimeout(() => setSuccessAngle(false), 2000);
      }
    } catch (e) {
      setErrorAngle('Network error');
    } finally {
      setLoadingAngle(false);
    }
  };

  const submitDistance = async () => {
    setLoadingDistance(true);
    setErrorDistance(null);
    setSuccessDistance(false);
    
    try {
      const res = await fetch('/api/params/distance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pendingDistance),
      });
      
      const data = await res.json();
      
      if (!res.ok || !data.success) {
        setErrorDistance(data.detail || data.message || 'Failed to update');
      } else {
        setSuccessDistance(true);
        setTimeout(() => setSuccessDistance(false), 2000);
      }
    } catch (e) {
      setErrorDistance('Network error');
    } finally {
      setLoadingDistance(false);
    }
  };

  const resetAngle = () => setPendingAngle(appliedAngle);
  const resetDistance = () => setPendingDistance(appliedDistance);

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>PID Parameters</h3>
      
      {!isConnected && (
        <div style={styles.warning}>
          ⚠️ ESP32 not connected - parameter changes will fail
        </div>
      )}

      {/* Angle PID Section */}
      <div style={styles.section}>
        <div style={styles.sectionHeader}>
          <h4 style={styles.sectionTitle}>Angle PID</h4>
          {successAngle && <span style={styles.success}>✓ Applied</span>}
        </div>
        
        <ParamSlider
          label="Kp"
          value={pendingAngle.kp}
          applied={appliedAngle.kp}
          min={PARAM_BOUNDS.angle.kp.min}
          max={PARAM_BOUNDS.angle.kp.max}
          step={1}
          onChange={(v) => setPendingAngle({ ...pendingAngle, kp: v })}
          hasChange={pendingAngle.kp !== appliedAngle.kp}
        />
        <ParamSlider
          label="Ki"
          value={pendingAngle.ki}
          applied={appliedAngle.ki}
          min={PARAM_BOUNDS.angle.ki.min}
          max={PARAM_BOUNDS.angle.ki.max}
          step={0.1}
          onChange={(v) => setPendingAngle({ ...pendingAngle, ki: v })}
          hasChange={pendingAngle.ki !== appliedAngle.ki}
        />
        <ParamSlider
          label="Kd"
          value={pendingAngle.kd}
          applied={appliedAngle.kd}
          min={PARAM_BOUNDS.angle.kd.min}
          max={PARAM_BOUNDS.angle.kd.max}
          step={0.1}
          onChange={(v) => setPendingAngle({ ...pendingAngle, kd: v })}
          hasChange={pendingAngle.kd !== appliedAngle.kd}
        />
        
        {errorAngle && <div style={styles.error}>{errorAngle}</div>}
        
        <div style={styles.buttonRow}>
          <button
            onClick={resetAngle}
            style={styles.buttonReset}
            disabled={!hasAngleChanges}
          >
            Reset
          </button>
          <button
            onClick={submitAngle}
            style={{
              ...styles.buttonSubmit,
              opacity: !hasAngleChanges || loadingAngle || !isConnected ? 0.5 : 1,
            }}
            disabled={!hasAngleChanges || loadingAngle || !isConnected}
          >
            {loadingAngle ? 'Applying...' : 'Apply Angle PID'}
          </button>
        </div>
      </div>

      {/* Distance PID Section */}
      <div style={styles.section}>
        <div style={styles.sectionHeader}>
          <h4 style={styles.sectionTitle}>Distance PID</h4>
          {successDistance && <span style={styles.success}>✓ Applied</span>}
        </div>
        
        <ParamSlider
          label="Kp"
          value={pendingDistance.kp}
          applied={appliedDistance.kp}
          min={PARAM_BOUNDS.distance.kp.min}
          max={PARAM_BOUNDS.distance.kp.max}
          step={0.1}
          onChange={(v) => setPendingDistance({ ...pendingDistance, kp: v })}
          hasChange={pendingDistance.kp !== appliedDistance.kp}
        />
        <ParamSlider
          label="Ki"
          value={pendingDistance.ki}
          applied={appliedDistance.ki}
          min={PARAM_BOUNDS.distance.ki.min}
          max={PARAM_BOUNDS.distance.ki.max}
          step={0.01}
          onChange={(v) => setPendingDistance({ ...pendingDistance, ki: v })}
          hasChange={pendingDistance.ki !== appliedDistance.ki}
        />
        <ParamSlider
          label="Kd"
          value={pendingDistance.kd}
          applied={appliedDistance.kd}
          min={PARAM_BOUNDS.distance.kd.min}
          max={PARAM_BOUNDS.distance.kd.max}
          step={0.1}
          onChange={(v) => setPendingDistance({ ...pendingDistance, kd: v })}
          hasChange={pendingDistance.kd !== appliedDistance.kd}
        />
        
        {errorDistance && <div style={styles.error}>{errorDistance}</div>}
        
        <div style={styles.buttonRow}>
          <button
            onClick={resetDistance}
            style={styles.buttonReset}
            disabled={!hasDistanceChanges}
          >
            Reset
          </button>
          <button
            onClick={submitDistance}
            style={{
              ...styles.buttonSubmit,
              opacity: !hasDistanceChanges || loadingDistance || !isConnected ? 0.5 : 1,
            }}
            disabled={!hasDistanceChanges || loadingDistance || !isConnected}
          >
            {loadingDistance ? 'Applying...' : 'Apply Distance PID'}
          </button>
        </div>
      </div>
    </div>
  );
}

interface ParamSliderProps {
  label: string;
  value: number;
  applied: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
  hasChange: boolean;
}

function ParamSlider({ label, value, applied, min, max, step, onChange, hasChange }: ParamSliderProps) {
  return (
    <div style={styles.sliderRow}>
      <label style={styles.sliderLabel}>
        {label}
        {hasChange && <span style={styles.changed}>*</span>}
      </label>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={styles.slider}
      />
      <input
        type="number"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => {
          const v = Number(e.target.value);
          if (v >= min && v <= max) onChange(v);
        }}
        style={{
          ...styles.numberInput,
          borderColor: hasChange ? '#f59e0b' : '#333',
        }}
      />
      <span style={styles.appliedValue}>
        (applied: {applied})
      </span>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: '#1a1a2e',
    borderRadius: 8,
    padding: 16,
  },
  title: {
    color: '#fff',
    margin: '0 0 16px 0',
    fontSize: 18,
  },
  warning: {
    backgroundColor: '#78350f',
    color: '#fbbf24',
    padding: 12,
    borderRadius: 4,
    marginBottom: 16,
    fontSize: 14,
  },
  section: {
    backgroundColor: '#0f0f1a',
    borderRadius: 4,
    padding: 16,
    marginBottom: 16,
  },
  sectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    color: '#fff',
    margin: 0,
    fontSize: 16,
  },
  success: {
    color: '#10b981',
    fontSize: 14,
    fontWeight: 'bold',
  },
  sliderRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
  },
  sliderLabel: {
    color: '#888',
    width: 40,
    fontSize: 14,
  },
  changed: {
    color: '#f59e0b',
    marginLeft: 4,
  },
  slider: {
    flex: 1,
    accentColor: '#3b82f6',
  },
  numberInput: {
    width: 70,
    padding: '4px 8px',
    backgroundColor: '#1a1a2e',
    border: '1px solid #333',
    borderRadius: 4,
    color: '#fff',
    fontSize: 14,
    textAlign: 'right' as const,
  },
  appliedValue: {
    color: '#666',
    fontSize: 12,
    minWidth: 90,
  },
  error: {
    backgroundColor: '#7f1d1d',
    color: '#fca5a5',
    padding: 8,
    borderRadius: 4,
    marginBottom: 12,
    fontSize: 14,
  },
  buttonRow: {
    display: 'flex',
    gap: 12,
    marginTop: 16,
  },
  buttonReset: {
    padding: '8px 16px',
    backgroundColor: 'transparent',
    color: '#888',
    border: '1px solid #333',
    borderRadius: 4,
    cursor: 'pointer',
  },
  buttonSubmit: {
    flex: 1,
    padding: '8px 16px',
    backgroundColor: '#3b82f6',
    color: '#fff',
    border: 'none',
    borderRadius: 4,
    cursor: 'pointer',
    fontWeight: 'bold',
  },
};
