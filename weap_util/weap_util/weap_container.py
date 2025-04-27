import os
import time
import yaml
from argparse import Namespace

import gym
import numpy as np
from PIL import Image, ImageOps
from pyglet.gl import GL_POINTS, glPointSize
from f110_gym.envs.base_classes import Integrator

from weap_util.abstract_controller import AbstractController

# todo: disable kill on collision

# Global variable to store the current set of waypoints for rendering
current_waypoints_global = None

# Global list to store drawn waypoint objects for later clearing
rendered_waypoints = []

_cam_follow_car = True

def _render_callback(env_renderer):
    """
    Custom render callback that updates the camera and renders waypoints.
    Uses the global current_waypoints_global variable for drawing.
    """
    global rendered_waypoints
    e = env_renderer
    
    if _cam_follow_car:
        # Update camera to follow the car
        x = e.cars[0].vertices[::2]
        y = e.cars[0].vertices[1::2]
        top, bottom, left, right = max(y), min(y), min(x), max(x)
        e.score_label.x = left
        e.score_label.y = top - 300

        e.left = left - 400
        e.right = right + 400
        e.top = top + 400
        e.bottom = bottom - 400

    # Clear previously drawn waypoints
    for obj in rendered_waypoints:
        obj.delete()
    rendered_waypoints = []

    # Render new waypoints using the global current_waypoints_global
    if current_waypoints_global is not None and current_waypoints_global.shape[0] > 0:
        points = current_waypoints_global[:, :2]
        scaled_points = 50 * points  # Scale factor for visualization
        glPointSize(5)  # Increase point size for clarity
        for i in range(len(points)):
            obj = e.batch.add(
                1,
                GL_POINTS,
                None,
                ('v3f/stream', [scaled_points[i, 0], scaled_points[i, 1], 0.0]),
                ('c3B/stream', [255, 0, 0])
            )
            rendered_waypoints.append(obj)
    # print("Render callback: waypoints drawn.")

def run(model: AbstractController, config_path: str, config_name: str = None, render_on=True, invert_image=False, cam_follow_car=True, kill_on_collision=True):
    """
    If config_name is provided then config_path is interpreted as the directory in which
    the config file lives. The final file name is built by appending either .yaml or .csv
    (with a default to .yaml if neither exists) to config_name. Then, we pass this file path
    to the map_path, set map_ext to .png, and override sx, sy, and stheta to 0.
    
    If config_name is None then config_path is treated as the full path to the YAML file.
    """
    global _cam_follow_car 
    _cam_follow_car = cam_follow_car

    # Monkey-patch PIL.Image.open so that it only returns the red channel (i.e. a single-channel image)
    _orig_open = Image.open
    if invert_image:
        Image.open = lambda *args, **kwargs: ImageOps.invert(_orig_open(*args, **kwargs).convert("RGB").split()[0])
    else:
        Image.open = lambda *args, **kwargs: _orig_open(*args, **kwargs).convert("RGB").split()[0]

    global current_waypoints_global

    if config_name is not None:
        # Use the provided config_path as the full path to the YAML file.
        full_config_path = config_path+".yaml"
        with open(full_config_path) as file:
            conf_dict = yaml.safe_load(file)
        conf = Namespace(**conf_dict)
    else:
        # Override the config settings.
        conf = Namespace(
            map_path=config_path,
            map_ext='.png',
            sx=0,
            sy=0,
            stheta=0 # 1.57079633 for up which is pi/2
        )

    # Create the environment.
    env = gym.make('f110_gym:f110-v0',
                   map=conf.map_path,
                   map_ext=conf.map_ext,
                   sx=conf.sx,
                   sy=conf.sy,
                   stheta=conf.stheta,
                   num_agents=1,
                   timestep=0.01,
                   integrator=Integrator.RK4,
                   done_on_collide=kill_on_collision)
    
    model.startup()

    # Reset environment and get initial observation.
    obs, step_reward, done, info = env.reset(np.array([[conf.sx, conf.sy, conf.stheta]]))

    if render_on:
        print("Registering render callback...")
        env.add_render_callback(_render_callback)
        env.render(mode='human')

    laptime = 0.0
    start = time.time()

    # put the image open back to what it is supposed to be
    Image.open = _orig_open

    # Main simulation loop.
    while not done:
        result = model.compute(obs)
        speed, steer = result[:2]
        current_waypoints = result[2] if len(result) >= 3 else None
        # Update the global variable for rendering.
        current_waypoints_global = current_waypoints
        obs, step_reward, done, info = env.step(np.array([[steer, speed]]))
        laptime += step_reward
        if render_on:
            env.render(mode='human')

    print('Sim elapsed time:', laptime, 'Real elapsed time:', time.time() - start)

if __name__ == '__main__':
    run(render_on=True)
