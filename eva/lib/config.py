import json
import logging

from eva.lib.settings import CONFIG_FILE

logger = logging.getLogger()


class Config:
    def __init__(self, config_file_name):
        self.config_file_name = config_file_name
        self.config = None

    def verify(self):
        raise NotImplemented()

    def read_settings_config_file(self):
        try:
            with open(self.config_file_name) as f:
                self.config = json.load(f)
        except IOError:
            logger.debug('File with configuration settings was not found. Configuration settings not defined.')
            self.config = {}

    def save_setting_to_config_file(self):
        with open(self.config_file_name, 'w') as f:
            json.dump(self.config, f)

    def get_property(self, property_name):
        if self.config is None:
            self.read_settings_config_file()

        if property_name in self.config:
            return self.config[property_name]
        else:
            return None

    def set_property(self, property_name, value):
        if self.config is None:
            self.read_settings_config_file()

        self.config[property_name] = value
        self.save_setting_to_config_file()


class TankConfig(Config):
    def __init__(self):
        super(TankConfig, self).__init__(CONFIG_FILE)

    def verify(self):
        if self.degrees_to_360_rotation is None:
            raise Exception(
                'The parameter "degrees_to_360_rotation" was not found in the config file. You must run the '
                'tune_motion.py.'
            )

        if self.degrees_to_1_meter_movement is None:
            raise Exception(
                'The parameter "degrees_to_1_meter_movement" was not found in the config file. You must run the '
                'tune_motion.py.'
            )

        if self.furrow is None:
            raise Exception(
                'The parameter "furrow" was not found in the config file. You must run the tune_motion.py.'
            )

    @property
    def furrow(self):
        return self.get_property('furrow')

    @furrow.setter
    def furrow(self, value):
        self.set_property('furrow', value)

    @property
    def degrees_to_360_rotation(self):
        return self.get_property('degrees_to_360_rotation')

    @degrees_to_360_rotation.setter
    def degrees_to_360_rotation(self, value):
        self.set_property('degrees_to_360_rotation', value)

    @property
    def degrees_to_1_meter_movement(self):
        return self.get_property('degrees_to_1_meter_movement')

    @degrees_to_1_meter_movement.setter
    def degrees_to_1_meter_movement(self, value):
        self.set_property('degrees_to_1_meter_movement', value)


class ColorConfig(Config):
    def __init__(self):
        super(ColorConfig, self).__init__(CONFIG_FILE)

    def verify(self):
        if self.min_reflected_light_intensity is None or self.max_reflected_light_intensity is None:
            raise Exception(
                'The reflected light intensity doesn\'t calibrated. You must run the tune_reflected_intensity.py.'
            )

    @property
    def min_reflected_light_intensity(self):
        return self.get_property('min_reflected_light_intensity')

    @min_reflected_light_intensity.setter
    def min_reflected_light_intensity(self, value):
        self.set_property('min_reflected_light_intensity', value)

    @property
    def max_reflected_light_intensity(self):
        return self.get_property('max_reflected_light_intensity')

    @max_reflected_light_intensity.setter
    def max_reflected_light_intensity(self, value):
        self.set_property('max_reflected_light_intensity', value)


class TrolleyPIDConfig(Config):
    def __init__(self):
        super(TrolleyPIDConfig, self).__init__(CONFIG_FILE)

    def verify(self):
        if self.kp is None or self.ki is None or self.kd is None:
            raise Exception(
                'The PID regulator doesn\'t tuned. You must run the tune_trolley_pid_regulator.py.'
            )

        if self.max_velocity is None:
            raise Exception(
                'The max velocity for the trolley doesn\'t tuned. You must run the tune_trolley_velocity.py.'
            )

    @property
    def kp(self):
        return self.get_property('kp')

    @kp.setter
    def kp(self, value):
        self.set_property('kp', value)

    @property
    def ki(self):
        return self.get_property('ki')

    @ki.setter
    def ki(self, value):
        self.set_property('ki', value)

    @property
    def kd(self):
        return self.get_property('kd')

    @kd.setter
    def kd(self, value):
        self.set_property('kd', value)

    @property
    def max_velocity(self):
        return self.get_property('max_velocity')

    @max_velocity.setter
    def max_velocity(self, value):
        self.set_property('max_velocity', value)
