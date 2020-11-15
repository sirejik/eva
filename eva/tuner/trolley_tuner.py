import logging

from eva.lib.regulator import PIDRegulatorBase
from eva.tuner.trolley_tuner_base import TrolleyTunerBase

logger = logging.getLogger()


MAX_STABLE_SPREAD = 5
MAX_STABLE_MEASURE_NUMBER = 20
MAX_EXTREMUM_NUMBER = 20
MAX_UNSTABLE_MEASURE_NUMBER = 50


class TrolleyTuner(TrolleyTunerBase):
    def __init__(self):
        super(TrolleyTuner, self).__init__()

        self.low_stable_reflected_light_intensity = self.middle_reflected_light_intensity - MAX_STABLE_SPREAD
        self.high_stable_reflected_light_intensity = self.middle_reflected_light_intensity + MAX_STABLE_SPREAD

        self.stable_measure_number = 0
        self.last_extremum = None
        self.extremum_number = 0
        self.unstable_measure_number = 0

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

        if self.stable_measure_number > MAX_STABLE_MEASURE_NUMBER:
            return True

        return False

    def prepare(self):
        self.stable_measure_number = 0
        self.last_extremum = None
        self.extremum_number = 0
        self.unstable_measure_number = 0

        return super(TrolleyTuner, self).prepare()

    def stopping(self, measures):
        if self.extremum_number > MAX_EXTREMUM_NUMBER:
            return True

        if self.stable_measure_number > MAX_STABLE_MEASURE_NUMBER:
            return True

        if self.unstable_measure_number > MAX_UNSTABLE_MEASURE_NUMBER:
            return True

        return super(TrolleyTuner, self).stopping(measures)

    def moving(self):
        measures = super(TrolleyTuner, self).moving()
        self._process_measures(measures)
        return measures

    def _process_measures(self, measures):
        if self.low_stable_reflected_light_intensity <= measures.reflected_light_intensity <= \
                self.high_stable_reflected_light_intensity:
            self.stable_measure_number += 1
        else:
            self.stable_measure_number = 0

        if measures.reflected_light_intensity < self.middle_reflected_light_intensity:
            comparison = -1
        elif measures.reflected_light_intensity > self.middle_reflected_light_intensity:
            comparison = 1
        else:
            comparison = 0

        if comparison != 0:
            if self.last_extremum is None:
                self.last_extremum = comparison
                self.extremum_number = 1
            elif self.last_extremum != comparison:
                self.last_extremum = comparison
                self.extremum_number += 1
                self.unstable_measure_number = 0
            else:
                self.unstable_measure_number += 1
        else:
            self.unstable_measure_number = 0

    def save_to_config(self):
        self.pid_config.kp = self.kp
        self.pid_config.ki = self.ki
        self.pid_config.kd = self.kd

    def create_regulator(self) -> PIDRegulatorBase:
        return PIDRegulatorBase(self.kp, self.ki, self.kd, 0)
