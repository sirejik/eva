import logging

from eva.lib.settings import LOG_FILE_NAME, ROBOT_NAME
from eva.lib.utils import configure_logging

logger = logging.getLogger()


def run(action):
    configure_logging()
    try:
        logger.info('{name} started to work.'.format(name=ROBOT_NAME))
        action()
        logger.info('{name} finished work successfully.'.format(name=ROBOT_NAME))
        return 0
    except SystemExit as e:
        logger.info('{name} finished work with the exit code {exit_code}.'.format(name=ROBOT_NAME, exit_code=e.code))
        return e.code
    except Exception as e:
        logger.debug('An unexpected error occurred: %s' % str(e), **{'exc_info': 1})
        logger.error('An unexpected error occurred. See the details in the log file "%s".' % LOG_FILE_NAME)
        logger.info('{name} unexpectedly finished work.'.format(name=ROBOT_NAME))
        return 1


def follow_sensor():
    from eva.robots.follower import Follower

    robot = Follower()
    robot.run()


def trolley():
    from eva.robots.trolley import Trolley

    robot = Trolley()
    robot.run()


def trolley_tuner():
    from eva.tuner.trolley_tuner import TrolleyTuner

    robot = TrolleyTuner()
    robot.tune()


def trolley_tuner_on_track():
    from eva.tuner.trolley_tuner_on_track import TrolleyTunerOnTrack

    robot = TrolleyTunerOnTrack()
    robot.tune()


def tune_motion():
    from eva.tuner.tank_tuner import TankTuner

    tuner = TankTuner()
    tuner.tune()


def tune_infrared_sensor():
    from eva.tuner.ir_tuner import InfraredTuner

    tuner = InfraredTuner()
    tuner.tune()


def tune_reflected_intensity():
    from eva.tuner.color_tuner import ColorTuner

    tuner = ColorTuner()
    tuner.tune()


def stop():
    from eva.modules.tank import TankBase

    robot = TankBase()
    robot.stop()


def square_movement():
    import math

    from eva.robots.traveler import Traveler
    from eva.lib.command import MovementCommand, RotationCommand

    robot = Traveler([
        MovementCommand(0.5),
        RotationCommand(math.pi / 2.0),
        MovementCommand(0.5),
        RotationCommand(math.pi / 2.0),
        MovementCommand(0.5),
        RotationCommand(math.pi / 2.0),
        MovementCommand(0.5),
        RotationCommand(math.pi / 2.0)
    ])
    robot.run()
