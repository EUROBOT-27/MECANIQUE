"""Strategy Package - Utility-based Task Selection for Eurobot 2026

This package implements a utility-based decision-making system that selects
the best task to execute based on:
- Expected score (Eurobot 2026 official rules)
- Path feasibility and distance
- Enemy proximity and safety
- Time remaining until endgame

The system integrates with existing modules:
- Path planning (path_planning.rrt_connect)
- Crate obstacle management (full_pipeline.scripts.crate_obstacle_manager)
- ArUco detection (ros_ready_pipeline.aruco_id_detector)
"""

from .task_models import (
    Task,
    TaskType,
    ActionType,
    PlaceHazelnutInNest,
    PlaceHazelnutInPantry,
    EmptyOpponentFridge,
    FillFridgeWithEmpty,
    ReachCursorZone,
    ReturnToNest,
)
from .world_state import WorldState, CrateInfo, CrateOwnership, CrateContainer
from .config import StrategyConfig

__all__ = [
    "Task",
    "TaskType",
    "ActionType",
    "PlaceHazelnutInNest",
    "PlaceHazelnutInPantry",
    "EmptyOpponentFridge",
    "FillFridgeWithEmpty",
    "ReachCursorZone",
    "ReturnToNest",
    "WorldState",
    "CrateInfo",
    "CrateOwnership",
    "CrateContainer",
    "StrategyConfig",
]
