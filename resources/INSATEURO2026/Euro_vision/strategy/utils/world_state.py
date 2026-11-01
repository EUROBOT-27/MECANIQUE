"""World State Representation

Dataclasses for representing the current state of the world,
including crates, robot pose, enemy positions, and obstacles.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional, Dict
import numpy as np


class CrateOwnership(Enum):
    """Crate ownership."""
    OURS = "ours"
    OPPONENT = "opponent"
    UNKNOWN = "unknown"


class CrateContainer(Enum):
    """Where a crate is currently located."""
    FREE = "free"  # On field, available
    PANTRY = "pantry"  # In a pantry zone
    FRIDGE = "fridge"  # In a fridge
    NEST = "nest"  # In scoring nest
    ROBOT = "robot"  # Being carried by robot
    UNKNOWN = "unknown"



@dataclass
class CrateInfo:
    """Information about a single crate."""
    unique_id: int  # Unique instance ID (1001, 1002, ... for blue; 2001, 2002, ... for yellow)
    aruco_id: int  # ArUco marker ID (36=blue, 47=yellow)
    position: Tuple[float, float]  # (x, y) world coordinates
    ownership: CrateOwnership  # Whose crate is this
   
    container: CrateContainer  # Where it is currently
    
    # Optional metadata
    confidence: float = 1.0  # Detection confidence
    last_seen: float = 0.0  # Timestamp of last detection


@dataclass
class RobotPose:
    """Robot's current pose."""
    x: float  # meters
    y: float  # meters
    theta: float  # radians (orientation)
    timestamp: float = 0.0


@dataclass
class EnemyInfo:
    """Enemy robot information."""
    position: Tuple[float, float]  # (x, y) world coordinates
    theta: float  # orientation (radians)
    velocity: Optional[Tuple[float, float]] = None  # (vx, vy) if available
    confidence: float = 1.0
    last_seen: float = 0.0


@dataclass
class WorldState:
    """Complete world state for decision making."""
    
    # Robot state
    robot_pose: RobotPose
    
    # Crate information
    crates: List[CrateInfo] = field(default_factory=list)
    
    # Enemy information
    enemies: List[EnemyInfo] = field(default_factory=list)
    
    # Static obstacles (from crate obstacle manager + field boundaries)
    static_obstacles: List[Tuple[np.ndarray, float]] = field(default_factory=list)
    # Format: List of (center_position, radius) tuples
    
    # Dynamic obstacles (moving objects, temporary)
    dynamic_obstacles: List[Tuple[np.ndarray, float]] = field(default_factory=list)
    
    # Game state
    time_remaining: float = 100.0  # seconds until end
    match_phase: str = "main"  # "main" or "endgame"
    
    # Mission state
    tasks_completed: List[str] = field(default_factory=list)  # Task IDs already done
    current_task: Optional[str] = None  # Currently executing task ID
    
    # ========================================================================
    # QUERY METHODS
    # ========================================================================
    
    def get_crates_by_ownership(self, ownership: CrateOwnership) -> List[CrateInfo]:
        """Get all crates of a specific ownership."""
        return [c for c in self.crates if c.ownership == ownership]
    
    def get_crates_by_container(self, container: CrateContainer) -> List[CrateInfo]:
        """Get all crates in a specific container/location."""
        return [c for c in self.crates if c.container == container]
    
    def get_free_crates(self, ownership: CrateOwnership) -> List[CrateInfo]:
        """Get free crates of specific ownership."""
        return [
            c for c in self.crates
            if c.ownership == ownership
            and c.container == CrateContainer.FREE
        ]
    
    def get_opponent_fridge_hazelnut_crates(self) -> List[CrateInfo]:
        """Get opponent's crates in their fridge."""
        return [
            c for c in self.crates
            if c.ownership == CrateOwnership.OPPONENT
            and c.container == CrateContainer.FRIDGE
        ]
    
    def get_all_obstacles(self) -> List[Tuple[np.ndarray, float]]:
        """Get combined static and dynamic obstacles."""
        return self.static_obstacles + self.dynamic_obstacles
    
    def get_nearest_enemy(self, position: Tuple[float, float]) -> Optional[EnemyInfo]:
        """Get nearest enemy to a position."""
        if not self.enemies:
            return None
        
        pos = np.array(position)
        min_dist = float('inf')
        nearest = None
        
        for enemy in self.enemies:
            enemy_pos = np.array(enemy.position)
            dist = np.linalg.norm(pos - enemy_pos)
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
        
        return nearest
    
    def compute_enemy_proximity_risk(
        self,
        path: List[np.ndarray],
        danger_radius: float = 0.5
    ) -> float:
        """
        Compute risk score based on enemy proximity along a path.
        
        Returns:
            Risk score from 0.0 (safe) to 1.0 (very dangerous)
        """
        if not self.enemies or not path:
            return 0.0
        
        max_risk = 0.0
        
        for waypoint in path:
            for enemy in self.enemies:
                enemy_pos = np.array(enemy.position[:2])
                waypoint_pos = np.array(waypoint[:2])
                dist = np.linalg.norm(waypoint_pos - enemy_pos)
                
                if dist < danger_radius:
                    # Risk increases as we get closer
                    risk = 1.0 - (dist / danger_radius)
                    max_risk = max(max_risk, risk)
        
        return max_risk
    
    def is_in_endgame(self, threshold: float = 15.0) -> bool:
        """Check if we're in endgame phase."""
        return self.time_remaining <= threshold
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/debugging."""
        return {
            'robot_pose': {
                'x': self.robot_pose.x,
                'y': self.robot_pose.y,
                'theta': self.robot_pose.theta,
            },
            'num_crates': len(self.crates),
            'num_enemies': len(self.enemies),
            'time_remaining': self.time_remaining,
            'phase': self.match_phase,
            'current_task': self.current_task,
        }
