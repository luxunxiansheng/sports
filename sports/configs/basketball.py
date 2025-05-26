from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class BasketballCourtConfiguration:
    # court dimensions [cm]
    court_width_cm: int = 1524
    court_length_cm: int = 2865

    # three-point line distances [cm]
    three_point_arc_radius_cm: int = 724
    straight_section_three_point_line_cm: int = 424

    # key (paint) dimensions [cm]
    paint_width_cm: int = 488
    paint_length_cm: int = 579
    free_throw_line_distance_cm: int = 457

    # center circle and restricted area [cm]
    center_circle_radius_cm: int = 183
    restricted_area_radius_cm: int = 122

    # rim [cm]
    rim_diameter_cm: int = 46

    # other offsets [cm]
    sideline_to_three_point_line_cm: float = 91
    baseline_to_rim_center_cm: int = 160
    baseline_to_throw_line_cm: int = 835
    baseline_to_throw_line_length_cm: int = 50

    @property
    def vertices(self) -> List[Tuple[int, int]]:
        paint_start_cm = (self.court_width_cm - self.paint_width_cm) // 2
        return [
            (0, 0),  # 1
            (0, self.sideline_to_three_point_line_cm),  # 2
            (0, paint_start_cm),  # 4
            (0, paint_start_cm + self.paint_width_cm),  # 5
            (0, self.court_width_cm - self.sideline_to_three_point_line_cm),  # 7
            (0, self.court_width_cm),  # 8
            (self.baseline_to_rim_center_cm, self.court_width_cm // 2),  # 9
            (self.straight_section_three_point_line_cm,
             self.sideline_to_three_point_line_cm),  # 10
            (self.straight_section_three_point_line_cm,
             self.court_width_cm - self.sideline_to_three_point_line_cm),  # 11
            (self.paint_length_cm, paint_start_cm),  # 12
            (self.paint_length_cm, paint_start_cm + self.paint_width_cm // 2),  # 13
            (self.paint_length_cm, paint_start_cm + self.paint_width_cm),  # 14
            (self.baseline_to_throw_line_cm, 0),  # 15
            (self.baseline_to_rim_center_cm + self.three_point_arc_radius_cm,
             self.court_width_cm // 2),  # 16
            (self.baseline_to_throw_line_cm, self.court_width_cm),  # 17

            (self.court_length_cm // 2, 0),  # 19
            (self.court_length_cm // 2, self.court_width_cm // 2),  # 21
            (self.court_length_cm // 2, self.court_width_cm),  # 23

            (self.court_length_cm - self.baseline_to_throw_line_cm, 0),  # 25
            (
            self.court_length_cm - self.baseline_to_rim_center_cm - self.three_point_arc_radius_cm,
            self.court_width_cm // 2),  # 26
            (
            self.court_length_cm - self.baseline_to_throw_line_cm, self.court_width_cm),
            # 27
            (self.court_length_cm - self.paint_length_cm, paint_start_cm),  # 28
            (self.court_length_cm - self.paint_length_cm,
             paint_start_cm + self.paint_width_cm // 2),  # 29
            (self.court_length_cm - self.paint_length_cm,
             paint_start_cm + self.paint_width_cm),  # 30
            (self.court_length_cm - self.straight_section_three_point_line_cm,
             self.sideline_to_three_point_line_cm),  # 31
            (self.court_length_cm - self.straight_section_three_point_line_cm,
             self.court_width_cm - self.sideline_to_three_point_line_cm),  # 32
            (self.court_length_cm - self.baseline_to_rim_center_cm,
             self.court_width_cm // 2),  # 33
            (self.court_length_cm, 0),  # 34
            (self.court_length_cm, self.sideline_to_three_point_line_cm),  # 35
            (self.court_length_cm, paint_start_cm),  # 37
            (self.court_length_cm, paint_start_cm + self.paint_width_cm),  # 38
            (self.court_length_cm,
             self.court_width_cm - self.sideline_to_three_point_line_cm),  # 40
            (self.court_length_cm, self.court_width_cm),  # 41
        ]

    edges: List[Tuple[int, int]] = field(default_factory=lambda: [
        # left line
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 5),
        # left key
        (2, 9), (11, 3), (9, 10), (10, 11),
        # left 3pt line borders
        (1, 7), (4, 8),
        # top border
        (0, 12), (12, 15), (15, 18), (18, 27),
        # center line
        (15, 16), (16, 17),
        # bottom border
        (5, 14), (14, 17), (17, 20), (20, 32),
        # right line
        (27, 28), (28, 29), (29, 30), (30, 31), (31, 32),
        # right 3pt line borders
        (25, 31), (28, 24),
        # right line
        (29, 21), (21, 22), (22, 23), (23, 30)
    ])

    labels: List[str] = field(default_factory=lambda: [
        "01", "02", "04", "05", "07", "08",
        "09", "10", "11", "12", "13", "14",
        "15", "16", "17", "19", "21", "23",
        "25", "26", "27", "28", "29", "30",
        "31", "32", "33", "34", "35", "37",
        "38", "40", "41"
    ])

    colors: List[str] = field(default_factory=lambda: [
        "#A4F84B", "#FF1493", "#FF1493", "#FF1493", "#FF1493", "#00BFFF",
        "#FF1493", "#FF1493", "#FF1493", "#FF1493", "#FF1493", "#FF1493",
        "#A4F84B", "#FF1493", "#00BFFF", "#A4F84B", "#A849F1", "#00BFFF",
        "#A4F84B", "#52F8C4", "#00BFFF", "#52F8C4", "#52F8C4", "#52F8C4",
        "#52F8C4", "#52F8C4", "#52F8C4", "#A4F84B", "#52F8C4", "#52F8C4",
        "#52F8C4", "#52F8C4", "#00BFFF"
    ])
