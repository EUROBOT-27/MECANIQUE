"""
Kalman Filter module for ArUco marker tracking in Eurobot 2026.

This module provides Kalman filtering for smoothing ArUco marker detections
and predicting positions during occlusion or frame drops.
"""

from .tracker import KalmanTracker, MultiMarkerTracker, MarkerType, MarkerState

__all__ = ['KalmanTracker', 'MultiMarkerTracker', 'MarkerType', 'MarkerState']
