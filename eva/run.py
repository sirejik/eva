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

    logger.info('{name} began to follow you.'.format(name=ROBOT_NAME))
    robot = Follower()
    robot.follow_sensor()
    logger.info('{name} found you.'.format(name=ROBOT_NAME))


def trolley():
    from eva.robots.trolley import Trolley

    logger.info('{name} began to follow you.'.format(name=ROBOT_NAME))
    robot = Trolley()
    robot.run()
    logger.info('{name} found you.'.format(name=ROBOT_NAME))


def trolley_tuner():
    from eva.robots.trolley_tuner import TrolleyTuner

    logger.info('{name} began to follow you.'.format(name=ROBOT_NAME))
    robot = TrolleyTuner()
    robot.run()
    logger.info('{name} found you.'.format(name=ROBOT_NAME))


def trolley_tuner_on_track():
    from eva.robots.trolley_tuner_on_track import TrolleyTunerOnTrack

    logger.info('{name} began to follow you.'.format(name=ROBOT_NAME))
    robot = TrolleyTunerOnTrack()
    robot.run()
    logger.info('{name} found you.'.format(name=ROBOT_NAME))


def tune_rotation():
    from eva.robots.tank_tuner import TankTuner

    logger.info('The auto-tuning of rotation started.')
    tuner = TankTuner()
    tuner.tune_rotation()
    logger.info('The auto-tuning of rotation finished.')


def tune_movement():
    from eva.robots.tank_tuner import TankTuner

    logger.info('The auto-tuning of movement started.')
    tuner = TankTuner()
    tuner.tune_movement()
    logger.info('The auto-tuning of movement finished.')


def tune_infrared_sensor():
    from eva.robots.ir_tuner import InfraredTuner

    logger.info('The auto-tuning of infrared sensor started.')
    tuner = InfraredTuner()
    tuner.tune_infrared_sensor()
    logger.info('The auto-tuning of infrared sensor finished.')


def tune_reflected_intensity():
    from eva.robots.color_tuner import ColorTuner

    logger.info('The auto-tuning of reflected intensity started.')
    tuner = ColorTuner()
    tuner.tune_reflected_intensity()
    logger.info('The auto-tuning of reflected intensity finished.')


def stop():
    from eva.robots.tracker import Tracker

    logger.info('{name} stop started.'.format(name=ROBOT_NAME))
    robot = Tracker()
    robot.tank.stop()
    logger.info('{name} was stopped.'.format(name=ROBOT_NAME))


def square_movement():
    import math

    from eva.robots.tracker import Tracker
    from eva.lib.command import MovementCommand, RotationCommand

    logger.info('{name} square movement started.'.format(name=ROBOT_NAME))
    robot = Tracker([
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
    logger.info('{name} movement was stopped.'.format(name=ROBOT_NAME))
