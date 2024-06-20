import math
from waypoint_generator.abstract import Camera


class GoProHero9Black(Camera):
    def __init__(self):
        self.sensor_width = 6.17  # in mm
        self.sensor_height = 4.55  # in mm
        self.focal_length = 3  # in mm

    def calculate_fov(self, sensor_size, focal_length):
        return 2 * math.degrees(math.atan(sensor_size / (2 * focal_length)))

    def calculate_coverage(self, fov, height):
        return 2 * (height * math.tan(math.radians(fov / 2)))

    def get_fov(self, height):
        fov_horizontal = self.calculate_fov(self.sensor_width, self.focal_length)
        fov_vertical = self.calculate_fov(self.sensor_height, self.focal_length)

        coverage_horizontal = self.calculate_coverage(fov_horizontal, height)
        coverage_vertical = self.calculate_coverage(fov_vertical, height)

        return coverage_vertical, coverage_horizontal
