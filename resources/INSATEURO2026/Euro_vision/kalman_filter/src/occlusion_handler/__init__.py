"""
Occlusion Handler module for managing partially occluded ArUco markers.

This module provides strategies for dealing with marker occlusion including:
- Partial marker detection
- Prediction during occlusion
- Confidence scoring
- Multi-strategy fusion
"""

from .handler import OcclusionHandler, OcclusionStrategy, DetectionQuality, OcclusionState, ConfidenceFusion

__all__ = ['OcclusionHandler', 'OcclusionStrategy', 'DetectionQuality', 'OcclusionState', 'ConfidenceFusion']
