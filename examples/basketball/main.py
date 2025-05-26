import argparse
from enum import Enum
from typing import Iterator, List

import os
import cv2
import numpy as np
import supervision as sv
from tqdm import tqdm

from sports.annotators.basketball import draw_court, draw_points_on_pitch
#from sports.common.ball import BallTracker, BallAnnotator
from sports.common.team import TeamClassifier
from sports.common.view import ViewTransformer
from sports.configs.basketball import BasketballCourtConfiguration
from inference import get_model
PARENT_DIR = os.path.dirname(os.path.abspath(__file__))

from trackers import ByteTrackTracker
from trackers import ReIDModel
ROBOFLOW_API_KEY = "YOUR-API-KEY"
PLAYER_DETECTION_MODEL_ID = "basketball-player-detection-2/7"
COURT_DETECTION_MODEL_ID = "basketball-court-detection-2/8"
REID_MODEL_NAME = "mobilenetv4_conv_small.e1200_r224_in1k"
BALL_CLASS_ID = 0
NUMBER_CLASS_ID = 1
PLAYER_CLASS_ID = 2
REFEREE_CLASS_ID = 9
keypoint_confidence_threshold = 0.5

STRIDE = 60
CONFIG = BasketballCourtConfiguration()

COLORS = ['#FF1493', '#00BFFF', '#FF6347', '#FFD700']
VERTEX_LABEL_ANNOTATOR = sv.VertexLabelAnnotator(
    color=[sv.Color.from_hex(color) for color in CONFIG.colors],
    text_color=sv.Color.from_hex('#FFFFFF'),
    border_radius=5,
    text_thickness=1,
    text_scale=0.5,
    text_padding=5,
)
EDGE_ANNOTATOR = sv.EdgeAnnotator(
    color=sv.Color.from_hex('#FF1493'),
    thickness=2,
    edges=CONFIG.edges,
)
TRIANGLE_ANNOTATOR = sv.TriangleAnnotator(
    color=sv.Color.from_hex('#FF1493'),
    base=20,
    height=15,
)
BOX_ANNOTATOR = sv.BoxAnnotator(
    color=sv.ColorPalette.from_hex(COLORS),
    thickness=2
)
ELLIPSE_ANNOTATOR = sv.EllipseAnnotator(
    color=sv.ColorPalette.from_hex(COLORS),
    thickness=2
)
BOX_LABEL_ANNOTATOR = sv.LabelAnnotator(
    color=sv.ColorPalette.from_hex(COLORS),
    text_color=sv.Color.from_hex('#FFFFFF'),
    text_padding=5,
    text_thickness=1,
)
ELLIPSE_LABEL_ANNOTATOR = sv.LabelAnnotator(
    color=sv.ColorPalette.from_hex(COLORS),
    text_color=sv.Color.from_hex('#FFFFFF'),
    text_padding=5,
    text_thickness=1,
    text_position=sv.Position.BOTTOM_CENTER,
)


class Mode(Enum):
    """
    Enum class representing different modes of operation for Soccer AI video analysis.
    """
    PITCH_DETECTION = 'PITCH_DETECTION'
    PLAYER_DETECTION = 'PLAYER_DETECTION'
    BALL_DETECTION = 'BALL_DETECTION'
    PLAYER_TRACKING = 'PLAYER_TRACKING'
    TEAM_CLASSIFICATION = 'TEAM_CLASSIFICATION'
    RADAR = 'RADAR'


def get_crops(frame: np.ndarray, detections: sv.Detections) -> List[np.ndarray]:
    """
    Extract crops from the frame based on detected bounding boxes.

    Args:
        frame (np.ndarray): The frame from which to extract crops.
        detections (sv.Detections): Detected objects with bounding boxes.

    Returns:
        List[np.ndarray]: List of cropped images.
    """
    return [sv.crop_image(frame, xyxy) for xyxy in detections.xyxy]


