"""Circular buffer for telemetry data with timestamp indexing."""
import time
import threading
from collections import deque
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class TelemetryPoint:
    """Single telemetry data point."""
    timestamp: float
    state: str
    x: float
    y: float
    th: float
    aErr: float
    dErr: float
    aPID: float
    dPID: float
    aKp: float
    aKi: float
    aKd: float
    dKp: float
    dKi: float
    dKd: float
    L: int
    R: int
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'state': self.state,
            'x': self.x,
            'y': self.y,
            'th': self.th,
            'aErr': self.aErr,
            'dErr': self.dErr,
            'aPID': self.aPID,
            'dPID': self.dPID,
            'aKp': self.aKp,
            'aKi': self.aKi,
            'aKd': self.aKd,
            'dKp': self.dKp,
            'dKi': self.dKi,
            'dKd': self.dKd,
            'L': self.L,
            'R': self.R,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TelemetryPoint':
        return cls(
            timestamp=data.get('timestamp', time.time()),
            state=data.get('state', 'UNKNOWN'),
            x=data.get('x', 0.0),
            y=data.get('y', 0.0),
            th=data.get('th', 0.0),
            aErr=data.get('aErr', 0.0),
            dErr=data.get('dErr', 0.0),
            aPID=data.get('aPID', 0.0),
            dPID=data.get('dPID', 0.0),
            aKp=data.get('aKp', 120.0),
            aKi=data.get('aKi', 0.0),
            aKd=data.get('aKd', 1.5),
            dKp=data.get('dKp', 1.0),
            dKi=data.get('dKi', 0.0),
            dKd=data.get('dKd', 0.0),
            L=data.get('L', 0),
            R=data.get('R', 0),
        )


class TelemetryBuffer:
    """Thread-safe circular buffer for telemetry with time-based queries."""
    
    def __init__(self, history_seconds: int = 60, sample_rate_hz: int = 10):
        """
        Initialize buffer.
        
        Args:
            history_seconds: How many seconds of history to keep
            sample_rate_hz: Expected sample rate (for buffer sizing)
        """
        self._history_seconds = history_seconds
        self._max_size = history_seconds * sample_rate_hz
        self._buffer: deque = deque(maxlen=self._max_size)
        self._lock = threading.RLock()
        self._latest: Optional[TelemetryPoint] = None
    
    @property
    def history_seconds(self) -> int:
        return self._history_seconds
    
    @history_seconds.setter
    def history_seconds(self, value: int):
        with self._lock:
            self._history_seconds = value
            new_max = value * 10  # Assume 10Hz
            # Create new buffer with adjusted size
            old_data = list(self._buffer)
            self._buffer = deque(old_data[-new_max:] if len(old_data) > new_max else old_data, maxlen=new_max)
            self._max_size = new_max
    
    def add(self, data: dict):
        """Add telemetry data point."""
        point = TelemetryPoint.from_dict(data)
        with self._lock:
            self._buffer.append(point)
            self._latest = point
    
    def get_latest(self) -> Optional[dict]:
        """Get the most recent data point."""
        with self._lock:
            return self._latest.to_dict() if self._latest else None
    
    def get_all(self) -> List[dict]:
        """Get all buffered data points."""
        with self._lock:
            return [p.to_dict() for p in self._buffer]
    
    def get_range(self, from_ts: float, to_ts: float) -> List[dict]:
        """Get data points within a timestamp range."""
        with self._lock:
            return [
                p.to_dict() for p in self._buffer
                if from_ts <= p.timestamp <= to_ts
            ]
    
    def get_last_n_seconds(self, seconds: float) -> List[dict]:
        """Get data points from the last N seconds."""
        cutoff = time.time() - seconds
        with self._lock:
            return [p.to_dict() for p in self._buffer if p.timestamp >= cutoff]
    
    def get_size(self) -> int:
        """Get current buffer size."""
        with self._lock:
            return len(self._buffer)
    
    def clear(self):
        """Clear all buffered data."""
        with self._lock:
            self._buffer.clear()
            self._latest = None
