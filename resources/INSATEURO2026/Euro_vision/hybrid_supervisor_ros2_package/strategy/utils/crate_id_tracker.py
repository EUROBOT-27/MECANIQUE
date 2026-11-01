"""Crate ID Tracker - Assign unique IDs to crates with same ArUco markers

Problem:
- All blue crates have ArUco ID 36
- All yellow crates have ArUco ID 47
- This causes tracking issues when multiple crates move

Solution:
- Assign unique instance IDs (1001, 1002, ...) based on spatial position
- Track crates across frames using position proximity
- Handle crates entering/leaving field of view

Usage:
    tracker = CrateIDTracker()
    
    # For each detection frame:
    detections = [
        {'aruco_id': 36, 'pos': (0.5, 0.3, 0.0), 'ownership': 'ours'},
        {'aruco_id': 36, 'pos': (1.2, 0.8, 0.0), 'ownership': 'ours'},
        {'aruco_id': 47, 'pos': (2.1, 1.5, 0.0), 'ownership': 'opponent'},
    ]
    
    unique_crates = tracker.assign_unique_ids(detections)
    # Result:
    # [
    #   {'unique_id': 1001, 'aruco_id': 36, 'pos': (0.5, 0.3, 0.0), ...},
    #   {'unique_id': 1002, 'aruco_id': 36, 'pos': (1.2, 0.8, 0.0), ...},
    #   {'unique_id': 2001, 'aruco_id': 47, 'pos': (2.1, 1.5, 0.0), ...},
    # ]
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import time
from collections import defaultdict


# ID ranges for different crate types
BLUE_CRATE_ID_START = 1000  # Blue crates: 1001, 1002, 1003, ...
YELLOW_CRATE_ID_START = 2000  # Yellow crates: 2001, 2002, 2003, ...

# Matching parameters
POSITION_MATCH_THRESHOLD = 0.05  # meters - crates within this distance are same (increased for robustness)
CRATE_TIMEOUT = 2.0  # seconds - remove crates not seen for this long


class TrackedCrate:
    """Internal representation of a tracked crate."""
    
    def __init__(self, unique_id: int, aruco_id: int, position: Tuple[float, float, float],
                 ownership: str, container: str = 'free', confidence: float = 1.0):
        self.unique_id = unique_id
        self.aruco_id = aruco_id
        self.position = np.array(position[:2])  # Only use x, y for matching
        self.position_3d = position
        self.ownership = ownership
        self.container = container
        self.confidence = confidence
        self.last_seen = time.time()
        self.times_seen = 1
    
    def update(self, position: Tuple[float, float, float], 
               ownership: str, container: str = 'free', confidence: float = 1.0):
        """Update crate with new detection."""
        # Exponential moving average for position smoothing
        alpha = 0.4
        new_pos_2d = np.array(position[:2])
        self.position = alpha * new_pos_2d + (1 - alpha) * self.position
        self.position_3d = (self.position[0], self.position[1], position[2])
        self.ownership = ownership
        self.container = container
        self.confidence = confidence
        self.last_seen = time.time()
        self.times_seen += 1
    
    def distance_to(self, position: Tuple[float, float, float]) -> float:
        """Calculate 2D distance to a position."""
        pos_2d = np.array(position[:2])
        return np.linalg.norm(self.position - pos_2d)
    
    def is_stale(self, timeout: float = CRATE_TIMEOUT) -> bool:
        """Check if crate hasn't been seen recently."""
        return (time.time() - self.last_seen) > timeout
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'unique_id': self.unique_id,
            'aruco_id': self.aruco_id,
            'pos': self.position_3d,
            'ownership': self.ownership,
            'container': self.container,
            'confidence': self.confidence,
            'last_seen': self.last_seen,
            'times_seen': self.times_seen
        }


