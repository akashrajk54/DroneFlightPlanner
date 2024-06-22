from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from waypoint_generator.models import FlightPath
from waypoint_generator.serializers import FlightPathSerializer
from accounts_engine.utils import success_true_response, success_false_response

from waypoint_generator.services import GoProHero9Black
from waypoint_generator.utils import (
    generate_horizontal_waypoints,
    generate_vertical_waypoints,
    generate_all_points,
    get_bounding_box,
    plot_waypoints,
    convert_polygon_to_decimal,
    filter_points,
)

import logging

logger = logging.getLogger(__name__)
logger_info = logging.getLogger("info")
logger_error = logging.getLogger("error")


@api_view(["GET"])
def home(request):
    return Response({"success": True})


class FlightPathViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = FlightPath.objects.all().order_by("-created_datetime")
    serializer_class = FlightPathSerializer

    def __init__(self, *args, **kwargs):
        self.get_bounding_box = kwargs.pop("get_bounding_box", get_bounding_box)
        self.camera = kwargs.pop("camera", GoProHero9Black())
        self.generate_vertical_waypoints = kwargs.pop("generate_vertical_waypoints", generate_vertical_waypoints)
        self.generate_horizontal_waypoints = kwargs.pop("generate_horizontal_waypoints", generate_horizontal_waypoints)
        self.generate_all_points = kwargs.pop("generate_all_points", generate_all_points)
        self.plot_waypoints = kwargs.pop("plot_waypoints", plot_waypoints)
        self.convert_polygon_to_decimal = kwargs.pop("convert_polygon_to_decimal", convert_polygon_to_decimal)
        self.filter_points = kwargs.pop("filter_points", filter_points)
        super().__init__(*args, **kwargs)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super(FlightPathViewSet, self).get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action in ["list", "retrieve"]:
            context["exclude_user"] = True
        return context

    def get_queryset(self):
        if self.action == "list":
            sorted_queryset = FlightPath.objects.all().order_by("-created_datetime")
            return sorted_queryset

    def create(self, request, *args, **kwargs):
        try:
            user = request.user

            requested_data = request.data.copy()
            requested_data["user"] = user.id
            serializer = self.get_serializer(data=requested_data)

            try:
                serializer.is_valid(raise_exception=True)

                polygon = requested_data["polygon_lat_lon"]
                # Convert polygon coordinates to decimal if in dms
                polygon = self.convert_polygon_to_decimal(polygon)
                bounding_box = self.get_bounding_box(polygon)
                overlapping_percentage = requested_data["overlapping_percentage"]
                altitude = requested_data["altitude"]

                # Calculate FOV
                coverage_vertical, coverage_horizontal = self.camera.get_fov(altitude)

                vertical_waypoints = self.generate_vertical_waypoints(
                    bounding_box, altitude, overlapping_percentage, coverage_vertical
                )
                horizontal_waypoints = self.generate_horizontal_waypoints(
                    bounding_box, altitude, overlapping_percentage, coverage_horizontal
                )

                # Now generate all points
                all_points = self.generate_all_points(vertical_waypoints, horizontal_waypoints)

                all_filter_points = self.filter_points(all_points, polygon)

                self.plot_waypoints(bounding_box, polygon, all_filter_points)

                flight_path = serializer.save(user=user, waypoints=all_filter_points)
                message = "Waypoints generated successfully"
                logger_info.info(f"{message} by {user.username}")
                return Response(
                    success_true_response(data={"id": flight_path.id, "waypoints": all_filter_points}, message=message),
                    status=status.HTTP_201_CREATED,
                )

            except ValidationError as e:
                error_detail = e.detail
                for field_name, errors in error_detail.items():
                    for error in errors:
                        message = str(error)
                        logger_error.error(message)
                        return Response(
                            success_false_response(message=message),
                            status=e.status_code,
                        )

        except Exception as e:
            message = str(e)
            logger_error.error(message)
            return Response(
                success_false_response(message="An unexpected error occurred. Please try again later."),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
