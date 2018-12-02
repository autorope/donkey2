"""
Scripts to drive a donkey 2 car and train a model for it.

Usage:
    drive.py [--model=<model>]

Options:
    -h --help        Show this screen.
    --model          Path to the model to use for your autopilot.
"""
import os
from docopt import docopt

import donkeycar as dk
from donkeypart_picamera import PiCamera
from donkeypart_keras_behavior_cloning import KerasLinear
from donkeypart_PCA9685_actuators import PCA9685, PWMSteering, PWMThrottle
from donkeypart_tub import TubWriter
from donkeypart_web_controller import LocalWebController
from donkeypart_common import Timestamp


def drive(cfg, model_path=None, use_chaos=False):
    """
    """

    V = dk.vehicle.Vehicle()

    clock = Timestamp()
    V.add(clock, outputs=['timestamp'])

    cam = PiCamera(resolution=cfg.CAMERA_RESOLUTION)
    V.add(cam, outputs=['cam/image_array'], threaded=True)

    ctr = LocalWebController(use_chaos=use_chaos)
    V.add(ctr,
          inputs=['cam/image_array'],
          outputs=['user/angle', 'user/throttle', 'user/mode', 'recording'],
          threaded=True)

    # See if we should even run the pilot module.
    # This is only needed because the part run_condition only accepts boolean

    pilot_condition_part = MakeRunConditionBoolean()
    V.add(pilot_condition_part,
          inputs=['user/mode'],
          outputs=['run_pilot'])

    # Run the pilot if the mode is not user.
    kl = KerasLinear()
    if model_path:
        kl.load(model_path)

    V.add(kl,
          inputs=['cam/image_array'],
          outputs=['pilot/angle', 'pilot/throttle'],
          run_condition='run_pilot')

    state_controller = StateController()
    V.add(state_controller,
          inputs=['user/mode',
                  'user/angle', 'user/throttle',
                  'pilot/angle', 'pilot/throttle'],
          outputs=['angle', 'throttle'])

    steering_controller = PCA9685(cfg.STEERING_CHANNEL)
    steering = PWMSteering(controller=steering_controller,
                           left_pulse=cfg.STEERING_LEFT_PWM,
                           right_pulse=cfg.STEERING_RIGHT_PWM) 

    throttle_controller = PCA9685(cfg.THROTTLE_CHANNEL)
    throttle = PWMThrottle(controller=throttle_controller,
                           max_pulse=cfg.THROTTLE_FORWARD_PWM,
                           zero_pulse=cfg.THROTTLE_STOPPED_PWM,
                           min_pulse=cfg.THROTTLE_REVERSE_PWM)

    V.add(steering, inputs=['angle'])
    V.add(throttle, inputs=['throttle'])

    # add tub to save data
    inputs = ['cam/image_array', 'user/angle', 'user/throttle', 'user/mode', 'timestamp']
    types = ['image_array', 'float', 'float',  'str', 'str']

    # single tub
    tub = TubWriter(path=cfg.TUB_PATH, inputs=inputs, types=types)
    V.add(tub, inputs=inputs, run_condition='recording')

    # run the vehicle
    V.start(rate_hz=cfg.DRIVE_LOOP_HZ)



class MakeRunConditionBoolean:
    def run(self, mode):
        if mode == 'user':
            return False
        else:
            return True


class StateController:
    """
    Wraps a function into a donkey part.
    """

    def __init__(self):
        pass

    def run(self, mode,
            user_angle, user_throttle,
            pilot_angle, pilot_throttle):

        """
        Returns the angle, throttle and boolean if autopilot should be run.
        The angle and throttles returned are the ones given to the steering and
        throttle actuators.
        """

        if mode == 'user':
            return user_angle, user_throttle

        elif mode == 'local_angle':
            return pilot_angle, user_throttle

        else:
            return pilot_angle, pilot_throttle


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()

    if args['drive']:
        drive(cfg, model_path=args['--model'], use_chaos=args['--chaos'])





