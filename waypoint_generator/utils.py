import math
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)
logger_info = logging.getLogger("info")
logger_error = logging.getLogger("error")


def get_bounding_box(polygon):
    try:
        min_lat = min(point["latitude"] for point in polygon)
        max_lat = max(point["latitude"] for point in polygon)
        min_lon = min(point["longitude"] for point in polygon)
        max_lon = max(point["longitude"] for point in polygon)

        # Create the rectangle corners (assuming the rectangle is axis-aligned)
        bounding_box = [
            {"latitude": min_lat, "longitude": max_lon},
            {"latitude": max_lat, "longitude": max_lon},
            {"latitude": max_lat, "longitude": min_lon},
            {"latitude": min_lat, "longitude": min_lon},
            {"latitude": min_lat, "longitude": max_lon},
        ]
        logger_info.info(f'Bounding box generated {bounding_box}')

        return bounding_box
    except Exception as e:
        logger_error(f'Bounding box generating error {str(e)}')
        return []

#
# # Function to calculate distance between two lat/lon points using Haversine formula
# def haversine_distance(lat1, lon1, lat2, lon2):
#     R = 6371e3  # Earth radius in meters
#     phi1 = math.radians(lat1)
#     phi2 = math.radians(lat2)
#     delta_phi = math.radians(lat2 - lat1)
#     delta_lambda = math.radians(lon2 - lon1)
#
#     a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#
#     return R * c


# Function to move a point by a certain distance in meters

def dms_to_decimal(degrees, minutes, seconds):
    return degrees + (minutes / 60.0) + (seconds / 3600.0)


def horizontal_move_point(lat, lon, distance, bearing):
    R = 6371e3  # Earth radius in meters
    bearing = math.radians(bearing)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(distance / R) + math.cos(lat1) * math.sin(distance / R) * math.cos(bearing))
    lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(distance / R) * math.cos(lat1),
                             math.cos(distance / R) - math.sin(lat1) * math.sin(lat2))

    return math.degrees(lat2), math.degrees(lon2)


def generate_horizontal_waypoints(polygon, altitude, overlapping_percentage):
    # Constants
    FOV = 100.0  # Field of View in meters
    overlap_distance = FOV * (overlapping_percentage / 100.0)
    move_distance = FOV - overlap_distance
    start_move = abs((FOV/2) - overlap_distance)

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
    # while lat < max_lat:
    while lon > min_lon:
        waypoints.append({"latitude": lat, "longitude": lon})
        lat, lon = horizontal_move_point(lat, lon, move_distance, 270)  # Move left (west)
    return waypoints


def vertical_move_point(lat, lon, distance, bearing):
    R = 6371e3  # Earth radius in meters
    bearing = math.radians(bearing)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(distance / R) + math.cos(lat1) * math.sin(distance / R) * math.cos(bearing))
    lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(distance / R) * math.cos(lat1),
                             math.cos(distance / R) - math.sin(lat1) * math.sin(lat2))

    return math.degrees(lat2), math.degrees(lon2)


def generate_vertical_waypoints(polygon, altitude, overlapping_percentage):
    # Constants
    FOV = 100.0  # Field of View in meters
    overlap_distance = FOV * (overlapping_percentage / 100.0)
    move_distance = FOV - overlap_distance
    start_move = abs((FOV / 2) - overlap_distance)

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
    direction = 0  # 0 for upward, 180 for downward
    # while lon > min_lon:
    while (direction == 0 and lat < max_lat) or (direction == 180 and lat > min_lat):
        waypoints.append({"latitude": lat, "longitude": lon})
        lat, lon = vertical_move_point(lat, lon, move_distance, direction)
        # direction = 180 - direction
        # lon -= 0.00035972864236910596
        # lat, lon = vertical_move_point(lat, lon, overlap_distance, 90)

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

    return degrees, minutes, seconds


def generate_all_points(vertical_points, horizontal_points): 
    # Extract latitudes and longitudes
    vertical_latitudes = [point['latitude'] for point in vertical_points]
    horizontal_longitudes = [point['longitude'] for point in horizontal_points]

    ulta = False
    all_points = []
    
    fast_lat = vertical_latitudes[0]
    last_lat = vertical_latitudes[-1]

    for lon in horizontal_longitudes:
        if not ulta:
            for lat in vertical_latitudes:
                all_points.append({'latitude': lat, 'longitude': lon})
                if last_lat == lat:
                    ulta = True
        else:
            for lat in vertical_latitudes[::-1]:
                all_points.append({'latitude': lat, 'longitude': lon})
                if last_lat == lat:
                    ulta = False

    return all_points


def plot_waypoints(bounding_box, all_points):
    fig, ax = plt.subplots()

    # Extracting latitude and longitude from primary points
    all_points_latitudes = [point['latitude'] for point in all_points]
    all_points_longitudes = [point['longitude'] for point in all_points]

    # Plotting secondary points with a different color
    ax.plot(all_points_longitudes, all_points_latitudes, 'bo-', marker='s', label='all Points')

    # Extracting latitude and longitude from secondary points
    secondary_latitudes = [point['latitude'] for point in bounding_box]
    secondary_longitudes = [point['longitude'] for point in bounding_box]

    # Plotting secondary points with a different color
    ax.plot(secondary_longitudes, secondary_latitudes, 'ro-', marker='x', label='Secondary Points')

    # Adding labels and title
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Latitude and Longitude Points')
    ax.legend()

    # Show grid
    ax.grid(True)

    # Display the plot
    plt.show()



