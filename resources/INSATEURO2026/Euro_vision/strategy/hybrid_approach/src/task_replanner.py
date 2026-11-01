"""
Task Replanner - Enemy-Aware Dynamic Task Switching

This module monitors enemy robot positions and velocities using Kalman filtering
to determine when tasks should be abandoned or reprioritized based on enemy
proximity and predicted trajectories.

Key Features:
- Kalman filter integration for enemy velocity estimation
- Predictive threat assessment (where enemy will be in N seconds)
- Task-specific threat zones (different radius per task type)
- Time-to-intercept calculations
- Confidence-based decision making

Author: Eurobot 2026 Vision Team
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path

# Import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config import StrategyConfig
from world_state import WorldState, EnemyInfo, RobotPose
from task_models import Task, TaskType

# Import Kalman filter (from existing module)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "kalman_filter"))
from src.kalman_filter.tracker import MultiMarkerTracker, MarkerState

# Import path planning utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "path_planning" / "utils"))
from rrt_connect import rrt_connect_plan
from path_smoothing import _line_segment_circle_collision


class ThreatLevel(Enum):
    """Threat assessment levels."""
    NONE = 0        # No threat
    LOW = 1         # Enemy distant, not approaching
    MODERATE = 2    # Enemy nearby or slowly approaching
    HIGH = 3        # Enemy close and approaching
    CRITICAL = 4    # Enemy very close, imminent collision


@dataclass
class TaskThreatAssessment:
    """Threat assessment for a specific task."""
    task_id: str
    task_type: TaskType
    task_position: Tuple[float, float]
    threat_level: ThreatLevel
    nearest_enemy_distance: float
    nearest_enemy_velocity: Optional[Tuple[float, float]]
    time_to_intercept: Optional[float]  # Seconds until enemy reaches task
    path_length: Optional[float]  # Actual path length to task (if calculated)
    path_is_clear: bool  # Whether a collision-free path exists
    should_abort: bool
    should_defer: bool  # Postpone but don't abandon
    reason: str


class TaskReplanner:
    """
    Monitors enemy threats and recommends task changes.
    
    Uses Kalman filter predictions to assess not just current enemy positions,
    but also their velocities and predicted future positions.
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize the task replanner.
        
        Args:
            config: Strategy configuration
        """
        self.config = config
        
        # Threat assessment parameters
        self.threat_zone_radius = {
            TaskType.PLACE_HAZELNUT_IN_NEST: 0.4,  # Nest tasks - moderate zone
            TaskType.PLACE_HAZELNUT_IN_PANTRY: 0.5,  # Pantry tasks - larger zone
            TaskType.FLIP_ENEMY_CRATE_IN_PANTRY: 0.6,  # Flipping - high risk
            TaskType.EMPTY_OPPONENT_FRIDGE: 0.7,  # Fridge - very high risk
            TaskType.RETURN_TO_NEST: 0.3,  # Return - lower zone (we're fleeing anyway)
        }
        
        # Time horizon for predictions
        self.prediction_horizon = 3.0  # seconds - how far ahead to predict
        
        # Decision thresholds
        self.abort_threshold_distance = 0.3  # meters - abort if enemy within this
        self.defer_threshold_distance = 0.6  # meters - defer if enemy within this
        self.approaching_speed_threshold = 0.1  # m/s - enemy approaching if velocity towards task > this
        
        # Tracking
        self.threat_history: Dict[str, List[TaskThreatAssessment]] = {}
        
        # Path planning parameters
        self.robot_radius = config.robot_radius
        self.use_path_planning = True  # Enable path-based threat assessment
        self.path_planning_max_iter = 1000  # Faster than full planning
        self.path_planning_step_size = config.path_planning_step_size
        
    def get_obstacles_for_planning(self, world_state: WorldState) -> List[Tuple[np.ndarray, float]]:
        """
        Convert world state obstacles into format for RRT planner.
        
        Args:
            world_state: Current world state with obstacles
        
        Returns:
            List of (center, radius) tuples for obstacles
        """
        obstacles = []
        
        # Add static obstacles
        for obstacle_center, obstacle_radius in world_state.static_obstacles:
            obstacles.append((obstacle_center[:2], obstacle_radius + self.robot_radius))
        
        # Add dynamic obstacles (enemies)
        for enemy in world_state.enemies:
            enemy_pos = np.array(enemy.position)
            # Use larger radius for enemies to account for uncertainty
            enemy_radius = self.threat_zone_radius.get(TaskType.RETURN_TO_NEST, 0.3)
            obstacles.append((enemy_pos, enemy_radius + self.robot_radius))
        
        return obstacles
    
    def plan_path_to_task(self, robot_pose: RobotPose, task_position: Tuple[float, float],
                         world_state: WorldState) -> Optional[List[np.ndarray]]:
        """
        Plan a path from robot's current position to a task location.
        
        Args:
            robot_pose: Current robot position
            task_position: Target task position
            world_state: Current world state with obstacles
        
        Returns:
            List of waypoints if path exists, None otherwise
        """
        start = np.array([robot_pose.x, robot_pose.y])
        goal = np.array(task_position)
        
        obstacles = self.get_obstacles_for_planning(world_state)
        
        # Use RRT-Connect for path planning
        path = rrt_connect_plan(
            start=start,
            goal=goal,
            obstacles=obstacles,
            bounds=self.config.field_bounds,
            max_iter=self.path_planning_max_iter,
            step_size=self.path_planning_step_size,
            goal_sample_rate=0.15
        )
        
        # Convert from [x,y,0] format to [x,y] format
        if path is not None:
            path = [np.array([p[0], p[1]]) for p in path]
        
        return path
    
    def calculate_path_length(self, path: List[np.ndarray]) -> float:
        """
        Calculate total length of a path.
        
        Args:
            path: List of waypoints
        
        Returns:
            Total path length in meters
        """
        if not path or len(path) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(path) - 1):
            segment_length = np.linalg.norm(path[i+1] - path[i])
            total_length += segment_length
        
        return total_length
        
    def estimate_enemy_velocity(self, enemy: EnemyInfo) -> np.ndarray:
        """
        Extract velocity from enemy info (from Kalman filter if available).
        
        Args:
            enemy: Enemy information
        
        Returns:
            (vx, vy) velocity vector
        """
        if enemy.velocity is not None:
            return np.array(enemy.velocity)
        else:
            # No velocity available - assume stationary
            return np.array([0.0, 0.0])
    
    def predict_enemy_position(self, enemy: EnemyInfo, 
                               time_ahead: float) -> np.ndarray:
        """
        Predict enemy position after a time interval.
        
        Args:
            enemy: Current enemy state
            time_ahead: Time in seconds to predict ahead
        
        Returns:
            Predicted (x, y) position
        """
        current_pos = np.array(enemy.position)
        velocity = self.estimate_enemy_velocity(enemy)
        
        predicted_pos = current_pos + velocity * time_ahead
        
        return predicted_pos
    
    def calculate_time_to_intercept(self, task_position: Tuple[float, float],
                                    enemy: EnemyInfo) -> Optional[float]:
        """
        Calculate time until enemy reaches task position.
        
        Args:
            task_position: (x, y) task location
            enemy: Enemy information
        
        Returns:
            Time in seconds, or None if enemy not approaching
        """
        enemy_pos = np.array(enemy.position)
        task_pos = np.array(task_position)
        velocity = self.estimate_enemy_velocity(enemy)
        
        speed = np.linalg.norm(velocity)
        
        if speed < 0.01:  # Stationary enemy
            return None
        
        # Vector from enemy to task
        to_task = task_pos - enemy_pos
        distance = np.linalg.norm(to_task)
        
        # Check if velocity is towards task (dot product > 0)
        velocity_normalized = velocity / speed
        to_task_normalized = to_task / distance
        
        dot_product = np.dot(velocity_normalized, to_task_normalized)
        
        if dot_product < 0.5:  # Enemy not really heading towards task
            return None
        
        # Estimate time to intercept
        time = distance / speed
        
        return time
    
    def assess_threat_to_task(self, task: Task, 
                              world_state: WorldState) -> TaskThreatAssessment:
        """
        Assess threat level for a specific task.
        
        Args:
            task: Task to assess
            world_state: Current world state with enemy positions
        
        Returns:
            TaskThreatAssessment with recommendation
        """
        task_pos = np.array(task.target_position)
        
        if not world_state.enemies:
            # No enemies detected - check if path exists
            path_to_task = None
            path_length = None
            path_is_clear = True
            
            if self.use_path_planning:
                path_to_task = self.plan_path_to_task(
                    world_state.robot_pose,
                    task.target_position,
                    world_state
                )
                if path_to_task is not None:
                    path_length = self.calculate_path_length(path_to_task)
                else:
                    path_is_clear = False
            
            return TaskThreatAssessment(
                task_id=task.task_id,
                task_type=task.task_type,
                task_position=task.target_position,
                threat_level=ThreatLevel.NONE if path_is_clear else ThreatLevel.LOW,
                nearest_enemy_distance=float('inf'),
                nearest_enemy_velocity=None,
                time_to_intercept=None,
                path_length=path_length,
                path_is_clear=path_is_clear,
                should_abort=not path_is_clear,
                should_defer=False,
                reason="No enemies detected" if path_is_clear else "No clear path to task"
            )
        
        # Find nearest enemy and assess threat
        min_distance = float('inf')
        nearest_enemy = None
        
        for enemy in world_state.enemies:
            enemy_pos = np.array(enemy.position)
            distance = np.linalg.norm(enemy_pos - task_pos)
            
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
        
        # Get threat zone radius for this task type
        threat_radius = self.threat_zone_radius.get(
            task.task_type, 
            0.5  # Default
        )
        
        # Calculate metrics
        enemy_velocity = self.estimate_enemy_velocity(nearest_enemy)
        enemy_speed = np.linalg.norm(enemy_velocity)
        time_to_intercept = self.calculate_time_to_intercept(
            task.target_position, 
            nearest_enemy
        )
        
        # Predict enemy position
        predicted_pos = self.predict_enemy_position(
            nearest_enemy, 
            self.prediction_horizon
        )
        predicted_distance = np.linalg.norm(predicted_pos - task_pos)
        
        # Assess threat level
        threat_level = ThreatLevel.NONE
        should_abort = False
        should_defer = False
        reason = "Clear"
        
        # Critical: Enemy very close
        if min_distance < self.abort_threshold_distance:
            threat_level = ThreatLevel.CRITICAL
            should_abort = True
            reason = f"Enemy within {self.abort_threshold_distance}m - ABORT"
        
        # High: Enemy close and approaching
        elif min_distance < threat_radius:
            if time_to_intercept is not None and time_to_intercept < 5.0:
                threat_level = ThreatLevel.HIGH
                should_defer = True
                reason = f"Enemy approaching (ETA: {time_to_intercept:.1f}s) - DEFER"
            else:
                threat_level = ThreatLevel.MODERATE
                reason = f"Enemy nearby ({min_distance:.2f}m) but not approaching"
        
        # Moderate: Enemy will be close soon
        elif predicted_distance < threat_radius:
            threat_level = ThreatLevel.MODERATE
            should_defer = True
            reason = f"Enemy predicted to be close in {self.prediction_horizon:.1f}s - DEFER"
        
        # Low: Enemy detected but distant
        elif min_distance < threat_radius * 2:
            threat_level = ThreatLevel.LOW
            reason = f"Enemy at safe distance ({min_distance:.2f}m)"
        
        # Check if enemy is moving fast towards task
        if time_to_intercept is not None and time_to_intercept < 3.0:
            if threat_level.value < ThreatLevel.HIGH.value:
                threat_level = ThreatLevel.HIGH
                should_defer = True
                reason = f"Fast enemy approach (ETA: {time_to_intercept:.1f}s) - DEFER"
        
        # Check path to task
        path_to_task = None
        path_length = None
        path_is_clear = True
        
        if self.use_path_planning and not should_abort:
            path_to_task = self.plan_path_to_task(
                world_state.robot_pose,
                task.target_position,
                world_state
            )
            if path_to_task is not None:
                path_length = self.calculate_path_length(path_to_task)
            else:
                path_is_clear = False
                should_abort = True
                reason = "No collision-free path to task location"
                threat_level = ThreatLevel.CRITICAL
        
        return TaskThreatAssessment(
            task_id=task.task_id,
            task_type=task.task_type,
            task_position=task.target_position,
            threat_level=threat_level,
            nearest_enemy_distance=min_distance,
            nearest_enemy_velocity=(enemy_velocity[0], enemy_velocity[1]),
            time_to_intercept=time_to_intercept,
            path_length=path_length,
            path_is_clear=path_is_clear,
            should_abort=should_abort,
            should_defer=should_defer,
            reason=reason
        )
    
    def assess_all_tasks(self, tasks: List[Task],
                        world_state: WorldState) -> Dict[str, TaskThreatAssessment]:
        """
        Assess threats to all tasks.
        
        Args:
            tasks: List of available tasks
            world_state: Current world state
        
        Returns:
            Dictionary mapping task_id to TaskThreatAssessment
        """
        assessments = {}
        
        for task in tasks:
            assessment = self.assess_threat_to_task(task, world_state)
            assessments[task.task_id] = assessment
            
            # Update history
            if task.task_id not in self.threat_history:
                self.threat_history[task.task_id] = []
            self.threat_history[task.task_id].append(assessment)
            
            # Keep only recent history (last 50 assessments)
            if len(self.threat_history[task.task_id]) > 50:
                self.threat_history[task.task_id] = self.threat_history[task.task_id][-50:]
        
        return assessments
    
    def recommend_task_switch(self, current_task: Task,
                             available_tasks: List[Task],
                             world_state: WorldState) -> Optional[Task]:
        """
        Recommend whether to switch from current task to another.
        
        Args:
            current_task: Currently executing task
            available_tasks: Other available tasks
            world_state: Current world state
        
        Returns:
            Recommended task to switch to, or None to continue current
        """
        # Assess current task
        current_assessment = self.assess_threat_to_task(current_task, world_state)
        
        # If current task should be aborted, find safer alternative
        if current_assessment.should_abort:
            # Filter safe tasks
            safe_tasks = []
            
            for task in available_tasks:
                if task.task_id == current_task.task_id:
                    continue
                
                assessment = self.assess_threat_to_task(task, world_state)
                
                if not assessment.should_abort and not assessment.should_defer:
                    safe_tasks.append((task, assessment))
            
            if safe_tasks:
                # Choose safest task (lowest threat level, farthest from enemies)
                safe_tasks.sort(
                    key=lambda x: (x[1].threat_level.value, -x[1].nearest_enemy_distance)
                )
                return safe_tasks[0][0]
            else:
                # No safe tasks - recommend return to nest or defensive position
                return None
        
        # If current task should be deferred, find better alternative
        elif current_assessment.should_defer:
            # Look for tasks with no threat
            clear_tasks = []
            
            for task in available_tasks:
                if task.task_id == current_task.task_id:
                    continue
                
                assessment = self.assess_threat_to_task(task, world_state)
                
                if assessment.threat_level == ThreatLevel.NONE:
                    clear_tasks.append((task, assessment))
            
            if clear_tasks:
                # Return highest priority clear task
                # (Assuming available_tasks is already sorted by priority)
                return clear_tasks[0][0]
        
        # Continue with current task
        return None
    
    def get_task_change_flag(self, current_task: Task,
                            world_state: WorldState) -> bool:
        """
        Get flag indicating whether current task should be changed.
        
        Args:
            current_task: Currently executing task
            world_state: Current world state
        
        Returns:
            True if task should be changed
        """
        assessment = self.assess_threat_to_task(current_task, world_state)
        return assessment.should_abort or assessment.should_defer
    
    def get_threat_report(self, tasks: List[Task],
                         world_state: WorldState) -> str:
        """
        Generate human-readable threat report.
        
        Args:
            tasks: List of tasks to assess
            world_state: Current world state
        
        Returns:
            Multi-line report string
        """
        assessments = self.assess_all_tasks(tasks, world_state)
        
        report_lines = ["=" * 70]
        report_lines.append("TASK THREAT ASSESSMENT REPORT")
        report_lines.append("=" * 70)
        report_lines.append(f"Enemies detected: {len(world_state.enemies)}")
        report_lines.append("")
        
        for task_id, assessment in sorted(assessments.items()):
            report_lines.append(f"Task: {task_id}")
            report_lines.append(f"  Type: {assessment.task_type.value}")
            report_lines.append(f"  Position: ({assessment.task_position[0]:.2f}, "
                              f"{assessment.task_position[1]:.2f})")
            report_lines.append(f"  Threat Level: {assessment.threat_level.name}")
            report_lines.append(f"  Nearest Enemy: {assessment.nearest_enemy_distance:.2f}m")
            
            if assessment.nearest_enemy_velocity:
                vx, vy = assessment.nearest_enemy_velocity
                speed = np.sqrt(vx**2 + vy**2)
                report_lines.append(f"  Enemy Velocity: ({vx:.2f}, {vy:.2f}) m/s "
                                  f"[Speed: {speed:.2f}]")
            
            if assessment.time_to_intercept:
                report_lines.append(f"  Time to Intercept: {assessment.time_to_intercept:.1f}s")
            
            if assessment.path_length is not None:
                report_lines.append(f"  Path Length: {assessment.path_length:.2f}m")
            
            if not assessment.path_is_clear:
                report_lines.append("  ❌ NO CLEAR PATH")
            
            if assessment.should_abort:
                report_lines.append("  ⚠️  RECOMMEND ABORT")
            elif assessment.should_defer:
                report_lines.append("  ⏸️  RECOMMEND DEFER")
            else:
                report_lines.append("  ✅ SAFE TO PROCEED")
            
            report_lines.append(f"  Reason: {assessment.reason}")
            report_lines.append("")
        
        report_lines.append("=" * 70)
        
        return "\n".join(report_lines)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    from config import DEFAULT_CONFIG
    from world_state import RobotPose
    from task_models import ActionType
    
    # Create mock world state with enemy
    world_state = WorldState(
        robot_pose=RobotPose(x=0.5, y=0.5, theta=0.0),
        enemies=[
            # Enemy approaching pantry1
            EnemyInfo(
                position=(1.0, 0.5),
                theta=0.0,
                velocity=(0.2, 0.05)  # Moving towards pantry1
            )
        ]
    )
    
    # Create mock tasks
    from task_models import Task
    
    task1 = Task(
        task_id="flip_pantry1",
        task_type=TaskType.FLIP_ENEMY_CRATE_IN_PANTRY,
        target_position=(1.25, 0.55),
        action=ActionType.FLIP,
        description="Flip crates in pantry1"
    )
    
    task2 = Task(
        task_id="place_pantry2",
        task_type=TaskType.PLACE_HAZELNUT_IN_PANTRY,
        target_position=(1.75, 0.55),
        action=ActionType.PLACE,
        description="Place hazelnut in pantry2"
    )
    
    # Initialize replanner
    replanner = TaskReplanner(DEFAULT_CONFIG)
    
    # Generate threat report
    print(replanner.get_threat_report([task1, task2], world_state))
    
    # Check if we should switch tasks
    alternative = replanner.recommend_task_switch(task1, [task2], world_state)
    
    if alternative:
        print(f"\n⚠️  Recommend switching to: {alternative.task_id}")
    else:
        print("\n✅ Continue with current task")
