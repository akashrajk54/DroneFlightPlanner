import math
import logging
import warnings
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

logger = logging.getLogger(__name__)
logger_info = logging.getLogger("info")
logger_error = logging.getLogger("error")


# Suppress specific warnings
warnings.filterwarnings(
    "ignore", message="marker is redundantly defined by the 'marker' " "keyword argument and the fmt string"
)
warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread will likely fail.")


def get_bounding_box(polygon):
    try:
        min_lat = min(point["latitude"] for point in polygon)
        max_lat = max(point["latitude"] for point in polygon)
        min_lon = min(point["longitude"] for point in polygon)
        max_lon = max(point["longitude"] for point in polygon)

        # Create the rectangle corners
        bounding_box = [
            {"latitude": min_lat, "longitude": max_lon},
            {"latitude": max_lat, "longitude": max_lon},
            {"latitude": max_lat, "longitude": min_lon},
            {"latitude": min_lat, "longitude": min_lon},
            {"latitude": min_lat, "longitude": max_lon},
        ]
        logger_info.info(f"Bounding box generated {bounding_box}")

        return bounding_box
    except Exception as e:
        logger_error(f"Bounding box generating error {str(e)}")
        return []


def dms_to_decimal(degrees, minutes, seconds):
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


def horizontal_move_point(lat, lon, distance, bearing):

    R = 6371e3  # Earth radius in meters
    bearing = math.radians(bearing)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(distance / R) + math.cos(lat1) * math.sin(distance / R) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(distance / R) * math.cos(lat1),
        math.cos(distance / R) - math.sin(lat1) * math.sin(lat2),
    )

    logger_info.info(f"Horizontal move point generated {math.degrees(lat2), math.degrees(lon2)}")
    return math.degrees(lat2), math.degrees(lon2)


def generate_horizontal_waypoints(polygon, altitude, overlapping_percentage, coverage_horizontal):
    FOV = coverage_horizontal
    overlap_distance = FOV * (overlapping_percentage / 100)
    move_distance = FOV - overlap_distance
    start_move = -(move_distance - abs((FOV / 2) - overlap_distance))
    # start_move = abs((FOV/2) - overlap_distance) # Use this if want to start from bounding box bottom point

    # Find the bounding box
    min_lat = min(point["latitude"] for point in polygon)
    max_lat = max(point["latitude"] for point in polygon)
    min_lon = min(point["longitude"] for point in polygon)
    max_lon = max(point["longitude"] for point in polygon)

    # Find the start point (right-bottom corner)
    right_bottom = {"latitude": min_lat, "longitude": max_lon}
    start_lat, start_lon = horizontal_move_point(right_bottom["latitude"], right_bottom["longitude"], start_move, 0)
    start_lat, start_lon = horizontal_move_point(start_lat, start_lon, start_move, 270)

    # Generate waypoints
    waypoints = []
    lat, lon = start_lat, start_lon

    min_lat, min_lon = vertical_move_point(min_lat, min_lon, move_distance, 270)
    while lon > min_lon:
        waypoints.append({"latitude": lat, "longitude": lon})
        lat, lon = horizontal_move_point(lat, lon, move_distance, 270)  # Move left (west)

    logger_info.info("Horizontal waypoint generated")
    return waypoints


def vertical_move_point(lat, lon, distance, bearing):
    R = 6371e3  # Earth radius in meters
    bearing = math.radians(bearing)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(distance / R) + math.cos(lat1) * math.sin(distance / R) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(distance / R) * math.cos(lat1),
        math.cos(distance / R) - math.sin(lat1) * math.sin(lat2),
    )

    logger_info.info(f"Vertical move point generated {math.degrees(lat2), math.degrees(lon2)}")
    return math.degrees(lat2), math.degrees(lon2)


def generate_vertical_waypoints(polygon, altitude, overlapping_percentage, coverage_vertical):
    FOV = coverage_vertical
    overlap_distance = FOV * (overlapping_percentage / 100)
    move_distance = FOV - overlap_distance
    start_move = -(move_distance - abs((FOV / 2) - overlap_distance))
    # start_move = abs((FOV / 2) - overlap_distance)

    # Find the bounding box
    min_lat = min(point["latitude"] for point in polygon)
    max_lat = max(point["latitude"] for point in polygon)
    min_lon = min(point["longitude"] for point in polygon)
    max_lon = max(point["longitude"] for point in polygon)

    # Find the start point (right-bottom corner)
    right_bottom = {"latitude": min_lat, "longitude": max_lon}
    begin_lat, begin_lon = vertical_move_point(right_bottom["latitude"], right_bottom["longitude"], start_move, 0)
    begin_lat, begin_lon = vertical_move_point(begin_lat, begin_lon, start_move, 270)

    # Generate waypoints
    waypoints = []
    lat, lon = begin_lat, begin_lon
    direction = 0  # 0 for upward
    max_lat, max_lon = vertical_move_point(max_lat, max_lon, move_distance, direction)

    while lat <= max_lat:
        waypoints.append({"latitude": lat, "longitude": lon})
        lat, lon = vertical_move_point(lat, lon, move_distance, direction)

    logger_info.info("Vertical waypoint generated")
    return waypoints


