import logging
import math

from ev3dev2.motor import LargeMotor, MoveTank

from eva.lib.config import TankConfig
from eva.lib.settings import LOW_SPEED_IN_PERCENT, TEST_SPEED_IN_PERCENT, NORMAL_SPEED_IN_PERCENT, \
    HIGH_SPEED_IN_PERCENT, MAX_VELOCITY_IN_PERCENT, MotorsPortMapping

logger = logging.getLogger()


class BaseTank:
    def __init__(self, left_motor=MotorsPortMapping.LEFT_MOTOR, right_motor=MotorsPortMapping.RIGHT_MOTOR):
        self.config = TankConfig()

        self.left_motor = left_motor
        self.right_motor = right_motor
        self._tank_pair = MoveTank(self.left_motor, self.right_motor, motor_class=LargeMotor)

    @property
    def motor_degrees(self):
        return self._tank_pair.motors[self.right_motor].degrees

    @property
    def max_velocity(self):
        return self._tank_pair.motors[self.right_motor].max_speed

    @property
    def low_velocity(self):
        return LOW_SPEED_IN_PERCENT

    @property
    def test_velocity(self):
        return TEST_SPEED_IN_PERCENT

    @property
    def normal_velocity(self):
        return NORMAL_SPEED_IN_PERCENT

    @property
    def high_velocity(self):
        return HIGH_SPEED_IN_PERCENT

    @property
    def max_power_in_percent(self):
        return MAX_VELOCITY_IN_PERCENT

    def forward(self, velocity):
        self._tank_pair.on(left_speed=velocity, right_speed=velocity)

    def on(self, velocity_left, velocity_right):
        velocity_left_percentage, velocity_right_percentage = self._get_calibrated_velocities_in_percent(
            velocity_left, velocity_right
        )

        self._tank_pair.on(left_speed=velocity_left_percentage, right_speed=velocity_right_percentage)

    def rotate(self, velocity, is_right_turn):
        if is_right_turn:
            self._tank_pair.on(left_speed=velocity, right_speed=-velocity)
        else:
            self._tank_pair.on(left_speed=-velocity, right_speed=velocity)

    def stop(self):
        self._tank_pair.stop()  # TODO: check option brake

    def _get_calibrated_velocities_in_percent(self, velocity_left, velocity_right):
        velocity_left_percentage = velocity_left
        velocity_right_percentage = velocity_right

        max_value = max(math.fabs(velocity_left), math.fabs(velocity_right))

        if max_value > self.max_power_in_percent:
            power_coefficient = self.max_power_in_percent / float(max_value)
            velocity_left_percentage = velocity_left_percentage * power_coefficient
            velocity_right_percentage = velocity_right_percentage * power_coefficient

        return velocity_left_percentage, velocity_right_percentage


class Tank(BaseTank):
    def __init__(self, left_motor=MotorsPortMapping.LEFT_MOTOR, right_motor=MotorsPortMapping.RIGHT_MOTOR):
        super(Tank, self).__init__(left_motor, right_motor)

        self.config.verify()
        self.degrees_to_360_rotation = self.config.degrees_to_360_rotation
        self.degrees_to_1_meter_movement = self.config.degrees_to_1_meter_movement
        self.furrow = self.config.furrow

    def move_in_arc(self, velocity, radius):
        if radius is None:
            self.forward(velocity)
            return

        if radius == 0:
            self.stop()

        velocity_coefficient = self.furrow * 0.5 / radius
        velocity_left = velocity * (1 + velocity_coefficient)
        velocity_right = velocity * (1 - velocity_coefficient)

        velocity_left_percentage, velocity_right_percentage = self._get_calibrated_velocities_in_percent(
            velocity_left, velocity_right
        )

        self._tank_pair.on(left_speed=velocity_left_percentage, right_speed=velocity_right_percentage)

    def forward_for_degrees(self, velocity, way_length):
        degrees = self.degrees_to_1_meter_movement * way_length
        self._tank_pair.on_for_degrees(left_speed=velocity, right_speed=velocity, degrees=degrees)

    def rotate_for_degrees(self, velocity, degrees):
        degrees = self.degrees_to_360_rotation * degrees / (2.0 * math.pi)
        self._tank_pair.on_for_degrees(left_speed=velocity, right_speed=-velocity, degrees=degrees)
