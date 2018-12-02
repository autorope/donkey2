"""
CAR CONFIG

This file is read by your cars drive script to ensure repeatable configurations.

EXAMPLE
-----------
import dk
cfg = dk.load_config(config_path='~/mycar/config.py')
print(cfg.CAMERA_RESOLUTION)
"""

import os

#PATHS
CAR_PATH = PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
TUB_PATH = os.path.join(CAR_PATH, 'tub')

#VEHICLE
DRIVE_LOOP_HZ = 20

#CAMERA
CAMERA_RESOLUTION = (120, 160)  # (height, width)

#STEERING
STEERING_CHANNEL = 1
STEERING_LEFT_PWM = 420
STEERING_RIGHT_PWM = 360

#THROTTLE
THROTTLE_CHANNEL = 0
THROTTLE_FORWARD_PWM = 400
THROTTLE_STOPPED_PWM = 360
THROTTLE_REVERSE_PWM = 310

