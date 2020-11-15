import logging

logger = logging.getLogger()


class PIDRegulator:
    def __init__(self, kp, ki, kd, r):
        self.power = 0
        self.en = 0
        self.en1 = 0

        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.r = r

        self.mistake = 0

    def get_power(self, value):
        en, en1, en2, power_old = self.r - value, self.en, self.en1, self.power
        power = power_old + self.kp * (en - en1) + self.ki * en + self.kd * (en - 2 * en1 + en2)
        self.en, self.en1, self.power = en, en1, power

        self.mistake += abs(en)
        return power
