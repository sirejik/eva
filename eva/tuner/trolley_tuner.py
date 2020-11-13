import logging

from collections import namedtuple

from eva.lib.regulator import PIDRegulatorBase
from eva.tuner.trolley_tuner_base import TrolleyTunerBase

logger = logging.getLogger()

TimePoint = namedtuple('TimePoint', ['time', 'color', 'comparison'])


class TrolleyTuner(TrolleyTunerBase):
    def __init__(self):
        super(TrolleyTuner, self).__init__()

        self.min_reflected_light_intensity = self.color_sensor.config.min_reflected_light_intensity
        self.max_reflected_light_intensity = self.color_sensor.config.max_reflected_light_intensity

        self.MAX_EXTREMUM_NUMBER = 20
        self.MAX_DAMPING = 0.5

        self.time = 0

    def find_track(self):
        return

    def process(self):
        kp = self.maximize_params(lambda x: (x, 0, 0), self.is_system_stable)
        kd = self.maximize_params(lambda x: (kp, 0, x), self.is_system_stable)
        ki = self.maximize_params(lambda x: (kp, x, kd), self.is_system_stable)

        self.kp, self.ki, self.kd = kp, ki, kd

    @property
    def forward_velocity(self):
        return 0

    def is_system_stable(self):
        if super(TrolleyTuner, self).is_system_stable() is False:
            return False

        extremum_list = self.extremum_list[1:-1]

        top_extremum = [x.color for x in extremum_list if x.comparison == 1]
        bottom_extremum = [x.color for x in extremum_list if x.comparison == -1]

        if len(top_extremum) == 0 or len(bottom_extremum) == 0:
            return True

        max_top_extremum = max(top_extremum)
        min_bottom_extremum = min(bottom_extremum)

        if max_top_extremum == min_bottom_extremum:
            raise

        return (top_extremum[-1] - bottom_extremum[-1]) / (
                self.max_reflected_light_intensity - self.min_reflected_light_intensity
        ) < self.MAX_DAMPING

    def prepare(self):
        self.time = 0
        return super(TrolleyTuner, self).prepare()

    def stopping(self, measures):
        if len(self.extremum_list) > self.MAX_EXTREMUM_NUMBER:
            return True

        return super(TrolleyTuner, self).stopping(measures)

    def moving(self):
        measures = super(TrolleyTuner, self).moving()
        self._process_measures(measures)
        return measures

    def _process_measures(self, measures):
        self.time += 1
        time_point = self._get_time_point(measures.reflected_light_intensity)
        if len(self.extremum_list) == 0:
            self.extremum_list.append(time_point)
        else:
            last_extremum = self.extremum_list[-1]
            if last_extremum.comparison != time_point.comparison or time_point.comparison == 0:
                self.extremum_list.append(time_point)
            else:
                if (last_extremum.comparison == 1 and last_extremum.color < time_point.color) or \
                        (last_extremum.comparison == -1 and last_extremum.color > time_point.color):
                    self.extremum_list[-1] = time_point

    def _get_time_point(self, color):
        if color < self.middle_reflected_light_intensity:
            comparison = -1
        elif color > self.middle_reflected_light_intensity:
            comparison = 1
        else:
            comparison = 0

        return TimePoint(time=self.time, color=color, comparison=comparison)

    def save_to_config(self):
        self.pid_config.kp = self.kp
        self.pid_config.ki = self.ki
        self.pid_config.kd = self.kd

    def create_regulator(self) -> PIDRegulatorBase:
        return PIDRegulatorBase(self.kp, self.ki, self.kd, 0.5)
