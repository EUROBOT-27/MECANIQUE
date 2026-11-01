"""
Crate Flip Manager - Computer Vision-Based Flip Count Determination

This module uses real-time ArUco detection to determine how many crates
need to be flipped in each pantry based on actual visual observations,
replacing static hardcoded values with dynamic perception.

Key Features:
- Tracks crate ownership (blue vs yellow) per pantry
- Determines optimal flip count based on current pantry state
- Provides confidence metrics for each decision
- Integrates with existing crate tracking system

Author: Eurobot 2026 Vision Team
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Import shared utilities from package-relative paths
from strategy.utils.config import StrategyConfig
from strategy.utils.world_state import WorldState, CrateInfo, CrateOwnership, CrateContainer
from strategy.utils.crate_id_tracker import CrateIDTracker


@dataclass
class PantryFlipDecision:
    """Decision output for a single pantry."""
    pantry_id: str 
    current_enemy_crates: int
    current_our_crates: int
    recommended_flips: int
    # confidence attribute removed
    crate_ids: List[int]  # Unique IDs of crates to flip
    reason: str  # Human-readable explanation


class CrateFlipManager:
    """
    Manages crate flip decisions based on computer vision data.
    
    This replaces static flip strategies (e.g., "always flip first 2") 
    with dynamic decisions based on real-time pantry observations.
    """
    
    def __init__(self, config: StrategyConfig, team_color: str = "blue"):
        """
        Initialize the flip manager.
        
        Args:
            config: Strategy configuration with pantry zones
            team_color: Our team color ("blue" or "yellow")
        """
        self.config = config
        self.team_color = team_color.lower()
        
        # Determine our ownership type
        if self.team_color == "blue":
            self.our_ownership = CrateOwnership.OURS
            self.enemy_ownership = CrateOwnership.OPPONENT
        else:
            self.our_ownership = CrateOwnership.OPPONENT  # Inverted perspective
            self.enemy_ownership = CrateOwnership.OURS
        
        # Pantry analysis cache
        self.pantry_state_cache: Dict[str, PantryFlipDecision] = {}
        
    def is_point_in_pantry(self, position: Tuple[float, float], 
                           pantry_bounds: Tuple[float, float, float, float]) -> bool:
        """
        Check if a point is inside a pantry zone.
        
        Args:
            position: (x, y) world coordinates
            pantry_bounds: (xmin, xmax, ymin, ymax)
        
        Returns:
            True if point is inside pantry
        """
        x, y = position
        xmin, xmax, ymin, ymax = pantry_bounds
        return xmin <= x <= xmax and ymin <= y <= ymax
    
    def analyze_pantry(self, pantry_id: str, 
                       world_state: WorldState) -> PantryFlipDecision:
        """
        Analyze a single pantry and determine flip strategy.
        
        Args:
            pantry_id: Name of pantry (e.g., "pantry1")
            world_state: Current world state with crate detections
        
        Returns:
            PantryFlipDecision with recommended flip count
        """
        # Get pantry bounds from config
        if pantry_id not in self.config.pantry_zones:
            return PantryFlipDecision(
                pantry_id=pantry_id,
                current_enemy_crates=0,
                current_our_crates=0,
                recommended_flips=0,
                confidence=0.0,
                crate_ids=[],
                reason=f"Unknown pantry ID: {pantry_id}"
            )
        
        pantry_bounds = self.config.pantry_zones[pantry_id]
        
        # Filter crates in this pantry
        enemy_crates_in_pantry = []
        our_crates_in_pantry = []
        
        for crate in world_state.crates:
            # Check if crate is in pantry container OR physically in pantry zone
            in_pantry_zone = self.is_point_in_pantry(crate.position, pantry_bounds)
            is_in_pantry_container = crate.container == CrateContainer.PANTRY
            
            if in_pantry_zone or is_in_pantry_container:
                if crate.ownership == self.enemy_ownership:
                    enemy_crates_in_pantry.append(crate)
                elif crate.ownership == self.our_ownership:
                    our_crates_in_pantry.append(crate)
        
        # Determine flip strategy
        num_enemy = len(enemy_crates_in_pantry)
        num_ours = len(our_crates_in_pantry)
        
        # Decision logic
        if num_enemy == 0:
            # No enemy crates - nothing to flip
            recommended_flips = 0
            reason = "No enemy crates detected in pantry"
            crate_ids = []
        elif num_enemy <= 2:
            # Few enemy crates - flip all
            recommended_flips = num_enemy
            reason = f"Flip all {num_enemy} enemy crate(s)"
            crate_ids = [c.unique_id for c in enemy_crates_in_pantry]
        elif num_enemy == 3:
            # 3 enemy crates - prioritize based on position
            # Flip the ones closest to pantry center for easier access
            center_x = (pantry_bounds[0] + pantry_bounds[1]) / 2
            center_y = (pantry_bounds[2] + pantry_bounds[3]) / 2
            center = np.array([center_x, center_y])
            # Sort by distance to center
            sorted_crates = sorted(
                enemy_crates_in_pantry,
                key=lambda c: np.linalg.norm(np.array(c.position) - center)
            )
            recommended_flips = 3
            reason = "Flip 2 closest enemy crates (3 detected, prioritizing center)"
            crate_ids = [c.unique_id for c in sorted_crates[:2]]
        else:  # num_enemy >= 4
            # Pantry is full or nearly full of enemy crates
            # Flip first N based on robot capacity
            max_flips = min(self.config.robot_flip_capacity, num_enemy)
            # Prioritize by proximity to pantry entrance (lower Y coordinate)
            sorted_crates = sorted(
                enemy_crates_in_pantry,
                key=lambda c: c.position[1]  # Sort by Y (entrance is typically at lower Y)
            )
            recommended_flips = max_flips
            reason = f"Pantry full ({num_enemy} enemy crates), flip {max_flips} nearest to entrance"
            crate_ids = [c.unique_id for c in sorted_crates[:max_flips]]
        return PantryFlipDecision(
            pantry_id=pantry_id,
            current_enemy_crates=num_enemy,
            current_our_crates=num_ours,
            recommended_flips=recommended_flips,
            crate_ids=crate_ids,
            reason=reason
        )
    
    def analyze_all_pantries(self, world_state: WorldState) -> Dict[str, PantryFlipDecision]:
        """
        Analyze all pantries and generate flip decisions.
        
        Args:
            world_state: Current world state
        
        Returns:
            Dictionary mapping pantry_id to PantryFlipDecision
        """
        decisions = {}
        
        for pantry_id in self.config.pantry_zones.keys():
            decision = self.analyze_pantry(pantry_id, world_state)
            decisions[pantry_id] = decision
            
            # Update cache
            self.pantry_state_cache[pantry_id] = decision
        
        return decisions
    
    def get_flip_flag(self, pantry_id: str, world_state: WorldState) -> int:
        """
        Get the flip count flag for a specific pantry.
        This is the main interface for the supervisor to query flip decisions.
        
        Args:
            pantry_id: Pantry identifier
            world_state: Current world state
        
        Returns:
            Number of crates to flip (0 if none)
        """
        decision = self.analyze_pantry(pantry_id, world_state)
        return decision.recommended_flips
    
    def get_flip_targets(self, pantry_id: str, 
                        world_state: WorldState) -> List[int]:
        """
        Get specific crate IDs to flip in a pantry.
        
        Args:
            pantry_id: Pantry identifier
            world_state: Current world state
        
        Returns:
            List of unique crate IDs to flip
        """
        decision = self.analyze_pantry(pantry_id, world_state)
        return decision.crate_ids
    
    def get_summary_report(self) -> str:
        """
        Generate a human-readable summary of all pantry states.
        
        Returns:
            Multi-line summary string
        """
        if not self.pantry_state_cache:
            return "No pantry data available (run analyze_all_pantries first)"
        
        report_lines = ["=" * 70]
        report_lines.append("PANTRY FLIP ANALYSIS REPORT")
        report_lines.append("=" * 70)
        
        for pantry_id, decision in sorted(self.pantry_state_cache.items()):
            report_lines.append(f"\n{pantry_id.upper()}:")
            report_lines.append(f"  Enemy Crates: {decision.current_enemy_crates}")
            report_lines.append(f"  Our Crates:   {decision.current_our_crates}")
            report_lines.append(f"  Recommended Flips: {decision.recommended_flips}")
            # Confidence attribute removed from report
            report_lines.append(f"  Reason: {decision.reason}")
            
            if decision.crate_ids:
                report_lines.append(f"  Target IDs: {decision.crate_ids}")
        
        report_lines.append("\n" + "=" * 70)
        
        return "\n".join(report_lines)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    from utils.config import DEFAULT_CONFIG
    from utils.world_state import RobotPose
    
    # Create mock world state
    world_state = WorldState(
        robot_pose=RobotPose(x=0.5, y=0.5, theta=0.0),
        crates=[
            # Enemy crates in pantry1
            CrateInfo(
                unique_id=2001, aruco_id=47,
                position=(1.25, 0.55),
                ownership=CrateOwnership.OPPONENT,
                container=CrateContainer.PANTRY
            ),
            CrateInfo(
                unique_id=2002, aruco_id=47,
                position=(1.20, 0.58),
                ownership=CrateOwnership.OPPONENT,
                container=CrateContainer.PANTRY
            ),
            # Our crate in pantry2
            CrateInfo(
                unique_id=1001, aruco_id=36,
                position=(1.75, 0.55),
                ownership=CrateOwnership.OURS,
                container=CrateContainer.PANTRY
            ),
        ]
    )
    
    # Initialize manager
    flip_manager = CrateFlipManager(DEFAULT_CONFIG, team_color="blue")
    
    # Analyze all pantries
    decisions = flip_manager.analyze_all_pantries(world_state)
    
    # Print report
    print(flip_manager.get_summary_report())
    
    # Query specific pantry
    flip_count = flip_manager.get_flip_flag("pantry1", world_state)
    print(f"\nFlip flag for pantry1: {flip_count}")
