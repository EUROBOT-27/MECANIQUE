"""Configuration for Strategy System

All tunable weights, constants, and parameters for the utility-based
task selection system are defined here for easy adjustment.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class StrategyConfig:
    """Configuration for strategy system - all tunable parameters."""
    
    # ========================================================================
    # FIELD GEOMETRY (from existing modules)
    # ========================================================================
    field_width: float = 3.0  # meters
    field_length: float = 2.0  # meters
    field_bounds: tuple = (0.0, 3.0, 0.0, 2.0)  # (xmin, xmax, ymin, ymax)
    
    robot_radius: float = 0.22  # meters - robot footprint
    crate_size: float = 0.05  # meters - crate marker size
    
    # ========================================================================
    # SCORING RULES (EUROBOT 2026 OFFICIAL - DO NOT MODIFY)
    # ========================================================================
    score_hazelnut_in_nest: float = 2.0  # points per hazelnut crate in nest
    score_hazelnut_in_pantry: float = 3.0  # points per valid hazelnut in pantry
    score_bonus_zone: float = 5.0  # points for reaching bonus zone
    score_fridge_empty_of_hazelnut: float = 2.0  # points if fridge has no hazelnuts at end
    score_fridge_full_of_empty: float = 5.0  # points if fridge full of empty crates at end
    score_cursor_zone_min: float = 0.0  # minimum cursor zone points
    score_cursor_zone_max: float = 6.0  # maximum cursor zone points
    score_endgame_partial: float = 5.0  # points if robot partially in own area
    score_endgame_full: float = 10.0  # points if robot fully in own area (5 + 5 bonus)
    
    # ========================================================================
    # UTILITY CALCULATION WEIGHTS
    # ========================================================================
    # Base weights for utility components
    weight_expected_score: float = 1.5  # Weight for expected score (increased to prioritize high-value tasks)
    weight_time_cost: float = 0.5  # Weight for time cost (higher = prefer fast tasks)
    weight_distance_cost: float = 0.3  # Weight for distance cost
    weight_safety: float = 0.8  # Weight for safety factor
    
    # Safety parameters
    enemy_danger_radius: float = 0.5  # meters - radius around enemy considered dangerous
    enemy_critical_radius: float = 0.3  # meters - very dangerous zone
    safety_penalty_per_meter: float = 0.2  # Safety reduction per meter inside danger zone
    
    # ========================================================================
    # ENDGAME TIMING
    # ========================================================================
    game_duration: float = 100.0  # seconds - total game time
    endgame_threshold: float = 33.0  # seconds - last third of game (67s elapsed, 33s remaining)
    endgame_urgency_multiplier: float = 5.0  # Multiplier for endgame task utilities (score-heavy)
    
    # ========================================================================
    # PATH PLANNING PARAMETERS
    # ========================================================================
    path_planning_timeout: float = 1.0  # seconds - max time for path planning
    path_planning_max_iter: int = 2000  # max iterations for RRT
    path_planning_step_size: float = 0.5  # meters - RRT step size
    
    # Speed estimation for time cost calculation
    robot_linear_speed: float = 0.3  # m/s - average robot speed
    robot_rotation_speed: float = 1.0  # rad/s - average rotation speed
    
    # Crate manipulation time estimates
    time_pickup_crate: float = 3.0  # seconds to pick up a crate
    time_place_crate: float = 2.0  # seconds to place a crate
    time_flip_crate: float = 4.0  # seconds to flip a crate (empty opponent fridge)
    
    # Robot capacity constraints
    robot_max_capacity: int = 6  # Maximum crates robot can carry
    robot_flip_capacity: int = 4  # Maximum crates robot can flip in one trip
    capacity_planning_horizon: float = 20.0  # meters - distance threshold for capacity planning
    capacity_clustering_distance: float = 1.0  # meters - crates within this distance are "close"
    
    # Robotic arm reach parameters
    arm_reach_distance: float = 0.07  # meters - robot stops this far from crate to pick it up
    pantry_placement_distance: float = 0.15  # meters - robot stops this far from pantry center to place
    
    # Destination zone matching
    destination_zone_tolerance: float = 0.1  # meters - tolerance for matching destination to pantry/fridge
    
    # ========================================================================
    # TASK FEASIBILITY THRESHOLDS
    # ========================================================================
    min_safety_threshold: float = 0.3  # Tasks below this safety are infeasible
    max_path_length: float = 10.0  # meters - paths longer than this are infeasible
    max_task_time: float = 30.0  # seconds - tasks taking longer are infeasible
    
    # ========================================================================
    # ZONE DEFINITIONS (world coordinates)
    # ========================================================================
    # Nest zones (scoring areas)
    nest_blue: tuple = (0.0, 0.6, 0.0, 0.4)  # (xmin, xmax, ymin, ymax)
    nest_yellow: tuple = (2.4, 3.0, 0.0, 0.40)
    
    # Pantry zones (from crate_obstacle_manager.py)
    pantry_zones: Dict[str, tuple] = None  # Will be initialized in __post_init__
    pantry_capacity: int = 4  # Maximum crates per pantry
    pantry_detection_tolerance: float = 0.2# meters - inflate pantry boundaries for detection (5cm)
    
    # Cursor zone (placeholder - adjust based on actual field design)
    cursor_zone: tuple = (1.4, 1.6, 0.9, 1.1)  # Center of field
    
    # Endgame area (own starting zone)
    endgame_blue: tuple = (0.0, 0.6, 0.0, 2.0)  # Blue team starting area
    endgame_yellow: tuple = (2.4, 3.0, 0.0, 2.0)  # Yellow team starting area
    
    # Fridge locations (placeholder - adjust based on actual positions)
    fridge_blue: tuple = (0.2, 0.4, 0.8, 1.0)
    fridge_yellow: tuple = (2.6, 2.8, 1.0, 1.2)
    
    # Forbidden zone (no waypoints allowed)
    forbidden_zone: tuple = (0.6, 2.4, 0.0, 0.4)  # (xmin, xmax, ymin, ymax) - horizontal strip at field bottom
    forbidden_zone_buffer: float = 0.1  # meters - additional safety margin around forbidden zone
    
    def __post_init__(self):
        """Initialize derived parameters."""
        if self.pantry_zones is None:
            # From crate_obstacle_manager.py PANTRIES_WORLD
            self.pantry_zones = {
                'pantry1': (1.150,1.350, 0.450, 0.650),
                'pantry2': (1.650, 1.850, 0.450, 0.650),
                'pantry3': (1.400, 1.600, 1.100, 1.300),
                'pantry4': (2.100, 2.300, 1.100, 1.300),
                'pantry5': (0.700, 0.900, 1.100, 1.300),
                'pantry6': (2.800, 3.000, 1.100, 1.300),
                'pantry7': (0.000, 0.200, 1.100, 1.300),
            }
    
    # ========================================================================
    # TUNING HELPERS
    # ========================================================================
    
    def increase_safety_priority(self, factor: float = 1.5):
        """Make the robot more cautious (increase safety weight)."""
        self.weight_safety *= factor
    
    def increase_speed_priority(self, factor: float = 1.5):
        """Make the robot prefer faster tasks."""
        self.weight_time_cost *= factor
    
    def set_aggressive_mode(self):
        """Configure for aggressive play (lower safety, higher speed)."""
        self.weight_safety = 0.4
        self.weight_time_cost = 1.0
        self.enemy_danger_radius = 0.3
    
    def set_defensive_mode(self):
        """Configure for defensive play (higher safety, careful)."""
        self.weight_safety = 1.5
        self.weight_time_cost = 0.3
        self.enemy_danger_radius = 0.7


# Default global configuration instance
DEFAULT_CONFIG = StrategyConfig()
