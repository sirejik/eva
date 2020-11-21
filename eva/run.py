import logging

from eva.lib.settings import LOG_FILE_NAME, ROBOT_NAME
from eva.lib.utils import configure_logging
from eva.tuner.tuner_base import TunerBase

logger = logging.getLogger()


def run(create_robot):
    configure_logging()
    try:
        logger.info('{name} started to work.'.format(name=ROBOT_NAME))
        robot = create_robot()
        if isinstance(robot, TunerBase):
            robot.tune()
        else:
            robot.run()

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


def create_follower():
    from eva.robots.follower import Follower

    return Follower()


def create_traveler():
    from eva.robots.traveler import Traveler
    from eva.lib.command import MovementCommand, RotationCommand

    return Traveler([
            MovementCommand(0.5),
            RotationCommand(90),
            MovementCommand(0.5),
            RotationCommand(90),
            MovementCommand(0.5),
            RotationCommand(90),
            MovementCommand(0.5),
            RotationCommand(90)
        ])


def create_trolley():
    from eva.robots.trolley import Trolley

    return Trolley()


def create_color_tuner():
    from eva.tuner.color_tuner import ColorTuner

    return ColorTuner()


def create_infrared_tuner():
    from eva.tuner.infrared_tuner import InfraredTuner

    return InfraredTuner()


def create_tank_tuner():
    from eva.tuner.tank_tuner import TankTuner

    return TankTuner()


def create_trolley_tuner():
    from eva.tuner.trolley_pid_regulator_tuner import TrolleyPIDRegulatorTuner

    return TrolleyPIDRegulatorTuner()


def create_trolley_tuner_on_track():
    from eva.tuner.trolley_velocity_tuner import TrolleyVelocityTuner

    return TrolleyVelocityTuner()
