import logging

from ev3dev2.motor import LargeMotor, MoveTank

from eva.lib.config import TankConfig
from eva.lib.settings import LOW_VELOCITY_IN_PERCENT, TEST_VELOCITY_IN_PERCENT, NORMAL_VELOCITY_IN_PERCENT, \
    HIGH_VELOCITY_IN_PERCENT, MAX_VELOCITY_IN_PERCENT, MotorsPortMapping

logger = logging.getLogger()


class TankBase:
    def __init__(self, left_motor=MotorsPortMapping.LEFT_MOTOR, right_motor=MotorsPortMapping.RIGHT_MOTOR):
        self.config = TankConfig()

        self._left_motor = left_motor
        self._right_motor = right_motor
        self._tank_pair = MoveTank(self._left_motor, self._right_motor, motor_class=LargeMotor)

    @property
    def low_velocity(self):
        return LOW_VELOCITY_IN_PERCENT

    @property
    def test_velocity(self):
        return TEST_VELOCITY_IN_PERCENT

    @property
    def normal_velocity(self):
        return NORMAL_VELOCITY_IN_PERCENT

    @property
    def high_velocity(self):
        return HIGH_VELOCITY_IN_PERCENT

    @property
    def _max_velocity(self):
        return MAX_VELOCITY_IN_PERCENT

    @property
    def motor_degrees(self):
        return self._tank_pair.motors[self._right_motor].degrees

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
        if velocity_left > self._max_velocity or velocity_right > self._max_velocity:
            if velocity_left > velocity_right:
                return self._max_velocity, velocity_right * self._max_velocity / velocity_left
            else:
                return velocity_left * self._max_velocity / velocity_right, self._max_velocity
        else:
            return velocity_left, velocity_right


class Tank(TankBase):
    def __init__(self, left_motor=MotorsPortMapping.LEFT_MOTOR, right_motor=MotorsPortMapping.RIGHT_MOTOR):
        super(Tank, self).__init__(left_motor, right_motor)

        self.config.verify()

        self._degrees_for_360_rotation = self.config.degrees_for_360_rotation
        self._degrees_for_1_meter_movement = self.config.degrees_for_1_meter_movement
        self._track_spacing = self.config.track_spacing

    def move_in_arc(self, velocity, radius):
        if radius is None:
            self.forward(velocity)
            return

        if radius == 0:
            self.stop()

        velocity_coefficient = self._track_spacing * 0.5 / radius
        velocity_left = velocity * (1 + velocity_coefficient)
        velocity_right = velocity * (1 - velocity_coefficient)

        self.on(velocity_left, velocity_right)

    def forward_on_distance(self, velocity, distance):
        degrees = self._degrees_for_1_meter_movement * distance
        self._tank_pair.on_for_degrees(left_speed=velocity, right_speed=velocity, degrees=degrees)

    def rotate_on_angle(self, velocity, angle):
        degrees = self._degrees_for_360_rotation * angle / 360
        self._tank_pair.on_for_degrees(left_speed=velocity, right_speed=-velocity, degrees=degrees)

    def rotate_on_degrees(self, velocity, degrees):
        self._tank_pair.on_for_degrees(left_speed=velocity, right_speed=-velocity, degrees=degrees)
