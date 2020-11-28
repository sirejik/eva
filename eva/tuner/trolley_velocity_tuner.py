import logging

from eva.tuner.trolley_tuner_base import TrolleyTunerBase

logger = logging.getLogger()


class TrolleyVelocityTuner(TrolleyTunerBase):
    def __init__(self):
        super(TrolleyVelocityTuner, self).__init__()

        self._pid_config.verify_pid_parameters()
        self._params.update(
            {'forward_velocity': 0, 'kp': self._pid_config.kp, 'ki': self._pid_config.ki, 'kd': self._pid_config.kd}
        )

    def _process(self):
        super(TrolleyVelocityTuner, self)._process()

        forward_velocity = self._maximize_params(lambda x: {'forward_velocity': x})
        self._restore_and_update_params({'forward_velocity': forward_velocity})

    @property
    def _forward_velocity(self):
        return self._params.forward_velocity * self._tank.high_velocity

    def _save_to_config(self):
        self._pid_config.max_forward_velocity = self._forward_velocity
        self._pid_config.save()
