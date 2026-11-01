"""
Occlusion handling strategies for ArUco marker tracking.

This module implements various strategies to handle marker occlusion:
1. Kalman prediction during full occlusion
2. Partial marker detection (corners visible)
3. History-based estimation
4. Confidence-weighted fusion
"""

import numpy as np
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time


class OcclusionStrategy(Enum):
    """Strategies for handling occlusion."""
    KALMAN_PREDICTION = "kalman_prediction"
    PARTIAL_DETECTION = "partial_detection"
    HISTORY_BASED = "history_based"
    CONFIDENCE_FUSION = "confidence_fusion"


@dataclass
class DetectionQuality:
    """Represents the quality of a marker detection."""
    marker_id: int
    detected: bool
    corners_detected: int  # Number of visible corners (0-4)
    detection_confidence: float  # 0.0 to 1.0
    is_partial: bool
    timestamp: float
    
    def get_quality_score(self) -> float:
        """Calculate overall quality score."""
        if not self.detected:
            return 0.0
        
        corner_score = self.corners_detected / 4.0
        return (corner_score + self.detection_confidence) / 2.0


@dataclass
class OcclusionState:
    """Tracks occlusion state for a marker."""
    marker_id: int
    is_occluded: bool
    occlusion_duration: int = 0  # frames
    last_good_detection: Optional[Tuple[float, float, float]] = None
    last_detection_time: float = 0.0
    detection_history: List[Tuple[float, float, float, float]] = field(default_factory=list)  # (x, y, theta, timestamp)
    partial_detections: int = 0
    full_occlusions: int = 0


class OcclusionHandler:
    """
    Handles marker occlusion using multiple strategies.
    
    This class:
    - Detects when markers are occluded
    - Applies appropriate strategies based on occlusion type
    - Maintains detection history for recovery
    - Provides confidence scores for estimates
    """
    
    def __init__(self, history_length: int = 30, 
                 partial_detection_threshold: float = 0.5,
                 occlusion_timeout: float = 1.0):
        """
        Initialize occlusion handler.
        
        Args:
            history_length: Number of past detections to keep
            partial_detection_threshold: Minimum quality for partial detection
            occlusion_timeout: Seconds before considering marker lost
        """
        self.history_length = history_length
        self.partial_detection_threshold = partial_detection_threshold
        self.occlusion_timeout = occlusion_timeout
        
        # Track occlusion state for each marker
        self.occlusion_states: Dict[int, OcclusionState] = {}
        
    def update_detection_quality(self, marker_id: int, 
                                quality: DetectionQuality) -> OcclusionState:
        """
        Update detection quality and occlusion state for a marker.
        
        Args:
            marker_id: ID of the marker
            quality: Detection quality information
            
        Returns:
            Updated occlusion state
        """
        if marker_id not in self.occlusion_states:
            self.occlusion_states[marker_id] = OcclusionState(
                marker_id=marker_id,
                is_occluded=not quality.detected
            )
        
        state = self.occlusion_states[marker_id]
        
        if quality.detected:
            if quality.is_partial:
                state.partial_detections += 1
                state.occlusion_duration += 1
                state.is_occluded = True
            else:
                # Full detection - reset occlusion
                state.occlusion_duration = 0
                state.is_occluded = False
                state.last_detection_time = quality.timestamp
        else:
            state.full_occlusions += 1
            state.occlusion_duration += 1
            state.is_occluded = True
        
        return state
    
    def handle_occlusion(self, marker_id: int, 
                        detection_quality: DetectionQuality,
                        kalman_prediction: Optional[Tuple[float, float, float]] = None) -> Tuple[Optional[Tuple[float, float, float]], float]:
        """
        Handle occluded marker using appropriate strategy.
        
        Args:
            marker_id: ID of the marker
            detection_quality: Current detection quality
            kalman_prediction: Predicted position from Kalman filter
            
        Returns:
            Tuple of (estimated_pose, confidence) where:
            - estimated_pose is (x, y, theta) or None if lost
            - confidence is 0.0 to 1.0
        """
        state = self.update_detection_quality(marker_id, detection_quality)
        
        # Check if marker is lost (timeout exceeded)
        if state.is_occluded:
            time_since_detection = time.time() - state.last_detection_time
            if time_since_detection > self.occlusion_timeout:
                return None, 0.0
        
        # Strategy selection based on detection quality
        if not detection_quality.detected:
            # Full occlusion - use Kalman prediction
            if kalman_prediction is not None:
                confidence = max(0.0, 1.0 - (state.occlusion_duration / 30.0))
                return kalman_prediction, confidence * 0.7  # Reduce confidence during occlusion
            else:
                return None, 0.0
        
        elif detection_quality.is_partial:
            # Partial detection - use with reduced confidence
            quality_score = detection_quality.get_quality_score()
            if quality_score >= self.partial_detection_threshold:
                # Partial detection is good enough
                return None, quality_score * 0.8  # Signal partial detection quality
            elif kalman_prediction is not None:
                # Partial detection too poor, use Kalman
                return kalman_prediction, quality_score * 0.6
            else:
                return None, quality_score * 0.5
        
        else:
            # Full detection - no occlusion handling needed
            return None, 1.0
    
    def add_to_history(self, marker_id: int, pose: Tuple[float, float, float]):
        """
        Add a detection to the history.
        
        Args:
            marker_id: ID of the marker
            pose: Detected pose (x, y, theta)
        """
        if marker_id not in self.occlusion_states:
            self.occlusion_states[marker_id] = OcclusionState(
                marker_id=marker_id,
                is_occluded=False
            )
        
        state = self.occlusion_states[marker_id]
        timestamp = time.time()
        
        # Add to history
        state.detection_history.append((pose[0], pose[1], pose[2], timestamp))
        
        # Keep only recent history
        if len(state.detection_history) > self.history_length:
            state.detection_history.pop(0)
        
        state.last_good_detection = pose
        state.last_detection_time = timestamp
    
    def estimate_from_history(self, marker_id: int) -> Optional[Tuple[float, float, float]]:
        """
        Estimate position based on detection history.
        
        Args:
            marker_id: ID of the marker
            
        Returns:
            Estimated pose or None if insufficient history
        """
        if marker_id not in self.occlusion_states:
            return None
        
        state = self.occlusion_states[marker_id]
        
        if len(state.detection_history) < 3:
            return state.last_good_detection
        
        # Use weighted average of recent detections
        recent_history = state.detection_history[-5:]
        weights = np.exp(np.linspace(-1, 0, len(recent_history)))
        weights /= weights.sum()
        
        x = sum(h[0] * w for h, w in zip(recent_history, weights))
        y = sum(h[1] * w for h, w in zip(recent_history, weights))
        
        # For angle, use circular mean
        angles = [h[2] for h in recent_history]
        sin_sum = sum(np.sin(a) * w for a, w in zip(angles, weights))
        cos_sum = sum(np.cos(a) * w for a, w in zip(angles, weights))
        theta = np.arctan2(sin_sum, cos_sum)
        
        return (x, y, theta)
    
    def get_occlusion_statistics(self) -> Dict[str, any]:
        """Get statistics about occlusion handling."""
        if not self.occlusion_states:
            return {
                'total_markers': 0,
                'occluded_markers': 0,
                'partial_detections': 0,
                'full_occlusions': 0
            }
        
        occluded = [s for s in self.occlusion_states.values() if s.is_occluded]
        
        return {
            'total_markers': len(self.occlusion_states),
            'occluded_markers': len(occluded),
            'partial_detections': sum(s.partial_detections for s in self.occlusion_states.values()),
            'full_occlusions': sum(s.full_occlusions for s in self.occlusion_states.values()),
            'avg_occlusion_duration': np.mean([s.occlusion_duration for s in occluded]) if occluded else 0.0
        }
    
    def reset_marker(self, marker_id: int):
        """Reset occlusion state for a marker."""
        if marker_id in self.occlusion_states:
            del self.occlusion_states[marker_id]


