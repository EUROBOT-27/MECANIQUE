"""
Hybrid Strategy Supervisor - Main Coordination Module

This is the central supervisor that integrates all hybrid strategy features:
1. Computer vision-based crate flip counting
2. Dynamic return-to-nest path planning with obstacle avoidance
3. Enemy-aware task replanning using Kalman filter predictions

The supervisor monitors the world state, makes high-level decisions, and
sends command flags to the robot (via ROS, serial, or other communication).

This is a MONITORING AND DECISION system, not a low-level controller.
It does not directly control motors or execute waypoints.

Author: Eurobot 2026 Vision Team
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import time
import sys
from pathlib import Path

# Import our hybrid strategy modules
from crate_flip_manager import CrateFlipManager, PantryFlipDecision
from dynamic_return_to_nest import DynamicReturnToNest, PathSegment
from task_replanner import TaskReplanner, TaskThreatAssessment, ThreatLevel

# Import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
from config import StrategyConfig, DEFAULT_CONFIG
from world_state import WorldState, CrateInfo, EnemyInfo, RobotPose
from world_state import CrateOwnership, CrateContainer
from task_models import Task, TaskType, ActionType
from crate_id_tracker import CrateIDTracker


class SupervisorState(Enum):
    """High-level supervisor states."""
    INITIALIZING = "initializing"
    MONITORING = "monitoring"
    TASK_EXECUTION = "task_execution"
    EMERGENCY_RETURN = "emergency_return"
    ENDGAME = "endgame"
    FINISHED = "finished"


@dataclass
class SupervisorCommand:
    """Command output from supervisor to robot."""
    command_type: str  # "CONTINUE", "SWITCH_TASK", "RETURN_TO_NEST", "ABORT"
    target_task_id: Optional[str]  # Task to execute
    flip_counts: Dict[str, int]  # Pantry ID -> number of crates to flip
    waypoint: Optional[Tuple[float, float]]  # Next navigation waypoint
    threat_level: str  # "NONE", "LOW", "MODERATE", "HIGH", "CRITICAL"
    confidence: float  # Overall decision confidence
    reason: str  # Human-readable explanation


class HybridSupervisor:
    """
    Main supervisor integrating hybrid strategy features.
    
    Responsibilities:
    - Monitor world state from computer vision
    - Assess threats using Kalman-filtered enemy tracking
    - Determine crate flip counts per pantry
    - Plan return-to-nest paths dynamically
    - Recommend task switches when necessary
    - Generate command flags for robot controller
    """
    
    def __init__(self, config: StrategyConfig = None, 
                 team_color: str = "blue",
                 enable_visualization: bool = True):
        """
        Initialize the hybrid supervisor.
        
        Args:
            config: Strategy configuration (uses DEFAULT_CONFIG if None)
            team_color: Our team color ("blue" or "yellow")
            enable_visualization: Enable real-time visualization
        """
        self.config = config or DEFAULT_CONFIG
        self.team_color = team_color.lower()
        self.enable_visualization = enable_visualization
        
        # Initialize hybrid strategy components
        self.flip_manager = CrateFlipManager(self.config, team_color)
        self.return_planner = DynamicReturnToNest(self.config, team_color)
        self.task_replanner = TaskReplanner(self.config)
        
        # Crate tracking
        self.crate_tracker = CrateIDTracker()
        
        # State management
        self.state = SupervisorState.INITIALIZING
        self.current_task: Optional[Task] = None
        self.available_tasks: List[Task] = []
        
        # Statistics
        self.decision_count = 0
        self.task_switches = 0
        self.emergency_returns = 0
        self.start_time = time.time()
        
        # Visualization
        self.viz_display = None
        
    def update_world_state(self, detections: Dict) -> WorldState:
        """
        Convert raw detections to WorldState object.
        
        Args:
            detections: Dictionary from vision system with:
                - 'robot': {'pos': (x, y), 'theta': float}
                - 'enemies': [{'id': int, 'pos': (x, y, z), 'theta': float, 'velocity': (vx, vy)}]
                - 'crates': [{'aruco_id': int, 'pos': (x, y, z), 'ownership': str}]
                - 'time_remaining': float
        
        Returns:
            WorldState object
        """
        # Extract robot pose
        robot_data = detections.get('robot', {'pos': (0.0, 0.0), 'theta': 0.0})
        robot_pose = RobotPose(
            x=robot_data['pos'][0],
            y=robot_data['pos'][1],
            theta=robot_data.get('theta', 0.0),
            timestamp=time.time()
        )
        
        # Extract enemies
        enemies = []
        for enemy_data in detections.get('enemies', []):
            enemy = EnemyInfo(
                position=(enemy_data['pos'][0], enemy_data['pos'][1]),
                theta=enemy_data.get('theta', 0.0),
                velocity=enemy_data.get('velocity'),
                confidence=enemy_data.get('confidence', 1.0),
                last_seen=time.time()
            )
            enemies.append(enemy)
        
        # Extract and track crates
        crate_detections = []
        for crate_data in detections.get('crates', []):
            crate_detections.append({
                'aruco_id': crate_data.get('aruco_id', crate_data.get('id')),
                'pos': crate_data['pos'],
                'ownership': crate_data.get('ownership', 'unknown'),
                'container': crate_data.get('container', 'free'),
                'confidence': crate_data.get('confidence', 1.0)
            })
        
        # Assign unique IDs to crates
        tracked_crates = self.crate_tracker.assign_unique_ids(crate_detections)
        
        # Convert to CrateInfo objects
        crates = []
        for crate_data in tracked_crates:
            ownership_map = {
                'ours': CrateOwnership.OURS,
                'opponent': CrateOwnership.OPPONENT,
                'unknown': CrateOwnership.UNKNOWN
            }
            container_map = {
                'free': CrateContainer.FREE,
                'pantry': CrateContainer.PANTRY,
                'fridge': CrateContainer.FRIDGE,
                'nest': CrateContainer.NEST,
                'robot': CrateContainer.ROBOT
            }
            
            crate = CrateInfo(
                unique_id=crate_data['unique_id'],
                aruco_id=crate_data['aruco_id'],
                position=(crate_data['pos'][0], crate_data['pos'][1]),
                ownership=ownership_map.get(crate_data['ownership'], CrateOwnership.UNKNOWN),
                container=container_map.get(crate_data['container'], CrateContainer.FREE),
                confidence=crate_data.get('confidence', 1.0),
                last_seen=time.time()
            )
            crates.append(crate)
        
        # Create world state
        world_state = WorldState(
            robot_pose=robot_pose,
            crates=crates,
            enemies=enemies,
            time_remaining=detections.get('time_remaining', 100.0)
        )
        
        return world_state
    
    def generate_command(self, world_state: WorldState) -> SupervisorCommand:
        """
        Main decision-making logic - generates command for robot.
        
        Args:
            world_state: Current world state
        
        Returns:
            SupervisorCommand with recommended actions
        """
        self.decision_count += 1
        
        # 1. Analyze pantries for flip counts
        flip_decisions = self.flip_manager.analyze_all_pantries(world_state)
        flip_counts = {
            pantry_id: decision.recommended_flips
            for pantry_id, decision in flip_decisions.items()
        }
        
        # 2. Check if we're in endgame
        if world_state.time_remaining < self.config.endgame_threshold:
            self.state = SupervisorState.ENDGAME
            
            # Plan return to nest
            return_path = self.return_planner.plan_return_to_nest(world_state)
            
            if return_path and return_path.confidence > 0.3:
                waypoint = self.return_planner.get_current_waypoint(world_state)
                
                return SupervisorCommand(
                    command_type="RETURN_TO_NEST",
                    target_task_id=None,
                    flip_counts=flip_counts,
                    waypoint=waypoint,
                    threat_level="MODERATE",
                    confidence=return_path.confidence,
                    reason=f"Endgame ({world_state.time_remaining:.0f}s remaining) - returning to nest"
                )
            else:
                return SupervisorCommand(
                    command_type="ABORT",
                    target_task_id=None,
                    flip_counts=flip_counts,
                    waypoint=None,
                    threat_level="HIGH",
                    confidence=0.2,
                    reason="Endgame - no clear path to nest"
                )
        
        # 3. If no current task, continue monitoring
        if self.current_task is None:
            return SupervisorCommand(
                command_type="CONTINUE",
                target_task_id=None,
                flip_counts=flip_counts,
                waypoint=None,
                threat_level="NONE",
                confidence=1.0,
                reason="No active task - awaiting task assignment"
            )
        
        # 4. Assess threat to current task
        threat_assessment = self.task_replanner.assess_threat_to_task(
            self.current_task, 
            world_state
        )
        
        # 5. Decide on action based on threat
        if threat_assessment.should_abort:
            # Critical threat - emergency return to nest
            self.state = SupervisorState.EMERGENCY_RETURN
            self.emergency_returns += 1
            
            return_path = self.return_planner.plan_return_to_nest(world_state, force_replan=True)
            
            if return_path:
                waypoint = self.return_planner.get_current_waypoint(world_state)
                
                return SupervisorCommand(
                    command_type="RETURN_TO_NEST",
                    target_task_id=None,
                    flip_counts=flip_counts,
                    waypoint=waypoint,
                    threat_level=threat_assessment.threat_level.name,
                    confidence=return_path.confidence,
                    reason=f"EMERGENCY: {threat_assessment.reason}"
                )
            else:
                return SupervisorCommand(
                    command_type="ABORT",
                    target_task_id=None,
                    flip_counts=flip_counts,
                    waypoint=None,
                    threat_level="CRITICAL",
                    confidence=0.1,
                    reason="EMERGENCY: No escape path available"
                )
        
        elif threat_assessment.should_defer:
            # Moderate threat - switch to safer task
            alternative_task = self.task_replanner.recommend_task_switch(
                self.current_task,
                self.available_tasks,
                world_state
            )
            
            if alternative_task:
                self.task_switches += 1
                self.current_task = alternative_task
                
                return SupervisorCommand(
                    command_type="SWITCH_TASK",
                    target_task_id=alternative_task.task_id,
                    flip_counts=flip_counts,
                    waypoint=(alternative_task.target_position[0], 
                             alternative_task.target_position[1]),
                    threat_level=threat_assessment.threat_level.name,
                    confidence=0.7,
                    reason=f"Switching task: {threat_assessment.reason}"
                )
            else:
                # No alternative - return to nest
                return_path = self.return_planner.plan_return_to_nest(world_state)
                waypoint = self.return_planner.get_current_waypoint(world_state) if return_path else None
                
                return SupervisorCommand(
                    command_type="RETURN_TO_NEST",
                    target_task_id=None,
                    flip_counts=flip_counts,
                    waypoint=waypoint,
                    threat_level=threat_assessment.threat_level.name,
                    confidence=return_path.confidence if return_path else 0.3,
                    reason=f"No safe alternative - returning: {threat_assessment.reason}"
                )
        
        else:
            # Safe to continue current task
            self.state = SupervisorState.TASK_EXECUTION
            
            return SupervisorCommand(
                command_type="CONTINUE",
                target_task_id=self.current_task.task_id,
                flip_counts=flip_counts,
                waypoint=(self.current_task.target_position[0],
                         self.current_task.target_position[1]),
                threat_level=threat_assessment.threat_level.name,
                confidence=0.9,
                reason=f"Proceeding with task: {threat_assessment.reason}"
            )
    
    def visualize_state(self, world_state: WorldState, 
                       command: SupervisorCommand,
                       frame: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Create visualization of supervisor state.
        
        Args:
            world_state: Current world state
            command: Current command
            frame: Optional camera frame to overlay on
        
        Returns:
            Visualization image
        """
        # Create display (800x600 for field visualization)
        if frame is not None:
            display = frame.copy()
        else:
            display = np.zeros((600, 800, 3), dtype=np.uint8)
        
        # Field visualization scale
        scale_x = 800 / self.config.field_width  # pixels per meter
        scale_y = 600 / self.config.field_length
        
        def world_to_pixel(x: float, y: float) -> Tuple[int, int]:
            """Convert world coordinates to pixel coordinates."""
            px = int(x * scale_x)
            py = int((self.config.field_length - y) * scale_y)  # Flip Y
            return (px, py)
        
        # Draw field boundary
        cv2.rectangle(display, (0, 0), (799, 599), (100, 100, 100), 2)
        
        # Draw pantry zones
        for pantry_id, (xmin, xmax, ymin, ymax) in self.config.pantry_zones.items():
            p1 = world_to_pixel(xmin, ymin)
            p2 = world_to_pixel(xmax, ymax)
            cv2.rectangle(display, p1, p2, (150, 100, 50), 1)
            
            # Show flip count
            if pantry_id in command.flip_counts:
                flip_count = command.flip_counts[pantry_id]
                if flip_count > 0:
                    center = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
                    cv2.putText(display, f"F:{flip_count}", center,
                              cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        # Draw nest zones
        for nest_name, (xmin, xmax, ymin, ymax) in [
            ("Blue Nest", self.config.nest_blue),
            ("Yellow Nest", self.config.nest_yellow)
        ]:
            p1 = world_to_pixel(xmin, ymin)
            p2 = world_to_pixel(xmax, ymax)
            color = (255, 100, 0) if "Blue" in nest_name else (0, 100, 255)
            cv2.rectangle(display, p1, p2, color, 2)
        
        # Draw robot
        robot_px = world_to_pixel(world_state.robot_pose.x, world_state.robot_pose.y)
        cv2.circle(display, robot_px, 15, (0, 255, 0), -1)
        cv2.circle(display, robot_px, 15, (255, 255, 255), 2)
        
        # Draw robot orientation
        theta = world_state.robot_pose.theta
        arrow_end = (
            int(robot_px[0] + 25 * np.cos(theta)),
            int(robot_px[1] - 25 * np.sin(theta))
        )
        cv2.arrowedLine(display, robot_px, arrow_end, (0, 255, 0), 2, tipLength=0.3)
        
        # Draw enemies with velocity arrows
        for enemy in world_state.enemies:
            enemy_px = world_to_pixel(enemy.position[0], enemy.position[1])
            cv2.circle(display, enemy_px, 12, (0, 0, 255), -1)
            cv2.circle(display, enemy_px, 12, (255, 255, 255), 2)
            
            # Draw velocity if available
            if enemy.velocity:
                vx, vy = enemy.velocity
                vel_scale = 100  # pixels per m/s
                vel_end = (
                    int(enemy_px[0] + vx * vel_scale),
                    int(enemy_px[1] - vy * vel_scale)
                )
                cv2.arrowedLine(display, enemy_px, vel_end, (255, 0, 0), 2, tipLength=0.4)
        
        # Draw crates
        for crate in world_state.crates:
            crate_px = world_to_pixel(crate.position[0], crate.position[1])
            color = (255, 150, 0) if crate.ownership == CrateOwnership.OURS else (0, 150, 255)
            cv2.circle(display, crate_px, 5, color, -1)
        
        # Draw current task target
        if self.current_task:
            task_px = world_to_pixel(
                self.current_task.target_position[0],
                self.current_task.target_position[1]
            )
            cv2.drawMarker(display, task_px, (255, 255, 0), 
                          cv2.MARKER_STAR, 20, 2)
        
        # Draw waypoint if available
        if command.waypoint:
            wp_px = world_to_pixel(command.waypoint[0], command.waypoint[1])
            cv2.circle(display, wp_px, 8, (0, 255, 255), -1)
        
        # Draw info panel
        info_y = 20
        line_height = 20
        
        # Supervisor state
        state_color = {
            SupervisorState.MONITORING: (0, 255, 0),
            SupervisorState.TASK_EXECUTION: (255, 255, 0),
            SupervisorState.EMERGENCY_RETURN: (0, 0, 255),
            SupervisorState.ENDGAME: (255, 165, 0)
        }.get(self.state, (255, 255, 255))
        
        cv2.putText(display, f"State: {self.state.value.upper()}", 
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, state_color, 2)
        info_y += line_height
        
        # Command
        cv2.putText(display, f"Command: {command.command_type}", 
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        info_y += line_height
        
        # Threat level
        threat_color = {
            "NONE": (0, 255, 0),
            "LOW": (0, 255, 255),
            "MODERATE": (0, 165, 255),
            "HIGH": (0, 100, 255),
            "CRITICAL": (0, 0, 255)
        }.get(command.threat_level, (255, 255, 255))
        
        cv2.putText(display, f"Threat: {command.threat_level}", 
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, threat_color, 1)
        info_y += line_height
        
        # Time remaining
        cv2.putText(display, f"Time: {world_state.time_remaining:.0f}s", 
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        info_y += line_height
        
        # Statistics
        cv2.putText(display, f"Decisions: {self.decision_count} | Switches: {self.task_switches}", 
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Reason (bottom of screen)
        cv2.putText(display, command.reason[:80], 
                   (10, 580), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        return display
    
    def run_supervision_cycle(self, detections: Dict,
                             camera_frame: Optional[np.ndarray] = None) -> SupervisorCommand:
        """
        Execute one supervision cycle.
        
        Args:
            detections: Raw detections from vision system
            camera_frame: Optional camera frame for visualization
        
        Returns:
            SupervisorCommand to send to robot
        """
        # Update world state
        world_state = self.update_world_state(detections)
        
        # Generate command
        command = self.generate_command(world_state)
        
        # Visualize if enabled
        if self.enable_visualization:
            self.viz_display = self.visualize_state(world_state, command, camera_frame)
            cv2.imshow("Hybrid Supervisor", self.viz_display)
            cv2.waitKey(1)
        
        return command
    
    def set_current_task(self, task: Task):
        """Set the current task being executed."""
        self.current_task = task
    
    def set_available_tasks(self, tasks: List[Task]):
        """Set the list of available tasks."""
        self.available_tasks = tasks
    
    def get_status_report(self) -> str:
        """Generate comprehensive status report."""
        elapsed = time.time() - self.start_time
        
        report = f"""
{'=' * 70}
HYBRID SUPERVISOR STATUS REPORT
{'=' * 70}
State: {self.state.value.upper()}
Elapsed Time: {elapsed:.1f}s
Decisions Made: {self.decision_count}
Task Switches: {self.task_switches}
Emergency Returns: {self.emergency_returns}

Current Task: {self.current_task.task_id if self.current_task else 'None'}

Flip Manager Status:
{self.flip_manager.get_summary_report()}

{'=' * 70}
        """
        return report


# ============================================================================
# EXAMPLE USAGE / DEMO
# ============================================================================

if __name__ == "__main__":
    print("Hybrid Supervisor - Demo Mode")
    print("=" * 70)
    
    # Initialize supervisor
    supervisor = HybridSupervisor(team_color="blue", enable_visualization=True)
    
    # Create mock task
    mock_task = Task(
        task_id="flip_pantry1",
        task_type=TaskType.FLIP_ENEMY_CRATE_IN_PANTRY,
        target_position=(1.25, 0.55),
        action=ActionType.FLIP,
        description="Flip crates in pantry1"
    )
    
    supervisor.set_current_task(mock_task)
    
    # Simulate detection data
    mock_detections = {
        'robot': {'pos': (0.5, 0.5), 'theta': 0.0},
        'enemies': [
            {'id': 13, 'pos': (1.5, 0.8, 0.0), 'theta': 0.0, 'velocity': (0.1, 0.05)}
        ],
        'crates': [
            {'aruco_id': 47, 'pos': (1.20, 0.55, 0.0), 'ownership': 'opponent'},
            {'aruco_id': 47, 'pos': (1.28, 0.58, 0.0), 'ownership': 'opponent'},
        ],
        'time_remaining': 85.0
    }
    
    # Run supervision cycle
    command = supervisor.run_supervision_cycle(mock_detections)
    
    # Print command
    print("\nGenerated Command:")
    print(f"  Type: {command.command_type}")
    print(f"  Target Task: {command.target_task_id}")
    print(f"  Flip Counts: {command.flip_counts}")
    print(f"  Waypoint: {command.waypoint}")
    print(f"  Threat Level: {command.threat_level}")
    print(f"  Confidence: {command.confidence:.1%}")
    print(f"  Reason: {command.reason}")
    
    print("\n" + supervisor.get_status_report())
    
    # Keep visualization open
    print("\nPress any key to exit...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
