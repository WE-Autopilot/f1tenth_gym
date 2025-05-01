# red_controller.py

import gym
# Monkey-patch Box to restore the .shape property (needed by SB3 replay buffer)
if not hasattr(gym.spaces.Box, "shape"):
    gym.spaces.Box.shape = property(lambda self: self._shape)

import os
import numpy as np
from weap_util.abstract_controller import AbstractModel
from stable_baselines3 import SAC

class Controller(AbstractModel):
    def __init__(self, model_path="f110_line_sensor_sac.zip"):
        super().__init__()
        self.model = None
        self.model_path = model_path

        self.sensor_angles = np.arange(-134.645, 134.645, 9.97370976287)
        self.max_range     = 10.0
        self.fov           = 4.7

        print(self.model_path)
        # Now SAC.load will find observation_space.shape correctly
        self.model = SAC.load(self.model_path)

    def startup(self):
        print("LOL")
        pass

    def init(self):
        pass

    def eval(self, obs, timestamp=0):
        # pull out the 1080-beam scan
        scan = obs["scans"][0]
        n    = len(scan)
        # interpolate down to your 27 angles
        scan_angles = np.linspace(-self.fov/2, self.fov/2, n)
        desired     = np.linspace(-self.fov/2, self.fov/2, len(self.sensor_angles))
        vals        = np.interp(desired, scan_angles, scan)
        vals        = np.clip(vals, 0.0, self.max_range)

        speed = obs["linear_vels_x"][0] / 4.0
        speed = float(np.clip(speed, 0.0, 1.0))

        obs_vec = np.concatenate([vals, [speed]]).astype(np.float32)
        action, _states = self.model.predict(obs_vec, deterministic=True)
        steer, throttle = action

        throttle = float(np.clip(throttle, 0.4, 2.0))
        return throttle*7, float(steer)

    def shutdown(self):
        pass
