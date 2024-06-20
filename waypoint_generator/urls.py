from django.urls import path, include
from rest_framework import routers
from waypoint_generator.views import home, FlightPathViewSet

router = routers.SimpleRouter()
router.register(r"generate_waypoints", FlightPathViewSet, basename="generate_waypoints")

urlpatterns = [
    path("", home, name="home"),
    path("", include(router.urls)),
]
