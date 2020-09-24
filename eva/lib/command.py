class CommandList:
    MOVEMENT = 1
    ROTATION = 2


class CommandBase:
    def __init__(self, name):
        self.name = name


class MovementCommand(CommandBase):
    def __init__(self, way_length):
        super(MovementCommand, self).__init__(CommandList.MOVEMENT)
        self.way_length = way_length


class RotationCommand(CommandBase):
    def __init__(self, angle):
        super(RotationCommand, self).__init__(CommandList.ROTATION)
        self.angle = angle
