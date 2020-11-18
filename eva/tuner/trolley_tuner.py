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

        self._low_stable_reflected_light_intensity = self._middle_reflected_light_intensity - MAX_STABLE_DEVIATION
        self._high_stable_reflected_light_intensity = self._middle_reflected_light_intensity + MAX_STABLE_DEVIATION

        self._params.update(
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

    def _find_track(self):
        return

    def _process(self):
        kp = self._maximize_params(lambda x: {'kp': x, 'ki': 0, 'kd': 0})
        kd = self._maximize_params(lambda x: {'kp': kp, 'ki': 0, 'kd': x})
        ki = self._maximize_params(lambda x: {'kp': kp, 'ki': x, 'kd': kd})
        self._params.update({'kp': kp, 'ki': ki, 'kd': kd})

    @property
    def _forward_velocity(self):
        return 0

    def _is_system_stable(self):
        if super(TrolleyTuner, self)._is_system_stable() is False:
            return False

        if self._params.stable_measure_number > MAX_STABLE_MEASURE_NUMBER:
            return True

        return False

    def _stopping(self, measure):
        if self._params.extremum_number > MAX_EXTREMUM_NUMBER:
            return True

        if self._params.stable_measure_number > MAX_STABLE_MEASURE_NUMBER:
            return True

        if self._params.unstable_measure_number > MAX_UNSTABLE_MEASURE_NUMBER:
            return True

        return super(TrolleyTuner, self)._stopping(measure)

    def _moving(self):
        measures = super(TrolleyTuner, self)._moving()
        self._process_measures(measures)
        return measures

    def _process_measures(self, measures):
        if self._low_stable_reflected_light_intensity <= measures.reflected_light_intensity <= \
                self._high_stable_reflected_light_intensity:
            self._params.stable_measure_number += 1
        else:
            self._params.stable_measure_number = 0

        if measures.reflected_light_intensity < self._middle_reflected_light_intensity:
            comparison = -1
        elif measures.reflected_light_intensity > self._middle_reflected_light_intensity:
            comparison = 1
        else:
            comparison = 0

        if comparison != 0:
            if self._params.last_extremum is None:
                self._params.last_extremum = comparison
                self._params.extremum_number = 1
            elif self._params.last_extremum != comparison:
                self._params.last_extremum = comparison
                self._params.extremum_number += 1
                self._params.unstable_measure_number = 0
            else:
                self._params.unstable_measure_number += 1
        else:
            self._params.unstable_measure_number = 0

    def _save_to_config(self):
        self._pid_config.kp = self._params.kp
        self._pid_config.ki = self._params.ki
        self._pid_config.kd = self._params.kd

    def _create_regulator(self) -> PIDRegulator:
        return PIDRegulator(self._params.kp, self._params.ki, self._params.kd, 0)
