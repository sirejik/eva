import logging

from collections import namedtuple

from ev3dev2.sensor.lego import ColorSensor, TouchSensor
from ev3dev2.sound import Sound

from eva.lib.config import ColorConfig
from eva.lib.settings import TEST_SPEED_IN_PERCENT, MAX_VELOCITY_IN_PERCENT, MotorsPortMapping
from eva.lib.regulator import PIDRegulatorBase
from eva.lib.utils import FunctionResultWaiter
from eva.modules.tank import Tank

logger = logging.getLogger()

Measure = namedtuple('Measure', ['reflected_light_intensity', 'color'])


class TrolleyTunerBase:
    TRACK_COLOR = ColorSensor.COLOR_WHITE
    STOP_COLOR = ColorSensor.COLOR_RED
    FLOOR_COLOR = ColorSensor.COLOR_BLACK
    FINISH_COLOR = ColorSensor.COLOR_GREEN

    def __init__(self):
        self.tank = Tank(left_motor=MotorsPortMapping.LEFT_MOTOR, right_motor=MotorsPortMapping.RIGHT_MOTOR)
        self.color_sensor = ColorSensor()
        self.touch_sensor = TouchSensor()
        self.sound = Sound()

        config = ColorConfig()
        config.verify()
        self.min_reflected_light_intensity = config.min_reflected_light_intensity
        self.max_reflected_light_intensity = config.max_reflected_light_intensity
        self.middle_reflected_light_intensity = (
            self.min_reflected_light_intensity + self.max_reflected_light_intensity
        ) * 0.5

        self.MAX_STEPS = 13
        self.is_stopped_on_stop_line = False
        self.regulator = None
        self.extremum_list = []
        self.min_mistake = None

    @property
    def forward_velocity(self):
        return self.tank.max_velocity * TEST_SPEED_IN_PERCENT / 100.0

    @property
    def rotate_velocity(self):
        return self.tank.max_velocity * MAX_VELOCITY_IN_PERCENT / 100.0

    def find_max_params(self, get_params, is_system_stable, start_value=0.0, end_value=1.0, step=0):
        current_value = (start_value + end_value) * 0.5
        if step >= self.MAX_STEPS:
            return start_value

        params = get_params(current_value)
        self.calibrate(params)

        if is_system_stable():
            return self.find_max_params(get_params, is_system_stable, current_value, end_value, step + 1)
        else:
            return self.find_max_params(get_params, is_system_stable, start_value, current_value, step + 1)

    def is_system_stable(self):
        if self.is_stopped_on_stop_line:
            return False

    def calibrate(self, params):
        self.preparation(params)

        FunctionResultWaiter(self.moving, None, check_function=self.is_should_be_stopped).run()
        self.tank.stop()

    def preparation(self, params):
        # 1. Set manually to the initial position
        self.sound.beep()
        FunctionResultWaiter(
            lambda: self.touch_sensor.is_pressed, None, check_function=lambda is_pressed: is_pressed == 1
        ).run()
        FunctionResultWaiter(
            lambda: self.touch_sensor.is_pressed, None, check_function=lambda is_pressed: is_pressed == 0
        ).run()

        # 2. Initiate variables
        self.is_stopped_on_stop_line = False
        kp, ki, kd = params

        self.regulator = PIDRegulatorBase(kp, ki, kd, self.middle_reflected_light_intensity)
        self.extremum_list = []

    def moving(self):
        measure = self.get_sensor_measures()
        power = self.regulator.get_power(measure.reflected_light_intensity)

        velocity_left = self.forward_velocity + self.rotate_velocity * power
        velocity_right = self.forward_velocity - self.rotate_velocity * power
        self.tank.on(velocity_left, velocity_right)

        return measure

    def is_should_be_stopped(self, measure):
        color_intensity, color = measure
        logger.debug(measure)
        if color == self.STOP_COLOR:
            self.is_stopped_on_stop_line = True
            return True

        if color == self.FINISH_COLOR:
            return True

        return False

    def get_sensor_measures(self):
        return Measure(
            reflected_light_intensity=self.color_sensor.reflected_light_intensity, color=self.color_sensor.color
        )

    def is_more_accurate(self):
        if not self.is_system_stable():
            return False

        if self.regulator.mistake <= self.min_mistake:
            self.min_mistake = self.regulator.mistake
            return True
        else:
            return False
