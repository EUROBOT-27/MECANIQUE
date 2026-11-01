"""
Hybrid Strategy System - Package Initialization

This package implements a hybrid approach to robot strategy:
- Static field coordinates (pantries, nests) for reliability
- Dynamic computer vision perception for intelligent decisions

Main Components:
- CrateFlipManager: Vision-based flip count determination
- DynamicReturnToNest: Obstacle-avoiding path planning
- TaskReplanner: Enemy-aware task switching
- HybridSupervisor: Main coordination and decision-making

Author: Eurobot 2026 Vision Team
"""

from .crate_flip_manager import CrateFlipManager, PantryFlipDecision
from .dynamic_return_to_nest import DynamicReturnToNest, PathSegment
from .task_replanner import TaskReplanner, TaskThreatAssessment, ThreatLevel
from .hybrid_supervisor import HybridSupervisor, SupervisorCommand, SupervisorState

__all__ = [
    # Flip management
    'CrateFlipManager',
    'PantryFlipDecision',
    
    # Return to nest
    'DynamicReturnToNest',
    'PathSegment',
    
    # Task replanning
    'TaskReplanner',
    'TaskThreatAssessment',
    'ThreatLevel',
    
    # Main supervisor
    'HybridSupervisor',
    'SupervisorCommand',
    'SupervisorState',
]

__version__ = "1.0.0"
__author__ = "Eurobot 2026 Vision Team"
