import math

from ev3dev2.motor import OUTPUT_B, OUTPUT_C

CONFIG_FILE = 'config.ini'
LOG_FILE_NAME = 'debug.log'

ROBOT_NAME = 'Eva'

RADIAN_IN_HEADING = math.pi / 80.0
METER_IN_DISTANCE = 2.3 / 100.0

TUNE_MOVEMENT_LENGTH = 2.0
TUNE_MOVEMENT_ROTATION_COUNT = 10

TIME_INTERVAL_BETWEEN_ATTEMPTS = 0.001
TEST_SPEED_IN_PERCENT = 25
MIN_SPEED_IN_PERCENT = 10
NORMAL_VELOCITY_IN_PERCENT = 50
MAX_VELOCITY_IN_PERCENT = 80


class MotorsPortMapping:
    LEFT_MOTOR = OUTPUT_C
    RIGHT_MOTOR = OUTPUT_B
