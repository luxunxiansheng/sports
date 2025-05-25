from typing import Optional, List, Tuple, Any

import cv2
import supervision as sv
import numpy as np

from sports.configs.basketball import BasketballCourtConfiguration

# def draw_three_point_arc(
#     image: np.ndarray,
#     point1: Tuple[float, float],
#     point2: Tuple[float, float],
#     color: Tuple[int, int, int],
#     config: Any,
#     padding: int,
#     scale: float,
#     side: str = "left",
#     thickness: int = 2,
# ) -> None:
#     center_x = int(((point1[0] + point2[0]) / 2) * scale + padding)
#     center_y = int(((point1[1] + point2[1]) / 2) * scale + padding)
#     center = (center_x, center_y)
#
#     dx = point2[0] - point1[0]
#     dy = point2[1] - point1[1]
#     angle = np.degrees(np.arctan2(dy, dx))
#
#     radius_height = int((config.three_point_arc_radius_cm - config.baseline_to_rim_start_cm) * scale)
#     radius_width = int((config.court_width_cm / 2 - config.sideline_to_three_point_line_cm) * scale)
#     axes = (radius_width, radius_height)
#
#     if side == "left":
#         start_angle, end_angle = 180, 360
#     elif side == "right":
#         start_angle, end_angle = 0, 180
#     else:
#         raise ValueError("side must be either 'left' or 'right'")
#
#     cv2.ellipse(
#         image,
#         center=center,
#         axes=axes,
#         angle=angle,
#         startAngle=start_angle,
#         endAngle=end_angle,
#         color=color,
#         thickness=thickness,
#     )


def draw_arc_from_points(
    image: np.ndarray,
    point_a: Tuple[float, float],
    point_b: Tuple[float, float],
    point_c: Tuple[float, float],
    color: Tuple[int, int, int],
    thickness: int = 2,
) -> None:
    """
    Draw an arc on the image from point_a to point_c passing through point_b.
    """

    def compute_circle_center_and_radius(
        point1: Tuple[float, float],
        point2: Tuple[float, float],
        point3: Tuple[float, float]
    ) -> Tuple[Tuple[float, float], float]:
        temp_sum_squares = point2[0] ** 2 + point2[1] ** 2
        first_term = (point1[0] ** 2 + point1[1] ** 2 - temp_sum_squares) / 2.0
        second_term = (temp_sum_squares - point3[0] ** 2 - point3[1] ** 2) / 2.0
        determinant = (
            (point1[0] - point2[0]) * (point2[1] - point3[1]) -
            (point2[0] - point3[0]) * (point1[1] - point2[1])
        )

        if abs(determinant) < 1e-10:
            raise ValueError("Points are collinear")

        center_x = (
            first_term * (point2[1] - point3[1]) -
            second_term * (point1[1] - point2[1])
        ) / determinant

        center_y = (
            (point1[0] - point2[0]) * second_term -
            (point2[0] - point3[0]) * first_term
        ) / determinant

        radius = np.sqrt((center_x - point1[0]) ** 2 + (center_y - point1[1]) ** 2)

        return (center_x, center_y), radius

    circle_center, radius = compute_circle_center_and_radius(point_a, point_b, point_c)
    circle_center_int = (int(circle_center[0]), int(circle_center[1]))
    radius_int = int(radius)

    def compute_angle_in_degrees(
        center: Tuple[float, float], point: Tuple[float, float]
    ) -> float:
        return np.degrees(np.arctan2(point[1] - center[1], point[0] - center[0]))

    angle_start = compute_angle_in_degrees(circle_center, point_a)
    angle_mid = compute_angle_in_degrees(circle_center, point_b)
    angle_end = compute_angle_in_degrees(circle_center, point_c)

    angles_array = np.array([angle_start, angle_mid, angle_end])
    angles_array = np.mod(angles_array, 360)

    if ((angles_array[1] - angles_array[0]) % 360) > ((angles_array[2] - angles_array[0]) % 360):
        start_angle, end_angle = angles_array[0], angles_array[2]
    else:
        start_angle, end_angle = angles_array[2], angles_array[0]

    cv2.ellipse(
        image,
        center=circle_center_int,
        axes=(radius_int, radius_int),
        angle=0,
        startAngle=start_angle,
        endAngle=end_angle,
        color=color,
        thickness=thickness,
    )


