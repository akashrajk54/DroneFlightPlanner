from django.db import models
from accounts_engine.models import BaseClass, CustomUser


class FlightPath(BaseClass):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="flightpaths")
    polygon_lat_lon = models.JSONField(help_text="List of latitude and longitude coordinates forming the closed "
                                                 "polygon.")
    altitude = models.FloatField(help_text="Altitude in meters.")
    overlapping_percentage = models.FloatField(help_text="Image overlapping percentage.")
    drone_speed = models.FloatField(help_text="Speed of the drone in meters per second.", null=True, blank=True)
    waypoints = models.JSONField(help_text="List of generated waypoints (latitude, longitude) in the format of "
                                           "[(lat, lon), ...].", null=True, blank=True)

    def clean(self):
        if not isinstance(self.polygon_lat_lon, list) or len(self.polygon_lat_lon) < 3:
            raise ValueError("Polygon must have at least 3 points.")
        if self.polygon_lat_lon[0] != self.polygon_lat_lon[-1]:
            raise ValueError("Polygon must be closed.")
        if self.altitude < 100:
            raise ValueError("Altitude must be at least 100 meters.")
        if self.overlapping_percentage < 50:
            raise ValueError("Image overlapping percentage must be at least 50%.")

    def __str__(self):
        return f"FlightPathRequest by {self.user.email} - Altitude: {self.altitude} meters, Overlap: {self.overlapping_percentage}%"
