from eva.modules.tank import Tank


class Traveler:
    def __init__(self, commands=None):
        self._tank = Tank()
        self._commands = commands or []

    def _run(self):
        for command in self._commands:
            command.execute(self._tank, self._velocity)

    @property
    def _velocity(self):
        return self._tank.normal_velocity
