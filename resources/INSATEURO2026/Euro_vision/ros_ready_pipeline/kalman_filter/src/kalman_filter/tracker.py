"""
Kalman Filter implementation for ArUco marker tracking.

This module implements a Kalman filter for 2D position and orientation tracking
with support for handling missing detections during occlusion or frame drops.
"""

import numpy as np
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
from enum import Enum


class MarkerType(Enum):
    """Types of ArUco markers in the system."""
    MAP = "map"  # IDs 20-23 (fixed corner anchors)
    CAISSE = "caisse"  # IDs 36, 47, 41 (blue, yellow, black boxes)
    ENEMY = "enemy"  # IDs 30+ (opponent robots)


@dataclass
class MarkerState:
    """Represents the state of a tracked marker."""
    marker_id: int
    marker_type: MarkerType
    x: float
    y: float
    theta: float
    confidence: float
    frames_since_detection: int
    is_occluded: bool


class KalmanTracker:
    """
    Kalman Filter for tracking a single ArUco marker in 2D space.
    
    State vector: [x, y, theta, vx, vy, vtheta]
    - x, y: position in meters
    - theta: orientation in radians
    - vx, vy: linear velocities
    - vtheta: angular velocity
    """
    
    def __init__(self, marker_id: int, marker_type: MarkerType,
                 process_noise: float = 0.01, measurement_noise: float = 0.1,
                 max_frames_without_detection: int = 30):
        """
        Initialize Kalman filter for marker tracking.
        
        Args:
            marker_id: Unique ID of the ArUco marker
            marker_type: Type of marker (MAP, CAISSE, ENEMY)
            process_noise: Process noise covariance (Q)
            measurement_noise: Measurement noise covariance (R)
            max_frames_without_detection: Maximum frames before marking as lost
        """
        self.marker_id = marker_id
        self.marker_type = marker_type
        self.max_frames_without_detection = max_frames_without_detection
        
        # State vector: [x, y, theta, vx, vy, vtheta]
        self.state = np.zeros(6)
        
        # State covariance matrix
        self.P = np.eye(6) * 1.0
        
        # Process noise covariance
        self.Q = np.eye(6) * process_noise
        # Higher noise for velocities
        self.Q[3:, 3:] *= 2.0
        
        # Measurement noise covariance
        self.R = np.eye(3) * measurement_noise
        
        # State transition matrix (will be updated with dt)
        self.F = np.eye(6)
        
        # Measurement matrix (we observe position and orientation)
        self.H = np.zeros((3, 6))
        self.H[0, 0] = 1.0  # x
        self.H[1, 1] = 1.0  # y
        self.H[2, 2] = 1.0  # theta
        
        # Tracking state
        self.is_initialized = False
        self.frames_since_detection = 0
        self.total_updates = 0
        
    def predict(self, dt: float = 0.033) -> MarkerState:
        """
        Predict the next state using the motion model.
        
        Args:
            dt: Time step in seconds (default: 0.033s = 30 FPS)
            
        Returns:
            Predicted marker state
        """
        # Update state transition matrix with dt
        self.F[0, 3] = dt  # x += vx * dt
        self.F[1, 4] = dt  # y += vy * dt
        self.F[2, 5] = dt  # theta += vtheta * dt
        
        # Predict state
        self.state = self.F @ self.state
        
        # Normalize theta to [-pi, pi]
        self.state[2] = self._normalize_angle(self.state[2])
        
        # Predict covariance
        self.P = self.F @ self.P @ self.F.T + self.Q
        
        self.frames_since_detection += 1
        
        return self._get_current_state()
    
    def update(self, measurement: Tuple[float, float, float]) -> MarkerState:
        """
        Update the filter with a new measurement.
        
        Args:
            measurement: Tuple of (x, y, theta) in meters and radians
            
        Returns:
            Updated marker state
        """
        if not self.is_initialized:
            # Initialize state with first measurement
            self.state[0] = measurement[0]  # x
            self.state[1] = measurement[1]  # y
            self.state[2] = measurement[2]  # theta
            self.state[3:] = 0.0  # velocities
            self.is_initialized = True
            self.frames_since_detection = 0
            self.total_updates = 1
            return self._get_current_state()
        
        # Convert measurement to numpy array
        z = np.array(measurement)
        z[2] = self._normalize_angle(z[2])
        
        # Compute innovation (measurement residual)
        y = z - self.H @ self.state
        y[2] = self._normalize_angle(y[2])
        
        # Innovation covariance
        S = self.H @ self.P @ self.H.T + self.R
        
        # Kalman gain
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # Update state
        self.state = self.state + K @ y
        self.state[2] = self._normalize_angle(self.state[2])
        
        # Update covariance
        I = np.eye(6)
        self.P = (I - K @ self.H) @ self.P
        
        self.frames_since_detection = 0
        self.total_updates += 1
        
        return self._get_current_state()
    
    def _get_current_state(self) -> MarkerState:
        """Get current marker state."""
        # Confidence decreases with frames since detection
        confidence = max(0.0, 1.0 - (self.frames_since_detection / 
                                     self.max_frames_without_detection))
        
        is_occluded = self.frames_since_detection > 0
        
        return MarkerState(
            marker_id=self.marker_id,
            marker_type=self.marker_type,
            x=float(self.state[0]),
            y=float(self.state[1]),
            theta=float(self.state[2]),
            confidence=confidence,
            frames_since_detection=self.frames_since_detection,
            is_occluded=is_occluded
        )
    
    def is_lost(self) -> bool:
        """Check if the marker is considered lost."""
        return self.frames_since_detection > self.max_frames_without_detection
    
    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """Normalize angle to [-pi, pi]."""
        while angle > np.pi:
            angle -= 2 * np.pi
        while angle < -np.pi:
            angle += 2 * np.pi
        return angle


