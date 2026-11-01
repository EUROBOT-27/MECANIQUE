"""Task Models and Utility Calculation

Defines all task types with their utility calculation logic based on
Eurobot 2026 official scoring rules.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
from abc import ABC, abstractmethod
import numpy as np

from .world_state import WorldState, CrateInfo, CrateOwnership, CrateContainer
from .config import StrategyConfig


class TaskType(Enum):
    """Types of tasks the robot can execute."""
    PLACE_HAZELNUT_IN_NEST = "place_hazelnut_in_nest"
    PLACE_HAZELNUT_IN_PANTRY = "place_hazelnut_in_pantry"
    FLIP_ENEMY_CRATE_IN_PANTRY = "flip_enemy_crate_in_pantry"
    FLIP_AND_PLACE_IN_PANTRY = "flip_and_place_in_pantry"  # Flip free enemy crate and place in pantry
    EMPTY_OPPONENT_FRIDGE = "empty_opponent_fridge"
    FILL_FRIDGE_WITH_EMPTY = "fill_fridge_with_empty"
    REACH_CURSOR_ZONE = "reach_cursor_zone"
    RETURN_TO_NEST = "return_to_nest"  # Endgame positioning


class ActionType(Enum):
    """Action required at destination."""
    PICKUP = "pickup"  # Pick up a crate
    PLACE = "place"  # Place a crate
    FLIP = "flip"  # Flip/empty a crate
    NONE = "none"  # Just navigate


@dataclass
class Task(ABC):
    """Base class for all tasks."""
    
    task_id: str  # Unique identifier
    task_type: TaskType
    target_position: Tuple[float, float]  # (x, y) destination
    action: ActionType  # What to do at destination
    
    # Utility components (computed)
    expected_score: float = 0.0
    feasibility: float = 0.0  # 0.0 = impossible, 1.0 = fully feasible
    safety_factor: float = 0.0  # 0.0 = very dangerous, 1.0 = safe
    time_cost: float = 0.0  # Estimated time in seconds
    distance_cost: float = 0.0  # Path length in meters
    
    # Final utility
    utility: float = 0.0
    
    # Path (computed by strategy manager)
    path: Optional[List[np.ndarray]] = None
    
    # Metadata
    description: str = ""
    associated_crate: Optional['CrateInfo'] = None
    
    # Perpendicular approach visualization data (for crates)
    perpendicular_point1: Optional[np.ndarray] = None
    perpendicular_point2: Optional[np.ndarray] = None
    chosen_approach_point: Optional[np.ndarray] = None
    
    @abstractmethod
    def compute_expected_score(self, world_state: WorldState, config: StrategyConfig) -> float:
        """Compute expected score based on official rules."""
        pass
    
    @abstractmethod
    def is_feasible(self, world_state: WorldState, config: StrategyConfig) -> bool:
        """Check if task is currently feasible."""
        pass
    
    def compute_utility(
        self,
        world_state: WorldState,
        config: StrategyConfig,
        path: Optional[List[np.ndarray]] = None
    ) -> float:
        """
        Compute utility score for this task.
        
        Formula:
            utility = (expected_score * weight_score * feasibility * safety)
                    / (time_cost * weight_time + distance_cost * weight_dist + epsilon)
        """
        epsilon = 0.01  # Prevent division by zero
        
        # Check feasibility first
        if not self.is_feasible(world_state, config):
            self.feasibility = 0.0
            self.utility = 0.0
            return 0.0
        
        self.feasibility = 1.0
        
        # Compute expected score
        self.expected_score = self.compute_expected_score(world_state, config)
        
        # Compute distance and time costs
        if path is not None and len(path) > 1:
            self.path = path
            self.distance_cost = self._compute_path_length(path)
            self.time_cost = self._estimate_time(path, config)
        else:
            # Estimate using straight-line distance
            robot_pos = np.array([world_state.robot_pose.x, world_state.robot_pose.y])
            target_pos = np.array(self.target_position)
            self.distance_cost = np.linalg.norm(target_pos - robot_pos)
            self.time_cost = self.distance_cost / config.robot_linear_speed
        
        # Add action time
        self.time_cost += self._get_action_time(config)
        
        # Compute safety factor
        if path is not None:
            risk = world_state.compute_enemy_proximity_risk(
                path, config.enemy_danger_radius
            )
            self.safety_factor = 1.0 - risk
        else:
            self.safety_factor = 1.0  # Unknown, assume safe
        
        # Apply safety threshold
        if self.safety_factor < config.min_safety_threshold:
            self.feasibility = 0.0
            self.utility = 0.0
            return 0.0
        
        # Compute final utility
        numerator = (
            self.expected_score
            * config.weight_expected_score
            * self.feasibility
            * self.safety_factor
        )
        
        denominator = (
            self.time_cost * config.weight_time_cost
            + self.distance_cost * config.weight_distance_cost
            + epsilon
        )
        
        self.utility = numerator / denominator
        
        # Endgame boost
        if world_state.is_in_endgame(config.endgame_threshold):
            if self.task_type == TaskType.RETURN_TO_NEST:
                self.utility *= config.endgame_urgency_multiplier
        
        return self.utility
    
    def _compute_path_length(self, path: List[np.ndarray]) -> float:
        """Compute total path length."""
        if len(path) < 2:
            return 0.0
        
        length = 0.0
        for i in range(len(path) - 1):
            p1 = path[i][:2]
            p2 = path[i + 1][:2]
            length += np.linalg.norm(p2 - p1)
        
        return length
    
    def _estimate_time(self, path: List[np.ndarray], config: StrategyConfig) -> float:
        """Estimate time to execute path."""
        # Simple model: distance / speed
        distance = self._compute_path_length(path)
        return distance / config.robot_linear_speed
    
    def _get_action_time(self, config: StrategyConfig) -> float:
        """Get time required for action at destination."""
        if self.action == ActionType.PICKUP:
            return config.time_pickup_crate
        elif self.action == ActionType.PLACE:
            return config.time_place_crate
        elif self.action == ActionType.FLIP:
            return config.time_flip_crate
        return 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for debugging."""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type.value,
            'action': self.action.value,
            'target': self.target_position,
            'expected_score': self.expected_score,
            'feasibility': self.feasibility,
            'safety_factor': self.safety_factor,
            'time_cost': self.time_cost,
            'distance_cost': self.distance_cost,
            'utility': self.utility,
            'description': self.description,
        }