# def draw_court(
#     config: Any,
#     background_color: sv.Color = sv.Color(224, 190, 139),
#     line_color: sv.Color = sv.Color.WHITE,
#     padding: int = 50,
#     line_thickness: int = 4,
#     scale: float = 0.2
# ) -> np.ndarray:
#     """
#     Draws a basketball court with specified dimensions, colors, and scale.
#     """
#     scaled_width = int(config.court_width_cm * scale)
#     scaled_length = int(config.court_length_cm * scale)
#     scaled_circle_radius = int(config.center_circle_radius_cm * scale)
#
#     pitch_image = np.ones(
#         (scaled_width + 2 * padding,
#          scaled_length + 2 * padding, 3),
#         dtype=np.uint8
#     ) * np.array(background_color.as_bgr(), dtype=np.uint8)
#
#     # Draw court lines
#     for start, end in config.edges:
#         point1 = (int(config.vertices[start - 1][0] * scale) + padding,
#                   int(config.vertices[start - 1][1] * scale) + padding)
#         point2 = (int(config.vertices[end - 1][0] * scale) + padding,
#                   int(config.vertices[end - 1][1] * scale) + padding)
#         cv2.line(
#             img=pitch_image,
#             pt1=point1,
#             pt2=point2,
#             color=line_color.as_bgr(),
#             thickness=line_thickness
#         )
#
#     # Draw center circle
#     centre_circle_center = (
#         scaled_length // 2 + padding,
#         scaled_width // 2 + padding
#     )
#     cv2.circle(
#         img=pitch_image,
#         center=centre_circle_center,
#         radius=scaled_circle_radius,
#         color=line_color.as_bgr(),
#         thickness=line_thickness
#     )
#
#     # Draw baskets and arcs (left and right)
#     for side in ["left", "right"]:
#         if side == "left":
#             basket_x = int(config.baseline_to_rim_start_cm * scale + padding)
#         else:
#             basket_x = int((config.court_length_cm - config.baseline_to_rim_start_cm) * scale + padding)
#         basket_y = int(config.court_width_cm * scale // 2 + padding)
#         basket_center = (basket_x, basket_y)
#
#         scaled_rim_radius = int(config.rim_diameter_cm / 2 * scale)
#         scaled_restricted_arc_radius = int(config.restricted_area_radius_cm * scale)
#
#         # Basket (rim)
#         cv2.circle(
#             img=pitch_image,
#             center=basket_center,
#             radius=scaled_rim_radius,
#             color=line_color.as_bgr(),
#             thickness=max(1, line_thickness // 2)
#         )
#         # Restricted area arc
#         if side == "left":
#             start_angle, end_angle = 180, 360
#         else:
#             start_angle, end_angle = 0, 180
#
#         cv2.ellipse(
#             img=pitch_image,
#             center=basket_center,
#             angle=90,
#             axes=(scaled_restricted_arc_radius, scaled_restricted_arc_radius),
#             startAngle=start_angle,
#             endAngle=end_angle,
#             color=line_color.as_bgr(),
#             thickness=line_thickness
#         )
#
#     # Draw three-point arcs
#     # These vertex indices might need to be rechecked if you change the layout
#     left_arc_points = (config.vertices[7], config.vertices[8])   # Indices for left arc ends
#     right_arc_points = (config.vertices[24], config.vertices[25])  # Indices for right arc ends
#
#     draw_three_point_arc(
#         pitch_image,
#         left_arc_points[0],
#         left_arc_points[1],
#         line_color.as_bgr(),
#         config,
#         padding,
#         scale,
#         side="left",
#         thickness=line_thickness
#     )
#
#     draw_three_point_arc(
#         pitch_image,
#         right_arc_points[0],
#         right_arc_points[1],
#         line_color.as_bgr(),
#         config,
#         padding,
#         scale,
#         side="right",
#         thickness=line_thickness
#     )
#
#     return pitch_image


