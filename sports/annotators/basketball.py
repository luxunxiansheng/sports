from typing import Optional, List

import cv2
import supervision as sv
import numpy as np

from sports.configs.basketball import BasketballCourtConfiguration

def draw_three_point_arc(
    image: np.ndarray,
    point1: Tuple[float, float],
    point2: Tuple[float, float],
    color: Tuple[int, int, int],
    config: Any,
    padding: int,
    scale: float,
    side: str = "left",
    thickness: int = 2,
) -> None:
    center_x = int(((point1[0] + point2[0]) / 2) * scale + padding)
    center_y = int(((point1[1] + point2[1]) / 2) * scale + padding)
    center = (center_x, center_y)

    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    angle = np.degrees(np.arctan2(dy, dx))

    radius_height = int((config.three_point_line_distance - config.end_to_rim_beginning) * scale)
    radius_width = int((config.width / 2 - config.side_to_3_point_line) * scale)
    axes = (radius_width, radius_height)

    if side == "left":
        start_angle, end_angle = 180, 360
    elif side == "right":
        start_angle, end_angle = 0, 180
    else:
        raise ValueError("side must be either 'left' or 'right'")

    cv2.ellipse(
        image,
        center=center,
        axes=axes,
        angle=angle,
        startAngle=start_angle,
        endAngle=end_angle,
        color=color,
        thickness=thickness,
    )


def draw_court(
    config: BasketballCourtConfiguration,
    background_color: sv.Color = sv.Color(224, 190, 139),
    line_color: sv.Color = sv.Color.WHITE,
    padding: int = 50,
    line_thickness: int = 4,
    scale: float = 0.2
) -> np.ndarray:
    """
    Draws a basketball court with specified dimensions, colors, and scale.

    Args:
        config (BasketballCourtConfiguration): Court configuration.
        background_color (sv.Color): Color of the court background.
        line_color (sv.Color): Color of the court lines.
        padding (int): Padding around the court image.
        line_thickness (int): Thickness of the court lines.
        point_radius (int): Radius of key points like center circle.
        scale (float): Scale factor to shrink/enlarge the court.

    Returns:
        np.ndarray: Image of the basketball court.
    """
    scaled_width = int(config.width * scale)
    scaled_length = int(config.length * scale)
    scaled_circle_radius = int(config.center_circle_radius * scale)
    #scaled_penalty_spot_distance = int(config.penalty_spot_distance * scale)

    pitch_image = np.ones(
        (scaled_width + 2 * padding,
         scaled_length + 2 * padding, 3),
        dtype=np.uint8
    ) * np.array(background_color.as_bgr(), dtype=np.uint8)

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


    # Draw baskets and arcs
    centre_circle_center = (
        int(config.end_to_rim_beginning *scale + padding),
        int(config.width*scale  // 2+ padding),

    )
    scaled_circle_radius = int(config.rim_diameter/2 * scale)
    scaled_arc_radius = int(config.restricted_area_radius * scale)


    # Basket
    cv2.circle(
        img=pitch_image,
        center=centre_circle_center,
        radius=scaled_circle_radius,
        color=line_color.as_bgr(),
        thickness=max(1, line_thickness // 2)
    )
    # Arc
    cv2.ellipse(
    img = pitch_image,
    center=centre_circle_center,
    angle = 90,
    axes=(scaled_arc_radius,scaled_arc_radius),
    startAngle=180,
    endAngle=360,
    color=line_color.as_bgr(),
    thickness=line_thickness
    )
    #Basket
    centre_circle_center = (
        int((config.length-config.end_to_rim_beginning) *scale + padding),
        int(config.width*scale  // 2+ padding),

    )

    cv2.circle(
        img=pitch_image,
        center=centre_circle_center,
        radius=scaled_circle_radius,
        color=line_color.as_bgr(),
        thickness=line_thickness
    )

    # Draw restricted area arcs
    cv2.ellipse(
    pitch_image,
    center=centre_circle_center,
    angle = 90,
    axes=(scaled_arc_radius,scaled_arc_radius),
    startAngle=0,
    endAngle=180,
    color=line_color.as_bgr(),
    thickness=line_thickness
    )

    draw_three_point_arc(pitch_image, config.vertices[10-2-1], config.vertices[11-2-1], line_color.as_bgr(), config, padding, scale,"left", thickness=line_thickness)
    draw_three_point_arc(pitch_image, config.vertices[31-6-1], config.vertices[32-6-1], line_color.as_bgr(), config, padding, scale,"right", thickness=line_thickness)


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
        pitch = draw_pitch(
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
        pitch = draw_pitch(
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
        pitch = draw_pitch(
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