# ============================================================================
# TASK IMPLEMENTATIONS
# ============================================================================

@dataclass
class PlaceHazelnutInNest(Task):
    """Task: Pick up our hazelnut crate and place in nest."""
    
    def __post_init__(self):
        if not self.description:
            crate_id = self.associated_crate.unique_id if self.associated_crate else "?"
            self.description = f"Place hazelnut crate {crate_id} in nest"
    
    def compute_expected_score(self, world_state: WorldState, config: StrategyConfig) -> float:
        """2 points per hazelnut crate in nest."""
        return config.score_hazelnut_in_nest
    
    def is_feasible(self, world_state: WorldState, config: StrategyConfig) -> bool:
        """Feasible if we have a free hazelnut crate and robot is not carrying."""
        if self.associated_crate is None:
            return False
        
        # Check crate is still free
        if self.associated_crate.container != CrateContainer.FREE:
            return False
        
        # Check robot is not already carrying
        if world_state.robot_pose is None:
            return False
        
        return True


@dataclass
class PlaceHazelnutInPantry(Task):
    """Task: Pick up our hazelnut crate and place in pantry."""
    
    pantry_name: str = ""
    
    def __post_init__(self):
        if not self.description:
            crate_id = self.associated_crate.unique_id if self.associated_crate else "?"
            self.description = f"Place hazelnut crate {crate_id} in {self.pantry_name}"
    
    def compute_expected_score(self, world_state: WorldState, config: StrategyConfig) -> float:
        """3 points per valid hazelnut in pantry."""
        return config.score_hazelnut_in_pantry
    
    def is_feasible(self, world_state: WorldState, config: StrategyConfig) -> bool:
        """Feasible if we have a free hazelnut crate and pantry is not full."""
        if self.associated_crate is None:
            return False
        
        # Check crate is still free
        if self.associated_crate.container != CrateContainer.FREE:
            return False
        
        return True


@dataclass
class FlipEnemyCrateInPantry(Task):
    """Task: Flip enemy hazelnut crate in pantry to convert to our points.
    
    Each crate has 2 ArUco markers (ID 36 blue, ID 47 yellow).
    Flipping converts opponent's 3pts to our 3pts = 6pt swing.
    """
    associated_crate: Optional[CrateInfo] = None
    pantry_name: Optional[str] = None
    
    def __post_init__(self):
        if not self.description:
            pantry = self.pantry_name or "pantry"
            crate_id = self.associated_crate.unique_id if self.associated_crate else "?"
            self.description = f"Flip enemy crate {crate_id} in {pantry}"
    
    def compute_expected_score(self, world_state: WorldState, config: StrategyConfig) -> float:
        """
        6 points total:
        - Deny opponent 3 points (they lose the crate)
        - Gain 3 points for us (we score it)
        """
        return config.score_hazelnut_in_pantry * 2  # 3pts * 2 = 6pts
    
    def is_feasible(self, world_state: WorldState, config: StrategyConfig) -> bool:
        """Feasible if enemy crate is still in pantry."""
        if self.associated_crate is None:
            return False
        
        # Check crate is still in pantry and belongs to opponent
        if self.associated_crate.container != CrateContainer.PANTRY:
            return False
        
        if self.associated_crate.ownership != CrateOwnership.OPPONENT:
            return False
        
        return True