def draw_court(
    config: Any,
    background_color: sv.Color = sv.Color(224, 190, 139),
    line_color: sv.Color = sv.Color.WHITE,
    padding: int = 50,
    line_thickness: int = 4,
    scale: float = 0.2
) -> np.ndarray:
    """
    Draws a basketball court with specified dimensions, colors, and scale.
    """
    scaled_width = int(config.court_width_cm * scale)
    scaled_length = int(config.court_length_cm * scale)
    scaled_circle_radius = int(config.center_circle_radius_cm * scale)

    pitch_image = np.ones(
        (scaled_width + 2 * padding,
         scaled_length + 2 * padding, 3),
        dtype=np.uint8
    ) * np.array(background_color.as_bgr(), dtype=np.uint8)

    # Draw court lines
    for start, end in config.edges:
        point1 = (int(config.vertices[start - 1][0] * scale) + padding,
                  int(config.vertices[start - 1][1] * scale) + padding)
        point2 = (int(config.vertices[end - 1][0] * scale) + padding,
                  int(config.vertices[end - 1][1] * scale) + padding)
        cv2.line(
            img=pitch_image,
            pt1=point1,
            pt2=point2,
            color=line_color.as_bgr(),
            thickness=line_thickness
        )

    # Draw center circle
    centre_circle_center = (
        scaled_length // 2 + padding,
        scaled_width // 2 + padding
    )
    cv2.circle(
        img=pitch_image,
        center=centre_circle_center,
        radius=scaled_circle_radius,
        color=line_color.as_bgr(),
        thickness=line_thickness
    )

    # Draw baskets and restricted arcs (left and right)
    for side in ["left", "right"]:
        basket_x = (
            int(config.baseline_to_rim_start_cm * scale + padding)
            if side == "left"
            else int((config.court_length_cm - config.baseline_to_rim_start_cm) * scale + padding)
        )
        basket_y = int(config.court_width_cm * scale // 2 + padding)
        basket_center = (basket_x, basket_y)

        scaled_rim_radius = int(config.rim_diameter_cm / 2 * scale)
        scaled_restricted_arc_radius = int(config.restricted_area_radius_cm * scale)

        cv2.circle(
            img=pitch_image,
            center=basket_center,
            radius=scaled_rim_radius,
            color=line_color.as_bgr(),
            thickness=max(1, line_thickness // 2)
        )

        start_angle, end_angle = (180, 360) if side == "left" else (0, 180)

        cv2.ellipse(
            img=pitch_image,
            center=basket_center,
            angle=90,
            axes=(scaled_restricted_arc_radius, scaled_restricted_arc_radius),
            startAngle=start_angle,
            endAngle=end_angle,
            color=line_color.as_bgr(),
            thickness=line_thickness
        )

    # Draw three-point arcs using the generalized method
    left_arc_points = [config.vertices[i] for i in [7, 15, 8]]
    right_arc_points = [config.vertices[i] for i in [24, 20, 25]]

    scaled_left_arc_points = [(x * scale + padding, y * scale + padding) for x, y in left_arc_points]
    scaled_right_arc_points = [(x * scale + padding, y * scale + padding) for x, y in right_arc_points]

    draw_arc_from_points(
        pitch_image,
        *scaled_left_arc_points,
        line_color.as_bgr(),
        thickness=line_thickness
    )

    draw_arc_from_points(
        pitch_image,
        *scaled_right_arc_points,
        line_color.as_bgr(),
        thickness=line_thickness
    )

    return pitch_image



def draw_points_on_pitch(
    config: BasketballCourtConfiguration,
    xy: np.ndarray,
    face_color: sv.Color = sv.Color.RED,
    edge_color: sv.Color = sv.Color.BLACK,
    radius: int = 10,
    thickness: int = 2,
    padding: int = 50,
    scale: float = 0.1,
    pitch: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Draws points on a soccer pitch.

    Args:
        config (BasketballCourtConfiguration): Configuration object containing the
            dimensions and layout of the pitch.
        xy (np.ndarray): Array of points to be drawn, with each point represented by
            its (x, y) coordinates.
        face_color (sv.Color, optional): Color of the point faces.
            Defaults to sv.Color.RED.
        edge_color (sv.Color, optional): Color of the point edges.
            Defaults to sv.Color.BLACK.
        radius (int, optional): Radius of the points in pixels.
            Defaults to 10.
        thickness (int, optional): Thickness of the point edges in pixels.
            Defaults to 2.
        padding (int, optional): Padding around the pitch in pixels.
            Defaults to 50.
        scale (float, optional): Scaling factor for the pitch dimensions.
            Defaults to 0.1.
        pitch (Optional[np.ndarray], optional): Existing pitch image to draw points on.
            If None, a new pitch will be created. Defaults to None.

    Returns:
        np.ndarray: Image of the soccer pitch with points drawn on it.
    """
    if pitch is None:
        pitch = draw_court(
            config=config,
            padding=padding,
            scale=scale
        )

    for point in xy:
        scaled_point = (
            int(point[0] * scale) + padding,
            int(point[1] * scale) + padding
        )
        cv2.circle(
            img=pitch,
            center=scaled_point,
            radius=radius,
            color=face_color.as_bgr(),
            thickness=-1
        )
        cv2.circle(
            img=pitch,
            center=scaled_point,
            radius=radius,
            color=edge_color.as_bgr(),
            thickness=thickness
        )

    return pitch


def draw_paths_on_pitch(
    config: BasketballCourtConfiguration,
    paths: List[np.ndarray],
    color: sv.Color = sv.Color.WHITE,
    thickness: int = 2,
    padding: int = 50,
    scale: float = 0.1,
    pitch: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Draws paths on a soccer pitch.

    Args:
        config (BasketballCourtConfiguration): Configuration object containing the
            dimensions and layout of the pitch.
        paths (List[np.ndarray]): List of paths, where each path is an array of (x, y)
            coordinates.
        color (sv.Color, optional): Color of the paths.
            Defaults to sv.Color.WHITE.
        thickness (int, optional): Thickness of the paths in pixels.
            Defaults to 2.
        padding (int, optional): Padding around the pitch in pixels.
            Defaults to 50.
        scale (float, optional): Scaling factor for the pitch dimensions.
            Defaults to 0.1.
        pitch (Optional[np.ndarray], optional): Existing pitch image to draw paths on.
            If None, a new pitch will be created. Defaults to None.

    Returns:
        np.ndarray: Image of the soccer pitch with paths drawn on it.
    """
    if pitch is None:
        pitch = draw_court(
            config=config,
            padding=padding,
            scale=scale
        )

    for path in paths:
        scaled_path = [
            (
                int(point[0] * scale) + padding,
                int(point[1] * scale) + padding
            )
            for point in path if point.size > 0
        ]

        if len(scaled_path) < 2:
            continue

        for i in range(len(scaled_path) - 1):
            cv2.line(
                img=pitch,
                pt1=scaled_path[i],
                pt2=scaled_path[i + 1],
                color=color.as_bgr(),
                thickness=thickness
            )

        return pitch


def draw_pitch_voronoi_diagram(
    config: BasketballCourtConfiguration,
    team_1_xy: np.ndarray,
    team_2_xy: np.ndarray,
    team_1_color: sv.Color = sv.Color.RED,
    team_2_color: sv.Color = sv.Color.WHITE,
    opacity: float = 0.5,
    padding: int = 50,
    scale: float = 0.1,
    pitch: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Draws a Voronoi diagram on a soccer pitch representing the control areas of two
    teams.

    Args:
        config (BasketballCourtConfiguration): Configuration object containing the
            dimensions and layout of the pitch.
        team_1_xy (np.ndarray): Array of (x, y) coordinates representing the positions
            of players in team 1.
        team_2_xy (np.ndarray): Array of (x, y) coordinates representing the positions
            of players in team 2.
        team_1_color (sv.Color, optional): Color representing the control area of
            team 1. Defaults to sv.Color.RED.
        team_2_color (sv.Color, optional): Color representing the control area of
            team 2. Defaults to sv.Color.WHITE.
        opacity (float, optional): Opacity of the Voronoi diagram overlay.
            Defaults to 0.5.
        padding (int, optional): Padding around the pitch in pixels.
            Defaults to 50.
        scale (float, optional): Scaling factor for the pitch dimensions.
            Defaults to 0.1.
        pitch (Optional[np.ndarray], optional): Existing pitch image to draw the
            Voronoi diagram on. If None, a new pitch will be created. Defaults to None.

    Returns:
        np.ndarray: Image of the soccer pitch with the Voronoi diagram overlay.
    """
    if pitch is None:
        pitch = draw_court(
            config=config,
            padding=padding,
            scale=scale
        )

    scaled_width = int(config.width * scale)
    scaled_length = int(config.length * scale)

    voronoi = np.zeros_like(pitch, dtype=np.uint8)

    team_1_color_bgr = np.array(team_1_color.as_bgr(), dtype=np.uint8)
    team_2_color_bgr = np.array(team_2_color.as_bgr(), dtype=np.uint8)

    y_coordinates, x_coordinates = np.indices((
        scaled_width + 2 * padding,
        scaled_length + 2 * padding
    ))

    y_coordinates -= padding
    x_coordinates -= padding

    def calculate_distances(xy, x_coordinates, y_coordinates):
        return np.sqrt((xy[:, 0][:, None, None] * scale - x_coordinates) ** 2 +
                       (xy[:, 1][:, None, None] * scale - y_coordinates) ** 2)

    distances_team_1 = calculate_distances(team_1_xy, x_coordinates, y_coordinates)
    distances_team_2 = calculate_distances(team_2_xy, x_coordinates, y_coordinates)

    min_distances_team_1 = np.min(distances_team_1, axis=0)
    min_distances_team_2 = np.min(distances_team_2, axis=0)

    control_mask = min_distances_team_1 < min_distances_team_2

    voronoi[control_mask] = team_1_color_bgr
    voronoi[~control_mask] = team_2_color_bgr

    overlay = cv2.addWeighted(voronoi, opacity, pitch, 1 - opacity, 0)

    return overlay