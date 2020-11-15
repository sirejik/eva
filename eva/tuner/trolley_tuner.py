import logging

from eva.lib.regulator import PIDRegulator
from eva.tuner.trolley_tuner_base import TrolleyTunerBase

logger = logging.getLogger()


MAX_STABLE_DEVIATION = 5
MAX_STABLE_MEASURE_NUMBER = 20
MAX_EXTREMUM_NUMBER = 20
MAX_UNSTABLE_MEASURE_NUMBER = 50


class TrolleyTuner(TrolleyTunerBase):
    def __init__(self):
        super(TrolleyTuner, self).__init__()

        self.low_stable_reflected_light_intensity = self.middle_reflected_light_intensity - MAX_STABLE_DEVIATION
        self.high_stable_reflected_light_intensity = self.middle_reflected_light_intensity + MAX_STABLE_DEVIATION

        self.params.update(
            {
                'kp': None,
                'ki': None,
                'kd': None,
                'stable_measure_number': 0,
                'last_extremum': None,
                'extremum_number': 0,
                'unstable_measure_number': 0
            }
        )

    def find_track(self):
        return

    def process(self):
        kp = self.maximize_params(lambda x: {'kp': x, 'ki': 0, 'kd': 0})
        kd = self.maximize_params(lambda x: {'kp': kp, 'ki': 0, 'kd': x})
        ki = self.maximize_params(lambda x: {'kp': kp, 'ki': x, 'kd': kd})
        self.params.update({'kp': kp, 'ki': ki, 'kd': kd})

    @property
    def forward_velocity(self):
        return 0

    def is_system_stable(self):
        if super(TrolleyTuner, self).is_system_stable() is False:
            return False

        if self.params.stable_measure_number > MAX_STABLE_MEASURE_NUMBER:
            return True

        return False

    def stopping(self, measure):
        if self.params.extremum_number > MAX_EXTREMUM_NUMBER:
            return True

        if self.params.stable_measure_number > MAX_STABLE_MEASURE_NUMBER:
            return True

        if self.params.unstable_measure_number > MAX_UNSTABLE_MEASURE_NUMBER:
            return True

        return super(TrolleyTuner, self).stopping(measure)

    def moving(self):
        measures = super(TrolleyTuner, self).moving()
        self._process_measures(measures)
        return measures

    def _process_measures(self, measures):
        if self.low_stable_reflected_light_intensity <= measures.reflected_light_intensity <= \
                self.high_stable_reflected_light_intensity:
            self.params.stable_measure_number += 1
        else:
            self.params.stable_measure_number = 0

        if measures.reflected_light_intensity < self.middle_reflected_light_intensity:
            comparison = -1
        elif measures.reflected_light_intensity > self.middle_reflected_light_intensity:
            comparison = 1
        else:
            comparison = 0

        if comparison != 0:
            if self.params.last_extremum is None:
                self.params.last_extremum = comparison
                self.params.extremum_number = 1
            elif self.params.last_extremum != comparison:
                self.params.last_extremum = comparison
                self.params.extremum_number += 1
                self.params.unstable_measure_number = 0
            else:
                self.params.unstable_measure_number += 1
        else:
            self.params.unstable_measure_number = 0

    def save_to_config(self):
        self.pid_config.kp = self.params.kp
        self.pid_config.ki = self.params.ki
        self.pid_config.kd = self.params.kd

    def create_regulator(self) -> PIDRegulator:
        return PIDRegulator(self.params.kp, self.params.ki, self.params.kd, 0)