@dataclass
class FlipAndPlaceInPantry(Task):
    """Task: Pick up free enemy crate, flip it, and place in pantry.
    
    Our mechanism can flip and place simultaneously. This task combines:
    - Picking up a free enemy crate
    - Flipping it to make it ours
    - Placing it in the nearest available pantry
    
    Score: 3 points (our crate in pantry)
    """
    associated_crate: Optional[CrateInfo] = None
    pantry_name: Optional[str] = None
    
    def __post_init__(self):
        if not self.description:
            pantry = self.pantry_name or "pantry"
            crate_id = self.associated_crate.unique_id if self.associated_crate else "?"
            self.description = f"Flip & place enemy crate {crate_id} in {pantry}"
    
    def compute_expected_score(self, world_state: WorldState, config: StrategyConfig) -> float:
        """
        3 points for placing our hazelnut in pantry.
        (Enemy loses nothing since crate was free, we gain 3pts)
        """
        return config.score_hazelnut_in_pantry
    
    def is_feasible(self, world_state: WorldState, config: StrategyConfig) -> bool:
        """Feasible if enemy crate is free (not in any container)."""
        if self.associated_crate is None:
            return False
        
        # Check crate is free (not in pantry/nest/fridge)
        if self.associated_crate.container != CrateContainer.FREE:
            return False
        
        # Check crate belongs to opponent
        if self.associated_crate.ownership != CrateOwnership.OPPONENT:
            return False
        
        return True


@dataclass
class EmptyOpponentFridge(Task):
    """Task: Flip/empty opponent's hazelnut crates in their fridge."""
    
    def __post_init__(self):
        if not self.description:
            self.description = "Empty opponent fridge"
    
    def compute_expected_score(self, world_state: WorldState, config: StrategyConfig) -> float:
        """
        2 points if opponent fridge is empty of hazelnuts at end.
        This is probabilistic - we score points only at game end.
        """
        return config.score_fridge_empty_of_hazelnut
    
    def is_feasible(self, world_state: WorldState, config: StrategyConfig) -> bool:
        """Feasible if opponent has hazelnut crates in fridge."""
        opponent_fridge_crates = world_state.get_opponent_fridge_hazelnut_crates()
        return len(opponent_fridge_crates) > 0


@dataclass
class FillFridgeWithEmpty(Task):
    """Task: Fill our fridge with empty crates."""
    
    def __post_init__(self):
        if not self.description:
            crate_id = self.associated_crate.unique_id if self.associated_crate else "?"
            self.description = f"Place empty crate {crate_id} in fridge"
    
    def compute_expected_score(self, world_state: WorldState, config: StrategyConfig) -> float:
        """5 points if fridge is full of empty crates at end."""
        # This is probabilistic - assuming fridge capacity is 5
        return config.score_fridge_full_of_empty / 5.0  # 1 point per crate
    
    def is_feasible(self, world_state: WorldState, config: StrategyConfig) -> bool:
        """Feasible if we have a free crate."""
        if self.associated_crate is None:
            return False
        
        # Check crate is still free
        if self.associated_crate.container != CrateContainer.FREE:
            return False
        
        # TODO: Check if fridge is full (would need fridge capacity tracking)
        
        return True


@dataclass
class ReachCursorZone(Task):
    """Task: Navigate to cursor scoring zone."""
    
    def __post_init__(self):
        if not self.description:
            self.description = "Reach cursor zone"
    
    def compute_expected_score(self, world_state: WorldState, config: StrategyConfig) -> float:
        """0-6 points depending on cursor position (simplified to 3 average)."""
        # Simplified: average score
        return (config.score_cursor_zone_min + config.score_cursor_zone_max) / 2.0
    
    def is_feasible(self, world_state: WorldState, config: StrategyConfig) -> bool:
        """Always feasible unless already completed."""
        # Check if already reached
        task_completed = "cursor_zone" in world_state.tasks_completed
        return not task_completed


@dataclass
class ReturnToNest(Task):
    """Task: Return to our starting zone for endgame positioning."""
    
    fully_inside: bool = False  # Whether targeting full or partial
    
    def __post_init__(self):
        if not self.description:
            zone_type = "fully" if self.fully_inside else "partially"
            self.description = f"Return to nest ({zone_type})"
    
    def compute_expected_score(self, world_state: WorldState, config: StrategyConfig) -> float:
        """5 points partial, 10 points if fully inside. Only relevant in last 25% of game."""
        # Only score in last quarter of game (25 seconds remaining out of 100)
        if world_state.time_remaining > 25.0:
            return 0.0  # Completely irrelevant in first 3/4 of game
        
        if self.fully_inside:
            return config.score_endgame_full
        else:
            return config.score_endgame_partial
    
    def is_feasible(self, world_state: WorldState, config: StrategyConfig) -> bool:
        """Always feasible, but priority increases in endgame."""
        return True