def decimal_to_dms(decimal_degrees):
    is_positive = decimal_degrees >= 0
    decimal_degrees = abs(decimal_degrees)

    degrees = int(decimal_degrees)
    minutes_float = (decimal_degrees - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60

    if not is_positive:
        degrees = -degrees

    logger_info.info(f"decimal to dsm {degrees, minutes, seconds}")
    return degrees, minutes, seconds


def generate_all_points(vertical_points, horizontal_points):
    # Extract latitudes and longitudes
    vertical_latitudes = [point["latitude"] for point in vertical_points]
    horizontal_longitudes = [point["longitude"] for point in horizontal_points]

    reverse = False
    all_points = []

    first_lat = vertical_latitudes[0]
    last_lat = vertical_latitudes[-1]

    for lon in horizontal_longitudes:
        if not reverse:
            for lat in vertical_latitudes:
                all_points.append({"latitude": lat, "longitude": lon})
                if last_lat == lat:
                    reverse = True
        else:
            for lat in vertical_latitudes[::-1]:
                all_points.append({"latitude": lat, "longitude": lon})
                if last_lat == lat:
                    reverse = False

    logger_info.info("All waypoint generated")
    return all_points


def plot_waypoints(bounding_box, polygon, all_points):
    fig, ax = plt.subplots()

    # Extracting latitude and longitude from all points
    all_points_latitudes = [point["latitude"] for point in all_points]
    all_points_longitudes = [point["longitude"] for point in all_points]

    # Plotting all points
    ax.plot(all_points_longitudes, all_points_latitudes, "bo-", marker="s", label="Drone waypoints")

    # Extracting latitude and longitude from bounding box points
    bounding_box_latitudes = [point["latitude"] for point in bounding_box]
    bounding_box_longitudes = [point["longitude"] for point in bounding_box]

    # Plotting bounding box points with a different color
    ax.plot(bounding_box_longitudes, bounding_box_latitudes, "ro-", marker="x", label="Bounding box")

    # Extracting latitude and longitude from user polygon points
    if polygon[0] != polygon[-1]:
        polygon.append(polygon[0])
    polygon_latitudes = [point["latitude"] for point in polygon]
    polygon_longitudes = [point["longitude"] for point in polygon]

    # Plotting user polygon points
    ax.plot(polygon_longitudes, polygon_latitudes, "gs-", marker="o", label="User polygon")

    # Adding labels and title
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Drone waypoints to cover whole polygon")
    ax.legend()

    # Show grid
    ax.grid(True)

    # Display the plot
    plt.show()


def dms_to_decimal(dms_str):
    # Example input: "23d48m35sN" or "86d41m24sE"
    degrees, minutes, seconds = 0, 0, 0.0
    if "d" in dms_str:
        degrees, dms_str = dms_str.split("d")
        degrees = int(degrees)
    if "m" in dms_str:
        minutes, dms_str = dms_str.split("m")
        minutes = int(minutes)
    if "s" in dms_str:
        seconds = float(dms_str.strip("sNSEW"))

    decimal_value = degrees + minutes / 60 + seconds / 3600

    # Adjust for direction
    if "S" in dms_str or "W" in dms_str:
        decimal_value = -decimal_value

    return decimal_value


def convert_polygon_to_decimal(polygon):
    converted_polygon = []
    for point in polygon:
        latitude = point["latitude"]
        longitude = point["longitude"]
        if isinstance(latitude, str) and "d" in latitude:
            latitude = dms_to_decimal(latitude)
        if isinstance(longitude, str) and "d" in longitude:
            longitude = dms_to_decimal(longitude)
        converted_polygon.append({"latitude": latitude, "longitude": longitude})
    return converted_polygon


def calculate_average_distance(points):
    distances = []
    for i in range(1, len(points)):
        prev_point = points[i - 1]
        curr_point = points[i]
        distance = (
            (curr_point["latitude"] - prev_point["latitude"]) ** 2
            + (curr_point["longitude"] - prev_point["longitude"]) ** 2
        ) ** 0.5
        distances.append(distance)
    return sum(distances) / len(distances) if distances else 0


def is_point_just_outside(polygon, point, buffer_distance):
    buffered_polygon = polygon.buffer(buffer_distance)
    return buffered_polygon.contains(point) and not polygon.contains(point)


def filter_points(points, polygon_coords):
    buffer_distance = calculate_average_distance(points)
    polygon = Polygon([(p["longitude"], p["latitude"]) for p in polygon_coords])
    inside_points = []
    just_outside_points = []

    for p in points:
        point = Point(p["longitude"], p["latitude"])
        if polygon.contains(point):
            inside_points.append(p)
        elif is_point_just_outside(polygon, point, buffer_distance):
            inside_points.append(p)

    return inside_points