class ConfidenceFusion:
    """
    Fuses multiple estimates with different confidence levels.
    
    This class combines:
    - Direct detections
    - Kalman predictions
    - History-based estimates
    
    Using confidence-weighted averaging.
    """
    
    @staticmethod
    def fuse_estimates(estimates: List[Tuple[Tuple[float, float, float], float]]) -> Tuple[Tuple[float, float, float], float]:
        """
        Fuse multiple pose estimates with confidence weights.
        
        Args:
            estimates: List of ((x, y, theta), confidence) tuples
            
        Returns:
            Fused (pose, confidence) tuple
        """
        if not estimates:
            return ((0.0, 0.0, 0.0), 0.0)
        
        if len(estimates) == 1:
            return estimates[0]
        
        # Normalize confidence weights
        confidences = np.array([e[1] for e in estimates])
        if confidences.sum() == 0:
            return estimates[0]
        
        weights = confidences / confidences.sum()
        
        # Weighted average for x, y
        x = sum(e[0][0] * w for e, w in zip(estimates, weights))
        y = sum(e[0][1] * w for e, w in zip(estimates, weights))
        
        # Circular mean for theta
        angles = [e[0][2] for e in estimates]
        sin_sum = sum(np.sin(a) * w for a, w in zip(angles, weights))
        cos_sum = sum(np.cos(a) * w for a, w in zip(angles, weights))
        theta = np.arctan2(sin_sum, cos_sum)
        
        # Combined confidence (weighted average)
        fused_confidence = float(np.average(confidences, weights=weights))
        
        return ((x, y, theta), fused_confidence)