def render_radar(
    detections: sv.Detections,
    keypoints: sv.KeyPoints,
    color_lookup: np.ndarray
) -> np.ndarray:
    mask = (keypoints.xy[0][:, 0] > 1) & (keypoints.xy[0][:, 1] > 1)
    transformer = ViewTransformer(
        source=keypoints.xy[0][mask].astype(np.float32),
        target=np.array(CONFIG.vertices)[mask].astype(np.float32)
    )
    xy = detections.get_anchors_coordinates(anchor=sv.Position.BOTTOM_CENTER)
    transformed_xy = transformer.transform_points(points=xy)
    scale = 0.2
    radar = draw_court(config=CONFIG, scale = scale)
    for i in range(2):
        radar = draw_points_on_pitch(
        config=CONFIG, xy=transformed_xy[color_lookup == i],
        face_color=sv.Color.from_hex(COLORS[i]), radius=4, pitch=radar, scale = scale)
    return radar

def run_pitch_detection(source_video_path: str, device: str) -> Iterator[np.ndarray]:
    """
    Run pitch detection on a video and yield annotated frames.

    Args:
        source_video_path (str): Path to the source video.
        device (str): Device to run the model on (e.g., 'cpu', 'cuda').

    Yields:
        Iterator[np.ndarray]: Iterator over annotated frames.
    """
    pitch_detection_model = get_model(model_id=COURT_DETECTION_MODEL_ID)
    frame_generator = sv.get_video_frames_generator(source_path=source_video_path)
    for frame in frame_generator:
        result = pitch_detection_model.infer(frame, verbose=False)[0]
        keypoints = sv.KeyPoints.from_inference(result)

        annotated_frame = frame.copy()
        annotated_frame = VERTEX_LABEL_ANNOTATOR.annotate(
            annotated_frame, keypoints, CONFIG.labels)
        yield annotated_frame

