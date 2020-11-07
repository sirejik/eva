import logging
import math
import time

from PIL import Image, ImageDraw

from eva.modules.tank import Tank
from eva.modules.infraredsensor import InfraredSensor
from eva.tuner.base_tuner import BaseTuner

logger = logging.getLogger()

IMAGE_SIZE = 400
RADIUS_SEGMENT = 16
RADIUS_STEP = 2.0 * math.pi / float(RADIUS_SEGMENT)
DISTANCE_SEGMENT = 8
DISTANCE_STEP = -0.1


class InfraredTuner(BaseTuner):
    def __init__(self):
        super(InfraredTuner, self).__init__()

        self.tank = Tank()
        self.infrared_sensor = InfraredSensor()

    def process(self):
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

                self.tank.rotate_for_degrees(self.tank.test_velocity, RADIUS_STEP)

            self.tank.rotate_for_degrees(self.tank.test_velocity, - 2 * math.pi)
            self.tank.forward_for_degrees(self.tank.test_velocity, DISTANCE_STEP)

        heading_image.save("heading_image.png")
        distance_image.save("distance_image.png")

    def save_to_config(self):
        raise
