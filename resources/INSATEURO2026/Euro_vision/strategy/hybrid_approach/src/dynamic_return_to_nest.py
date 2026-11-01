"""
Dynamic Return to Nest - Obstacle-Avoiding Path Planning

This module handles dynamic pathfinding from any position back to the nest
with real-time obstacle avoidance for both enemies and static objects.

Key Features:
- RRT-based path planning with dynamic replanning
- Avoids enemy robots with safety margins
- Handles static obstacles from field configuration
- Provides smooth, executable paths for robot navigation
- Real-time replanning when obstacles move

Author: Eurobot 2026 Vision Team
"""

import numpy as np
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass
import sys
from pathlib import Path

# Import shared utilities
from utils.config import StrategyConfig
from utils.world_state import WorldState, EnemyInfo, RobotPose

# Import path planning utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "path_planning" / "utils"))
from rrt_connect import rrt_connect_plan
from path_smoothing import _line_segment_circle_collision


@dataclass
class PathSegment:
    """A segment of a planned path."""
    waypoints: List[np.ndarray]  # List of (x, y) waypoints
    total_distance: float
    estimated_time: float
    has_enemy_nearby: bool
    # confidence attribute removed


class DynamicReturnToNest:
    """
    Manages dynamic path planning for returning to nest with obstacle avoidance.
    
    This uses RRT (Rapidly-exploring Random Tree) for path planning with
    real-time replanning when obstacles (enemies or objects) are detected.
    """
    
    def __init__(self, config: StrategyConfig, team_color: str = "blue"):
        """
        Initialize the return-to-nest planner.
        
        Args:
            config: Strategy configuration
            team_color: Our team color ("blue" or "yellow")
        """
        self.config = config
        self.team_color = team_color.lower()
        
        # Determine nest zone based on team
        if self.team_color == "blue":
            self.nest_zone = self.config.nest_blue
        else:
            self.nest_zone = self.config.nest_yellow
        
        # Path planning parameters
        self.rrt_max_iterations = self.config.path_planning_max_iter
        self.rrt_step_size = self.config.path_planning_step_size
        self.robot_radius = self.config.robot_radius
        
        # Safety margins
        self.enemy_avoidance_radius = self.config.enemy_danger_radius
        self.static_obstacle_margin = 0.1  # meters
        
        # Current path cache
        self.current_path: Optional[PathSegment] = None
        self.path_generation_count = 0
        
    def get_nest_center(self) -> np.ndarray:
        """
        Get the center point of our nest zone.
        
        Returns:
            (x, y) center coordinates
        """
        xmin, xmax, ymin, ymax = self.nest_zone
        center_x = (xmin + xmax) / 2.0
        center_y = (ymin + ymax) / 2.0
        return np.array([center_x, center_y])
    
    def get_obstacles_for_planning(self, world_state: WorldState) -> List[Tuple[np.ndarray, float]]:
        """
        Convert world state obstacles into format for RRT planner.
        
        Args:
            world_state: Current world state with obstacles
        
        Returns:
            List of (center, radius) tuples for obstacles
        """
        obstacles = []
        
        # Add static obstacles with margin
        for obstacle_center, obstacle_radius in world_state.static_obstacles:
            expanded_radius = obstacle_radius + self.robot_radius + self.static_obstacle_margin
            obstacles.append((obstacle_center[:2], expanded_radius))
        
        # Add dynamic obstacles (enemies) with margin
        for enemy in world_state.enemies:
            enemy_pos = np.array(enemy.position)
            expanded_radius = self.enemy_avoidance_radius + self.robot_radius
            obstacles.append((enemy_pos, expanded_radius))
        
        return obstacles
    
    def rrt_path_planning(self, start: np.ndarray, goal: np.ndarray,
                         world_state: WorldState) -> Optional[List[np.ndarray]]:
        """
        Plan path using RRT-Connect algorithm from path_planning module.
        
        Args:
            start: Start position (x, y)
            goal: Goal position (x, y)
            world_state: Current world state with obstacles
        
        Returns:
            List of waypoints from start to goal (already smoothed), or None if no path found
        """
        # Convert obstacles to RRT planner format
        obstacles = self.get_obstacles_for_planning(world_state)
        
        # Call RRT-Connect planner (already includes smoothing)
        path = rrt_connect_plan(
            start=start,
            goal=goal,
            obstacles=obstacles,
            bounds=self.config.field_bounds,
            max_iter=self.rrt_max_iterations,
            step_size=self.rrt_step_size,
            goal_sample_rate=0.1
        )
        
        # Convert from [x,y,0] format to [x,y] format
        if path is not None:
            path = [np.array([p[0], p[1]]) for p in path]
        
        return path
    
    def calculate_path_metrics(self, path: List[np.ndarray],
                               world_state: WorldState) -> Tuple[float, float, bool]:
        """
        Calculate metrics for a path.
        
        Args:
            path: List of waypoints
            world_state: Current world state
        
        Returns:
            (total_distance, estimated_time, has_enemy_nearby)
        """
        total_distance = 0.0
        has_enemy_nearby = False
        
        for i in range(len(path) - 1):
            segment_length = np.linalg.norm(path[i+1] - path[i])
            total_distance += segment_length
            
            # Check for nearby enemies along segment
            for enemy in world_state.enemies:
                enemy_pos = np.array(enemy.position)
                # Check distance from enemy to segment midpoint
                midpoint = (path[i] + path[i+1]) / 2
                if np.linalg.norm(midpoint - enemy_pos) < self.enemy_avoidance_radius * 1.5:
                    has_enemy_nearby = True
        
        # Estimate time based on robot speed
        estimated_time = total_distance / self.config.robot_linear_speed
        
        # Add time penalty for turns (approximation)
        turn_time = (len(path) - 2) * 0.5  # 0.5s per waypoint for turning
        estimated_time += turn_time
        
        return total_distance, estimated_time, has_enemy_nearby
    
    def plan_return_to_nest(self, world_state: WorldState,
                           force_replan: bool = False) -> Optional[PathSegment]:
        """
        Plan a path from current robot position to nest.
        
        Args:
            world_state: Current world state
            force_replan: Force replanning even if current path exists
        
        Returns:
            PathSegment with waypoints, or None if planning failed
        """
        start_pos = np.array([world_state.robot_pose.x, world_state.robot_pose.y])
        goal_pos = self.get_nest_center()
        
        # Check if we need to replan
        needs_replan = force_replan or self.current_path is None
        
        # Check if current path is still valid (no new obstacles)
        if not needs_replan and self.current_path is not None:
            # Replan if path validation needed - use RRT obstacle checking
            obstacles = self.get_obstacles_for_planning(world_state)
            
            path_still_valid = True
            for i in range(len(self.current_path.waypoints) - 1):
                p1 = self.current_path.waypoints[i]
                p2 = self.current_path.waypoints[i+1]
                
                # Check collision with any obstacle
                for (center, radius) in obstacles:
                    if _line_segment_circle_collision(p1, p2, center, radius):
                        path_still_valid = False
                        needs_replan = True
                        break
                
                if not path_still_valid:
                    break
        
        if not needs_replan:
            return self.current_path
        
        # Plan new path using RRT-Connect (already smoothed)
        smoothed_path = self.rrt_path_planning(start_pos, goal_pos, world_state)
        
        if smoothed_path is None:
            print("[WARN] Return-to-nest path planning failed - no clear path found")
            return None
        
        # Calculate metrics
        distance, time, has_enemy = self.calculate_path_metrics(smoothed_path, world_state)
        
        # confidence attribute removed
        path_segment = PathSegment(
            waypoints=smoothed_path,
            total_distance=distance,
            estimated_time=time,
            has_enemy_nearby=has_enemy
        )
        
        self.current_path = path_segment
        self.path_generation_count += 1
        
        return path_segment
    
    def get_return_flag(self, world_state: WorldState) -> bool:
        """
        Get flag indicating whether return-to-nest path is available and clear.
        
        Args:
            world_state: Current world state
        
        Returns:
            True if safe path to nest exists
        """
        path = self.plan_return_to_nest(world_state)
        return path is not None
    
    def get_current_waypoint(self, world_state: WorldState) -> Optional[np.ndarray]:
        """
        Get the next waypoint to navigate to.
        
        Args:
            world_state: Current world state
        
        Returns:
            Next waypoint (x, y), or None if no path
        """
        if self.current_path is None or len(self.current_path.waypoints) < 2:
            return None
        
        # Find closest waypoint ahead of us
        robot_pos = np.array([world_state.robot_pose.x, world_state.robot_pose.y])
        
        min_distance_to_waypoint = 0.2  # meters - advance to next waypoint when this close
        
        for waypoint in self.current_path.waypoints[1:]:  # Skip start point
            if np.linalg.norm(waypoint - robot_pos) > min_distance_to_waypoint:
                return waypoint
        
        # All waypoints reached, return goal
        return self.current_path.waypoints[-1]


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    from config import DEFAULT_CONFIG
    from world_state import RobotPose
    
    # Create mock world state
    world_state = WorldState(
        robot_pose=RobotPose(x=2.0, y=1.0, theta=0.0),
        enemies=[
            EnemyInfo(position=(1.5, 0.8), theta=0.0, velocity=(0.1, 0.0))
        ]
    )
    
    # Initialize planner
    planner = DynamicReturnToNest(DEFAULT_CONFIG, team_color="blue")
    
    # Plan path
    path = planner.plan_return_to_nest(world_state)
    
    if path:
        print(f"Path found with {len(path.waypoints)} waypoints")
        print(f"Distance: {path.total_distance:.2f}m")
        print(f"Estimated time: {path.estimated_time:.1f}s")
        print(f"Enemy nearby: {path.has_enemy_nearby}")
        # Confidence attribute removed from output
        print("\nWaypoints:")
        for i, wp in enumerate(path.waypoints):
            print(f"  {i}: ({wp[0]:.3f}, {wp[1]:.3f})")
    else:
        print("No path found!")
