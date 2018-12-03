"""
Script to drive a donkey 2 car.

Usage:
    drive.py [--model=model]

Options:
    -h --help        Show this screen.
    --model MODEL    Path to the model to use for your autopilot.
"""
import os
from docopt import docopt

import donkeycar as dk
from donkeypart_picamera import PiCamera
from donkeypart_keras_behavior_cloning import KerasLinear
from donkeypart_tub import TubWriter
from donkeypart_common import Timestamp

from donkeypart_bluetooth_game_controller import BluetoothGameController
from donkeypart_sombrero import Sombrero


def drive(cfg, model_path=None, use_chaos=False):
    """
    """

    V = dk.vehicle.Vehicle()

    clock = Timestamp()
    V.add(clock, outputs=['timestamp'])

    cam = PiCamera(resolution=cfg.CAMERA_RESOLUTION)
    V.add(cam, outputs=['cam/image_array'], threaded=True)

    ctl = BluetoothGameController()
    V.add(ctl,
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

    sombrero = Sombrero(
        steering_channel=cfg.STEERING_CHANNEL,
        steering_left_pwm=cfg.STEERING_LEFT_PWM,
        steering_right_pwm=cfg.STEERING_RIGHT_PWM,
        throttle_channel=cfg.THROTTLE_CHANNEL,
        throttle_forward_pwm=cfg.THROTTLE_FORWARD_PWM,
        throttle_stop_pwm=cfg.THROTTLE_STOPPED_PWM,
        throttle_reverse_pwm=cfg.THROTTLE_REVERSE_PWM
    )
    V.add(sombrero, inputs=['angle', 'throttle'])

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

    drive(cfg, model_path=args['--model'])





