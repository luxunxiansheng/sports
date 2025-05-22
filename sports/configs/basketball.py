from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class BasketballCourtConfiguration: #NBA Court
    width: int = 1524   # [cm]
    length: int = 2865  # [cm]
    three_point_line_distance: int = 853  # [cm] - 23.75 feet from the basket
    three_point_line_distance_corner: int = 670  # [cm] - 22 feet from the basket in the corners
    free_throw_line_distance: int = 457  # [cm] - 15 feet from the backboard
    key_width: int = 488  # [cm] - 16 feet
    key_length: int = 579  # [cm] - 19 feet from baseline to free-throw line
    center_circle_radius: int = 183  # [cm] - 6 feet
    restricted_area_radius: int = 122  # [cm] - 4 feet
    backboard_width: int = 183  # [cm] - 6 feet
    backboard_height: int = 107  # [cm] - 3.5 feet
    rim_height: int = 305  # [cm] - 10 feet
    rim_diameter: int = 46  # [cm] - 18 inches
    side_to_3_point_line: float = 91.44 # [cm]
    end_to_rim_beginning = 125 # [cm]
    @property
    def vertices(self) -> List[Tuple[int, int]]:

        distance_3_to_4 =  (self.width - 2* self.side_to_3_point_line  - 3*self.key_width )//2
        start_key = self.side_to_3_point_line + self.key_width + distance_3_to_4
        return [
            (0, 0),  # 1    
            (0, self.side_to_3_point_line),  # 2
            #(0, self.side_to_3_point_line+ self.key_width),  # 3 Deprecated
            (0, start_key),  # 4
            (0, start_key+self.key_width),  # 5
            #(0, start_key+self.key_width+ distance_3_to_4),  # 6 Deprecated
            (0, self.width -self.side_to_3_point_line),  # 7
            (0, self.width),  # 8
            (self.end_to_rim_beginning, self.width / 2),  # 9
            (self.end_to_rim_beginning, self.side_to_3_point_line),  # 10
            (self.end_to_rim_beginning, (self.width - self.side_to_3_point_line) ),  # 11
            (self.key_length, start_key) ,  # 12
            (self.key_length, start_key+ self.key_width//2),  # 13
            (self.key_length, start_key+self.key_width),  # 14
            (self.three_point_line_distance, 0),  # 15
            (self.three_point_line_distance, self.width//2),  # 16

            (self.three_point_line_distance, self.width),  # 17

            #(self.length//2 - self.center_circle_radius,  self.width  // 2),  # 18 Deprecated
            
            (self.length //2, 0),  # 19
            #(self.length //2, self.width//2-self.center_circle_radius),  # 20 Deprecated
            (self.length //2, self.width//2),  # 21
            #(self.length //2, self.width//2+self.center_circle_radius),  # 22 Deprecated
            (self.length //2, self.width),  # 23
            #(self.length//2 + self.center_circle_radius,  self.width  / 2),  # 24 Deprecated
            (self.length - self.three_point_line_distance, 0),  # 25
            (self.length - self.three_point_line_distance, self.width//2),  # 26
            (self.length - self.three_point_line_distance, self.width),  # 27
            (self.length- self.key_length, start_key) ,  # 28
            (self.length-self.key_length, start_key+ self.key_width//2),  # 29
            (self.length-self.key_length, start_key+self.key_width),  # 30
            (self.length-self.end_to_rim_beginning, self.side_to_3_point_line),  # 31
            (self.length-self.end_to_rim_beginning, (self.width - self.side_to_3_point_line) ),  # 32
            (self.length-self.end_to_rim_beginning, self.width / 2),  # 33


            (self.length, 0),  # 34  
            (self.length, self.side_to_3_point_line),  # 35
            #(self.length, self.side_to_3_point_line+ self.key_width),  # 36 Deprecated
            (self.length, start_key),  # 37
            (self.length, start_key+self.key_width),  # 38
            #(self.length, start_key+self.key_width+ distance_3_to_4),  # 39 Deprecated
            (self.length, self.width -self.side_to_3_point_line),  # 40
            (self.length, self.width),  # 41
        ]

    edges: List[Tuple[int, int]] = field(default_factory=lambda: [(1, 2), (2,3),(3, 4),(4,5), (5, 6), # Left Line
                                                                  (3, 10), (12, 4), (10, 11), (11, 12),# Left Key
                                                                  (2, 8), (5, 9), # Left 3 point line borders
                                                                  (1, 13), (13, 16), (16, 19), (19, 28), # Top border
                                                                  (16,17), (17,18), # Center line
                                                                  (6, 15), (15, 18), (18, 21), (21, 33), # Bottom border
                                                                  (28, 29), (29,30), (30, 31), (31,32), (32, 33), #Right line
                                                                  (26, 32), (29, 25), # Right 3 point line borders
                                                                  (30, 22), (22, 23), (23, 24), (24, 31)]) # Right line

    labels: List[str] = field(default_factory=lambda: [
        "01", "02", "04", "05", "07", "08", "09", "10",
        "11", "12", "13", "14","15", "16", "17", "19",  "21", 
        "23", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34",
        "35", "37", "38", "40", "41"
    ])

    colors: List[str] = field(default_factory=lambda: [
        "#A4F84B", "#FF1493", "#FF1493", "#FF1493", "#FF1493","#00BFFF",
        "#FF1493", "#FF1493", "#FF1493",
        "#FF1493", "#FF1493", "#FF1493",
        "#A4F84B", "#FF1493", "#00BFFF",
        "#A4F84B", "#A849F1", "#00BFFF",
        "#A4F84B", "#52F8C4", "#00BFFF",
        "#52F8C4", "#52F8C4", "#52F8C4",
        "#52F8C4", "#52F8C4", "#52F8C4",
        "#A4F84B", "#52F8C4", "#52F8C4","#52F8C4","#52F8C4", "#00BFFF"

    ])