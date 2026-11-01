import { useState, useCallback, useRef } from 'react';
import type { Telemetry, WSMessage } from '../types/telemetry';

interface UseTelemetryOptions {
  maxPoints?: number;
}

interface UseTelemetryReturn {
  data: Telemetry[];
  latest: Telemetry | null;
  isPaused: boolean;
  pauseTimestamp: number | null;
  selectedIndex: number | null;
  selectedData: Telemetry | null;
  pause: () => void;
  resume: () => void;
  setSelectedIndex: (index: number | null) => void;
  handleMessage: (message: WSMessage) => void;
  clearData: () => void;
}

export function useTelemetry({ maxPoints = 600 }: UseTelemetryOptions = {}): UseTelemetryReturn {
  const [data, setData] = useState<Telemetry[]>([]);
  const [latest, setLatest] = useState<Telemetry | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [pauseTimestamp, setPauseTimestamp] = useState<number | null>(null);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  
  // Buffer for data received while paused
  const pauseBufferRef = useRef<Telemetry[]>([]);
  const pausedDataRef = useRef<Telemetry[]>([]);

  const handleMessage = useCallback((message: WSMessage) => {
    if (message.type === 'telemetry') {
      setLatest(message.data);
      
      if (isPaused) {
        // Buffer data while paused
        pauseBufferRef.current.push(message.data);
      } else {
        setData(prev => {
          const newData = [...prev, message.data];
          return newData.slice(-maxPoints);
        });
      }
    } else if (message.type === 'history') {
      // Initial history from server
      if (!isPaused) {
        setData(message.data.slice(-maxPoints));
        if (message.data.length > 0) {
          setLatest(message.data[message.data.length - 1]);
        }
      }
    }
  }, [isPaused, maxPoints]);

  const pause = useCallback(() => {
    setIsPaused(true);
    setPauseTimestamp(Date.now());
    pausedDataRef.current = [...data];
    pauseBufferRef.current = [];
    setSelectedIndex(null);
  }, [data]);

  const resume = useCallback(() => {
    setIsPaused(false);
    setPauseTimestamp(null);
    setSelectedIndex(null);
    
    // Merge paused data with buffer
    setData(prev => {
      const merged = [...pausedDataRef.current, ...pauseBufferRef.current];
      pauseBufferRef.current = [];
      pausedDataRef.current = [];
      return merged.slice(-maxPoints);
    });
  }, [maxPoints]);

  const clearData = useCallback(() => {
    setData([]);
    setLatest(null);
    pauseBufferRef.current = [];
    pausedDataRef.current = [];
  }, []);

  // Get selected data point when paused
  const selectedData = isPaused && selectedIndex !== null && pausedDataRef.current[selectedIndex]
    ? pausedDataRef.current[selectedIndex]
    : null;

  // Return paused data snapshot when paused
  const displayData = isPaused ? pausedDataRef.current : data;

  return {
    data: displayData,
    latest,
    isPaused,
    pauseTimestamp,
    selectedIndex,
    selectedData,
    pause,
    resume,
    setSelectedIndex,
    handleMessage,
    clearData,
  };
}
