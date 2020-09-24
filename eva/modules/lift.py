import logging

from ev3dev2.motor import MediumMotor

logger = logging.getLogger()


class Lift:
    def __init__(self, medium_motor):
        self.medium_motor = medium_motor
        self._tank_pair = MediumMotor(medium_motor)

    #: The motor is turning, but cannot reach its ``speed_sp``.
    STATE_OVERLOADED = 'overloaded'

    #: The motor is not turning when it should be.
    STATE_STALLED = 'stalled'