class MultiMarkerTracker:
    """
    Manages multiple Kalman filters for tracking multiple ArUco markers.
    
    This class handles:
    - Tracking multiple markers simultaneously
    - Automatic creation/deletion of trackers
    - Handling occlusion and re-detection
    - Classification by marker type
    """
    
    def __init__(self, process_noise: float = 0.01, 
                 measurement_noise: float = 0.1,
                 max_frames_without_detection: int = 30):
        """
        Initialize multi-marker tracker.
        
        Args:
            process_noise: Process noise for Kalman filters
            measurement_noise: Measurement noise for Kalman filters
            max_frames_without_detection: Frames before marking marker as lost
        """
        self.trackers: Dict[int, KalmanTracker] = {}
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        self.max_frames_without_detection = max_frames_without_detection
    
    @staticmethod
    def classify_marker(marker_id: int) -> MarkerType:
        """
        Classify marker by ID according to competition specifications.
        
        Competition ID Schema:
        - Map anchors: 20-23 (fixed corner references)
        - Caisses: 36 (blue), 47 (yellow), 41 (black/rotten)
        - Enemy robots: 30-35, 38-40, 42-46, 48+ (excluding caisse IDs)
        """
        if 20 <= marker_id <= 23:
            return MarkerType.MAP
        elif marker_id in [36, 47, 41]:  # Competition caisse IDs
            return MarkerType.CAISSE
        elif marker_id >= 30:  # Enemy robots (30+, excluding caisse IDs)
            return MarkerType.ENEMY
        else:
            # Unknown ID - default to ENEMY for safety
            return MarkerType.ENEMY
    
    def update(self, detections: Dict[int, Tuple[float, float, float]], 
               dt: float = 0.033) -> Dict[int, MarkerState]:
        """
        Update all trackers with new detections.
        
        Args:
            detections: Dictionary mapping marker_id to (x, y, theta)
            dt: Time step in seconds
            
        Returns:
            Dictionary of all tracked marker states
        """
        # Predict step for all existing trackers
        for marker_id, tracker in list(self.trackers.items()):
            tracker.predict(dt)
            
            # Remove lost markers
            if tracker.is_lost():
                del self.trackers[marker_id]
        
        # Update step for detected markers
        for marker_id, measurement in detections.items():
            if marker_id not in self.trackers:
                # Create new tracker for this marker
                marker_type = self.classify_marker(marker_id)
                self.trackers[marker_id] = KalmanTracker(
                    marker_id=marker_id,
                    marker_type=marker_type,
                    process_noise=self.process_noise,
                    measurement_noise=self.measurement_noise,
                    max_frames_without_detection=self.max_frames_without_detection
                )
            
            self.trackers[marker_id].update(measurement)
        
        # Return all current states
        return {
            marker_id: tracker._get_current_state()
            for marker_id, tracker in self.trackers.items()
        }
    
    def get_state(self, marker_id: int) -> Optional[MarkerState]:
        """Get state of a specific marker."""
        tracker = self.trackers.get(marker_id)
        return tracker._get_current_state() if tracker else None
    
    def get_all_states(self) -> Dict[int, MarkerState]:
        """Get states of all tracked markers."""
        return {
            marker_id: tracker._get_current_state()
            for marker_id, tracker in self.trackers.items()
        }
    
    def get_states_by_type(self, marker_type: MarkerType) -> Dict[int, MarkerState]:
        """Get all markers of a specific type."""
        return {
            marker_id: state
            for marker_id, state in self.get_all_states().items()
            if state.marker_type == marker_type
        }
    
    def get_tracking_summary(self) -> Dict[str, int]:
        """Get summary of tracking status."""
        states = self.get_all_states()
        return {
            'total_markers': len(states),
            'map_markers': len([s for s in states.values() if s.marker_type == MarkerType.MAP]),
            'caisse_markers': len([s for s in states.values() if s.marker_type == MarkerType.CAISSE]),
            'enemy_markers': len([s for s in states.values() if s.marker_type == MarkerType.ENEMY]),
            'occluded_markers': len([s for s in states.values() if s.is_occluded]),
            'tracked_markers': len([s for s in states.values() if not s.is_occluded])
        }
