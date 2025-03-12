import yaml
from argparse import Namespace

import numpy as np

from weap_util.abstract_controller import AbstractController
from waypoint_follow import PurePursuitPlanner, nearest_point_on_trajectory

class Controller(AbstractController):
    def startup(self):
        """
        Initialize the controller:
         - Load configuration parameters from the YAML file.
         - Instantiate the planner (PurePursuitPlanner) with the configuration and wheelbase.
         - Set work parameters (e.g., lookahead distance and speed gain).
        """
        # Load the configuration. (Ensure the config file contains required fields such as:
        # wpt_path, wpt_delim, wpt_rowskip, wpt_xind, wpt_yind, wpt_vind, and optionally tlad, vgain.)
        config_file = "config_example_map.yaml"
        with open(config_file, "r") as f:
            config_dict = yaml.safe_load(f)
        self.config = Namespace(**config_dict)
        
        # Instantiate the planner.
        # For example, the wheelbase is computed as the sum of two example values.
        self.planner = PurePursuitPlanner(self.config, (0.17145 + 0.15875))
        
        # Define additional parameters (lookahead distance and velocity gain).
        self.work = {
            'tlad': self.config.tlad if hasattr(self.config, 'tlad') else 0.8,
            'vgain': self.config.vgain if hasattr(self.config, 'vgain') else 1.0
        }
        print("Controller: Startup complete.")

    def compute(self, obs: dict):
        """
        Compute the actuation commands based on the current observation.

        Parameters:
            obs (dict): Observation from the environment.
                        Expected keys: 'poses_x', 'poses_y', 'poses_theta' (each an array)

        Returns:
            speed (float): Desired speed command.
            steer (float): Desired steering command.
            current_waypoints (np.ndarray): A 2D array (8x3) where each row contains [x, y, speed]
                                            for rendering purposes.
        """
        # Extract the vehicle's pose (assuming a single agent).
        pose_x = obs['poses_x'][0]
        pose_y = obs['poses_y'][0]
        pose_theta = obs['poses_theta'][0]
        
        # Compute actuation using the planner's plan method.
        speed, steer = self.planner.plan(pose_x, pose_y, pose_theta,
                                         self.work['tlad'], self.work['vgain'])
        
        # For rendering, compute eight consecutive waypoints.
        # Build a 2D array (Nx2) from the full waypoint array using indices for x and y.
        wpts = np.vstack((
            self.planner.waypoints[:, self.config.wpt_xind],
            self.planner.waypoints[:, self.config.wpt_yind]
        )).T
        
        # Find the nearest point index on the trajectory.
        _, _, _, i = nearest_point_on_trajectory(np.array([pose_x, pose_y]), wpts)
        
        # Extract a window of 16 waypoints (wrap around if needed).
        num_total = self.planner.waypoints.shape[0]
        indices = [(i + j) % num_total for j in range(16)]
        window_waypoints = []
        for idx in indices:
            x = self.planner.waypoints[idx, self.config.wpt_xind]
            y = self.planner.waypoints[idx, self.config.wpt_yind]
            v_val = self.planner.waypoints[idx, self.config.wpt_vind]
            window_waypoints.append([x, y, v_val])
        window_waypoints = np.array(window_waypoints)
        
        return speed, steer, window_waypoints

    def shutdown(self):
        pass