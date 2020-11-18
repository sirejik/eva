import logging

logger = logging.getLogger()


class PIDRegulator:
    def __init__(self, kp, ki, kd, r):
        self._kp = kp
        self._ki = ki
        self._kd = kd
        self._r = r

        self._power = 0
        self._en = 0
        self._en1 = 0
        self._mistake = 0

    def get_power(self, value):
        en, en1, en2, power_old = self._r - value, self._en, self._en1, self._power
        power = power_old + self._kp * (en - en1) + self._ki * en + self._kd * (en - 2 * en1 + en2)
        self._en, self._en1, self._power = en, en1, power

        self._mistake += abs(en)
        return power

    def get_mistake(self):
        return self._mistake
