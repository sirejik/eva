import logging
import math
import time

from PIL import Image, ImageDraw

from eva.lib.config import TankConfig
from eva.lib.settings import TEST_SPEED_IN_PERCENT, MotorsPortMapping
from eva.modules.tank import Tank
from eva.modules.infraredsensor import InfraredSensor

logger = logging.getLogger()

IMAGE_SIZE = 400
RADIUS_SEGMENT = 16
RADIUS_STEP = 2.0 * math.pi / float(RADIUS_SEGMENT)
DISTANCE_SEGMENT = 8
DISTANCE_STEP = -0.1


class InfraredTuner:
    def __init__(self):
        self.tank = Tank(left_motor=MotorsPortMapping.LEFT_MOTOR, right_motor=MotorsPortMapping.RIGHT_MOTOR)
        self.config = TankConfig()
        self.infrared_sensor = InfraredSensor()

    @property
    def velocity_for_test(self):
        return self.tank.max_velocity * TEST_SPEED_IN_PERCENT / 100.0

    def tune_infrared_sensor(self):
        def point_coord(_x, _y):
            radius = _x / float(DISTANCE_SEGMENT)
            angle = _y * RADIUS_STEP
            return int(0.5 * IMAGE_SIZE * (1 - radius * math.sin(angle))), \
                int(0.5 * IMAGE_SIZE * (1 - radius * math.cos(angle)))

        def draw_polygon(drawer, _polygon, value, min_value, max_value):
            color = int(0 if value is None else 255 * (value - min_value) / float(max_value - min_value))
            drawer.polygon(_polygon, fill=(color, color, color), outline=(color, color, color))

        def write_value(drawer, coord, value):
            drawer.text(coord, str(value), fill="red", align="center")

        heading_image = Image.new('RGB', (IMAGE_SIZE, IMAGE_SIZE), (0, 0, 0))
        heading_image_drawer = ImageDraw.Draw(heading_image)
        distance_image = Image.new('RGB', (IMAGE_SIZE, IMAGE_SIZE), (0, 0, 0))
        distance_image_drawer = ImageDraw.Draw(distance_image)

        for x in range(0, DISTANCE_SEGMENT):
            for y in range(0, RADIUS_SEGMENT):
                time.sleep(0.25)
                heading, distance = self.infrared_sensor.heading_and_distance()

                polygon = [
                    point_coord(x, y - 0.5), point_coord(x, y + 0.5), point_coord(x + 1, y + 0.5),
                    point_coord(x + 1, y - 0.5)
                ]

                draw_polygon(heading_image_drawer, polygon, heading, -25, 25)
                write_value(heading_image_drawer, point_coord(x + 0.5, y), heading)
                draw_polygon(distance_image_drawer, polygon, distance, 0, 100)
                write_value(distance_image_drawer, point_coord(x + 0.5, y), distance)

                self.tank.rotate_for_degrees(self.velocity_for_test, RADIUS_STEP)

            self.tank.rotate_for_degrees(self.velocity_for_test, - 2 * math.pi)
            self.tank.forward_for_degrees(self.velocity_for_test, DISTANCE_STEP)

        heading_image.save("heading_image.png")
        distance_image.save("distance_image.png")
