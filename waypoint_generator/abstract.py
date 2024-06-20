from abc import ABC, abstractmethod


class Camera(ABC):
    @abstractmethod
    def calculate_fov(self, sensor_size, focal_length):
        pass

    @abstractmethod
    def calculate_coverage(self, fov, height):
        pass

    @abstractmethod
    def get_fov(self, height):
        pass