def run_radar(source_video_path: str, device: str) -> Iterator[np.ndarray]:
    player_detection_model = get_model(model_id=PLAYER_DETECTION_MODEL_ID, api_key = ROBOFLOW_API_KEY)

    pitch_detection_model = get_model(model_id=COURT_DETECTION_MODEL_ID, api_key = ROBOFLOW_API_KEY)
    frame_generator = sv.get_video_frames_generator(
        source_path=source_video_path, stride=STRIDE)
    
    crops = []
    for frame in tqdm(frame_generator, desc='collecting crops'):
        result = player_detection_model.infer(frame, verbose=False)[0]
        detections = sv.Detections.from_inference(result)
        crops += get_crops(frame, detections[detections.class_id == PLAYER_CLASS_ID])

    team_classifier = TeamClassifier(device=device)
    team_classifier.fit(crops)

    frame_generator = sv.get_video_frames_generator(source_path=source_video_path)

    feature_model = ReIDModel.from_timm(REID_MODEL_NAME)
    tracker = ByteTrackTracker(
        minimum_consecutive_frames=3,
        reid_model=feature_model,
        lost_track_buffer=100,
        )
    for frame in frame_generator:
        result = pitch_detection_model.infer(frame, verbose=False)[0]
        keypoints = sv.KeyPoints.from_inference(result)

        mask = keypoints.confidence[0]<keypoint_confidence_threshold
        keypoints.xy[0][mask] = keypoints.xy[0][mask] * 0

        if len(mask)-np.count_nonzero(mask)<4: # If there arent 4 points for find homography
            print("Frame skipped due to lack of keypoints")
            continue
        result_players = player_detection_model.infer(frame, verbose=False)[0]
        detections = sv.Detections.from_inference(result_players)
        players = detections[detections.class_id == PLAYER_CLASS_ID]

        detections = tracker.update(players, frame)

        crops = get_crops(frame, players)
        players_team_id = team_classifier.predict(crops)

        color_lookup = players_team_id
        labels = [str(tracker_id) for tracker_id in detections.tracker_id]
        detections.class_id = players_team_id # For assigning the correct color in annotators

        annotated_frame = frame.copy()
        annotated_frame = ELLIPSE_ANNOTATOR.annotate(
            annotated_frame, detections, custom_color_lookup=sv.ColorLookup.CLASS)
        annotated_frame = ELLIPSE_LABEL_ANNOTATOR.annotate(
            annotated_frame, detections, labels,
            custom_color_lookup=sv.ColorLookup.CLASS)

        h, w, _ = frame.shape
        radar = render_radar(detections, keypoints, color_lookup)
        radar = sv.resize_image(radar, (w // 2, h // 2))
        radar_h, radar_w, _ = radar.shape
        rect = sv.Rect(
            x=w // 2 - radar_w // 2,
            y=h - radar_h,
            width=radar_w,
            height=radar_h
        )
        annotated_frame = sv.draw_image(annotated_frame, radar, opacity=0.8, rect=rect)
        yield annotated_frame

def run_player_detection(source_video_path: str, device: str) -> Iterator[np.ndarray]:
    """
    Run player detection on a video and yield annotated frames.

    Args:
        source_video_path (str): Path to the source video.
        device (str): Device to run the model on (e.g., 'cpu', 'cuda').

    Yields:
        Iterator[np.ndarray]: Iterator over annotated frames.
    """
    player_detection_model = get_model(model_id=PLAYER_DETECTION_MODEL_ID)
    frame_generator = sv.get_video_frames_generator(source_path=source_video_path)
    for frame in frame_generator:
        result = player_detection_model.infer(frame, verbose=False)[0]
        detections = sv.Detections.from_inference(result)

        annotated_frame = frame.copy()
        annotated_frame = BOX_ANNOTATOR.annotate(annotated_frame, detections)
        annotated_frame = BOX_LABEL_ANNOTATOR.annotate(annotated_frame, detections)
        yield annotated_frame

def run_player_tracking(source_video_path: str, device: str) -> Iterator[np.ndarray]:
    """
    Run player tracking on a video and yield annotated frames with tracked players.

    Args:
        source_video_path (str): Path to the source video.
        device (str): Device to run the model on (e.g., 'cpu', 'cuda').

    Yields:
        Iterator[np.ndarray]: Iterator over annotated frames.
    """
    player_detection_model = get_model(model_id=PLAYER_DETECTION_MODEL_ID)
    frame_generator = sv.get_video_frames_generator(source_path=source_video_path)

    feature_model = ReIDModel.from_timm(REID_MODEL_NAME)
    tracker = ByteTrackTracker(
        minimum_consecutive_frames=3,
        reid_model=feature_model,
        lost_track_buffer=40,
        )    
    for frame in frame_generator:
        result = player_detection_model.infer(frame, verbose=False)[0]
        detections = sv.Detections.from_inference(result)
        detections = tracker.update(detections, frame)

        labels = [str(tracker_id) for tracker_id in detections.tracker_id]

        annotated_frame = frame.copy()
        annotated_frame = ELLIPSE_ANNOTATOR.annotate(annotated_frame, detections)
        annotated_frame = ELLIPSE_LABEL_ANNOTATOR.annotate(
            annotated_frame, detections, labels=labels)
        yield annotated_frame

def main(source_video_path: str, target_video_path: str, device: str, mode: Mode    ) -> None:
    if mode == Mode.PITCH_DETECTION:
        frame_generator = run_pitch_detection(
            source_video_path=source_video_path, device=device)
    elif mode == Mode.PLAYER_DETECTION:
        frame_generator = run_player_detection(
            source_video_path=source_video_path, device=device)
    elif mode == Mode.BALL_DETECTION:
        frame_generator = run_ball_detection(
            source_video_path=source_video_path, device=device)
    elif mode == Mode.PLAYER_TRACKING:
        frame_generator = run_player_tracking(
            source_video_path=source_video_path, device=device)
    elif mode == Mode.TEAM_CLASSIFICATION:
        frame_generator = run_team_classification(
            source_video_path=source_video_path, device=device)
    elif mode == Mode.RADAR:
        frame_generator = run_radar(
            source_video_path=source_video_path, device=device)
    else:
        raise NotImplementedError(f"Mode {mode} is not implemented.")
    i = 0
    video_info = sv.VideoInfo.from_video_path(source_video_path)
    with sv.VideoSink(target_video_path, video_info) as sink:
        for frame in frame_generator:
            sink.write_frame(frame)
            cv2.imwrite(f"out{i}.jpg", frame)
            i+=1
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--source_video_path', type=str, required=True)
    parser.add_argument('--target_video_path', type=str, required=True)
    parser.add_argument('--device', type=str, default='cpu')
    parser.add_argument('--mode', type=Mode, default=Mode.PLAYER_DETECTION)

    args = parser.parse_args()
    main(
        source_video_path=args.source_video_path,
        target_video_path=args.target_video_path,
        device=args.device,
        mode=args.mode,
    )