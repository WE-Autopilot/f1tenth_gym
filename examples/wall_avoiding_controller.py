"""
Pretty garbage ngl.
"""
import numpy as np

from weap_util.abstract_controller import AbstractController

class WallAvoidingController(AbstractController):
    def __init__(self):
        self.max_speed = 2.0  # Maximum forward speed
        self.min_speed = 0.2  # Minimum speed when avoiding walls
        self.max_steering = 1.0  # Maximum steering angle
        self.safety_distance = 1.0  # Minimum safe distance from walls

    def startup(self) -> None:
        print("Controller started")

    def compute(self, obs: dict) -> tuple[2 | 3]:
        scans = obs['scans'][0]
        if not scans.any():
            print('No scans!')
            return 0.0, 0.0, None  # Stop if no scan data is available
        
        # Convert scan distances to a NumPy array
        scan_array = np.array(scans)
        num_scans = len(scans)
        if num_scans < 3:
            return 0.0, 0.0, None  # Not enough data to make a decision

        left_scans = scan_array[:num_scans//3]  # Left side scans
        front_scans = scan_array[num_scans//3:2*num_scans//3]  # Front scans
        right_scans = scan_array[2*num_scans//3:]  # Right side scans

        # Ensure min calculations do not fail on empty slices
        left_min = np.min(left_scans) if left_scans.size > 0 else float('inf')
        front_min = np.min(front_scans) if front_scans.size > 0 else float('inf')
        right_min = np.min(right_scans) if right_scans.size > 0 else float('inf')

        speed = self.max_speed
        steering = 0.0
        
        if front_min < self.safety_distance:
            # speed = self.min_speed  # Slow down
            if left_min > right_min:
                steering = -self.max_steering  # Turn left
            else:
                steering = self.max_steering  # Turn right
        elif left_min < self.safety_distance:
            steering = self.max_steering  # Turn right to avoid left obstacle
        elif right_min < self.safety_distance:
            steering = -self.max_steering  # Turn left to avoid right obstacle
        
        return speed, steering, None

    def shutdown(self) -> None:
        print("Controller shutting down")