class CrateIDTracker:
    """Track crates across frames and assign unique IDs."""
    
    def __init__(self, 
                 position_threshold: float = POSITION_MATCH_THRESHOLD,
                 timeout: float = CRATE_TIMEOUT):
        """
        Initialize crate ID tracker.
        
        Args:
            position_threshold: Maximum distance (meters) to match crates between frames
            timeout: Time (seconds) before removing unseen crates
        """
        self.position_threshold = position_threshold
        self.timeout = timeout
        
        # Tracked crates by ArUco ID
        # Key: ArUco ID (36 or 47)
        # Value: List[TrackedCrate]
        self.tracked_crates: Dict[int, List[TrackedCrate]] = defaultdict(list)
        
        # Next ID counters for each ArUco type
        self.next_id = {
            36: BLUE_CRATE_ID_START + 1,  # Blue crates start at 1001
            47: YELLOW_CRATE_ID_START + 1  # Yellow crates start at 2001
        }
        
        # Statistics
        self.total_crates_tracked = 0
        self.frames_processed = 0
    
    def assign_unique_ids(self, detections: List[Dict]) -> List[Dict]:
        """
        Assign unique IDs to detected crates.
        
        Args:
            detections: List of detected crates with format:
                [
                    {
                        'id': 36,  # ArUco marker ID (or 'aruco_id')
                        'pos': (x, y, z),  # World coordinates
                        'ownership': 'ours' or 'opponent',
                        'container': 'free' or 'pantry' or 'fridge' or 'nest',
                        'confidence': 0.0-1.0
                    },
                    ...
                ]
        
        Returns:
            List of detections with unique_id added:
                [
                    {
                        'unique_id': 1001,
                        'aruco_id': 36,
                        'pos': (x, y, z),
                        'ownership': 'ours',
                        'container': 'free',
                        'confidence': 1.0
                    },
                    ...
                ]
        """
        self.frames_processed += 1
        
        # Remove stale crates
        self._remove_stale_crates()
        
        # Track which detections have been matched
        matched_detections = set()
        result = []
        
        # Process each detection
        for i, detection in enumerate(detections):
            # Extract aruco_id (handle both 'id' and 'aruco_id' keys)
            aruco_id = detection.get('aruco_id', detection.get('id'))
            
            # Skip if not a crate (reference markers, robot markers, etc.)
            if aruco_id not in [36, 47]:
                continue
            
            position = detection['pos']
            ownership = detection.get('ownership', 'unknown')
            container = detection.get('container', 'free')
            confidence = detection.get('confidence', 1.0)
            
            # Try to match with existing tracked crate
            matched_crate = self._find_matching_crate(aruco_id, position)
            
            if matched_crate is not None:
                # Update existing crate
                matched_crate.update(position, ownership, container, confidence)
                unique_id = matched_crate.unique_id
                # Debug: print when updating existing crate
                # print(f"[TRACKER] Matched ArUco {aruco_id} at {position[:2]} to existing ID {unique_id}")
            else:
                # Create new tracked crate
                unique_id = self.next_id[aruco_id]
                self.next_id[aruco_id] += 1
                
                new_crate = TrackedCrate(
                    unique_id=unique_id,
                    aruco_id=aruco_id,
                    position=position,
                    ownership=ownership,
                    container=container,
                    confidence=confidence
                )
                self.tracked_crates[aruco_id].append(new_crate)
                self.total_crates_tracked += 1
                print(f"[TRACKER] New crate detected! ArUco {aruco_id} at ({position[0]:.2f}, {position[1]:.2f}) -> Unique ID {unique_id}")
            
            # Add to result with unique ID
            result_entry = detection.copy()
            result_entry['unique_id'] = unique_id
            result_entry['aruco_id'] = aruco_id
            result.append(result_entry)
            matched_detections.add(i)
        
        return result
    
    def _find_matching_crate(self, aruco_id: int, position: Tuple[float, float, float]) -> Optional[TrackedCrate]:
        """
        Find tracked crate that matches this detection.
        
        Args:
            aruco_id: ArUco marker ID (36 or 47)
            position: 3D position (x, y, z)
        
        Returns:
            Matched TrackedCrate or None
        """
        if aruco_id not in self.tracked_crates:
            return None
        
        # Find closest crate of this type
        min_distance = float('inf')
        closest_crate = None
        
        for crate in self.tracked_crates[aruco_id]:
            dist = crate.distance_to(position)
            if dist < min_distance and dist < self.position_threshold:
                min_distance = dist
                closest_crate = crate
        
        return closest_crate
    
    def _remove_stale_crates(self):
        """Remove crates that haven't been seen recently."""
        for aruco_id in list(self.tracked_crates.keys()):
            self.tracked_crates[aruco_id] = [
                crate for crate in self.tracked_crates[aruco_id]
                if not crate.is_stale(self.timeout)
            ]
            
            # Clean up empty lists
            if not self.tracked_crates[aruco_id]:
                del self.tracked_crates[aruco_id]
    
    def get_all_tracked_crates(self) -> List[Dict]:
        """
        Get all currently tracked crates.
        
        Returns:
            List of all tracked crates with unique IDs
        """
        all_crates = []
        for crates_list in self.tracked_crates.values():
            for crate in crates_list:
                all_crates.append(crate.to_dict())
        return all_crates
    
    def get_crate_by_unique_id(self, unique_id: int) -> Optional[Dict]:
        """Get a specific crate by its unique ID."""
        for crates_list in self.tracked_crates.values():
            for crate in crates_list:
                if crate.unique_id == unique_id:
                    return crate.to_dict()
        return None
    
    def reset(self):
        """Reset the tracker (clear all tracked crates)."""
        self.tracked_crates.clear()
        self.next_id = {
            36: BLUE_CRATE_ID_START + 1,
            47: YELLOW_CRATE_ID_START + 1
        }
        self.total_crates_tracked = 0
        self.frames_processed = 0
    
    def get_stats(self) -> Dict:
        """Get tracking statistics."""
        active_blue = len(self.tracked_crates.get(36, []))
        active_yellow = len(self.tracked_crates.get(47, []))
        
        return {
            'frames_processed': self.frames_processed,
            'total_crates_tracked': self.total_crates_tracked,
            'active_blue_crates': active_blue,
            'active_yellow_crates': active_yellow,
            'next_blue_id': self.next_id[36],
            'next_yellow_id': self.next_id[47]
        }


# Convenience function for single-line usage
def assign_unique_crate_ids(detections: List[Dict], 
                            tracker: Optional[CrateIDTracker] = None) -> Tuple[List[Dict], CrateIDTracker]:
    """
    Convenience function to assign unique IDs to crates.
    
    Args:
        detections: List of detected crates
        tracker: Existing tracker instance (creates new if None)
    
    Returns:
        Tuple of (updated_detections, tracker_instance)
    """
    if tracker is None:
        tracker = CrateIDTracker()
    
    updated_detections = tracker.assign_unique_ids(detections)
    return updated_detections, tracker
