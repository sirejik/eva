import logging

from collections import namedtuple

from eva.robots.trolley_tuner_base import TrolleyTunerBase

logger = logging.getLogger()

TimePoint = namedtuple('TimePoint', ['time', 'color', 'comparison'])


class TrolleyTuner(TrolleyTunerBase):
    def __init__(self):
        super(TrolleyTuner, self).__init__()

        self.MAX_EXTREMUM_NUMBER = 20
        self.MAX_DAMPING = 0.10

        self.min_mistake = 0
        self.time = 0

    def run(self):
        kp = self.find_max_params(lambda x: (x, 0, 0), self.is_system_stable)
        self.min_mistake = self.regulator.mistake
        kd = self.find_max_params(lambda x: (kp, 0, x), self.is_more_accurate)
        ki = self.find_max_params(lambda x: (kp, x, kd), self.is_more_accurate)

        logger.debug(kp)
        logger.debug(ki)
        logger.debug(kd)

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

    def calibrate(self, params):
        self.time = 0
        return super(TrolleyTuner, self).calibrate(params)

    def is_should_be_stopped(self, measure):
        if len(self.extremum_list) > self.MAX_EXTREMUM_NUMBER:
            return True

        return super(TrolleyTuner, self).is_should_be_stopped(measure)

    def moving(self):
        measure = super(TrolleyTuner, self).moving()
        self._process_measure(measure)
        return measure

    def _process_measure(self, measure):
        self.time += 1
        time_point = self._get_time_point(measure.reflected_light_intensity)
        if len(self.extremum_list) == 0:
            self.extremum_list.append(time_point)
        else:
            last_extremum = self.extremum_list[-1]
            if last_extremum.comparison != time_point.comparison or time_point.comparison == 0:
                self.extremum_list.append(time_point)
            else:
                if (last_extremum.comparison == 1 and last_extremum.color > time_point.color) or \
                        (last_extremum.comparison == -1 and last_extremum.color < time_point.color):
                    self.extremum_list[-1] = time_point

    def _get_time_point(self, color):
        if color < self.middle_reflected_light_intensity:
            comparison = -1
        elif color > self.middle_reflected_light_intensity:
            comparison = 1
        else:
            comparison = 0

        return TimePoint(time=self.time, color=color, comparison=comparison)
