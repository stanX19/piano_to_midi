import numpy as np
import cv2
from video_class import VideoClass
import utils
from my_types import *
import statistics


def get_average_color(image: ImageType, cords: list[CordType]) -> np.ndarray:
    # Extract pixel values using numpy array indexing
    pixel_values = np.array([image[y, x] for x, y in cords])
    # Calculate the average color by taking the mean of RGB values
    average_color = np.mean(pixel_values, axis=0)
    return average_color.astype(int)


def color_diff(color1: np.ndarray, color2: np.ndarray) -> int:
    return int(np.sum(np.abs(color1 - color2)))


def draw_keys(img: ImageType, difference: np.ndarray, keys: list[RectType]):
    WIDTH1 = 2
    WIDTH2 = 3
    COLOR1 = (0, 255, 0)  # Green
    COLOR2 = (0, 0, 255)  # Red
    THRESHOLD = 50  # Threshold for significant difference in brightness

    for idx, key in enumerate(keys):
        x, y, w, h = key
        diff_value = int(difference[idx])  # Convert difference to int
        color = COLOR2 if diff_value > THRESHOLD else COLOR1
        width = WIDTH2 if diff_value > THRESHOLD else WIDTH1
        cv2.rectangle(img, (x, y), (x + w, y + h), color, width)
        cv2.putText(img, str(diff_value), (x + w // 3, y - 1000 // h), cv2.FONT_HERSHEY_SIMPLEX, 0.3, color)

    return img


def interquartile_mean(values: np.ndarray) -> np.ndarray:
    q25, q75 = np.percentile(values, [25, 75], axis=0)
    # Filter values between the 25th and 75th percentiles and return the mean as integers
    iqm_values = values[(values >= q25) & (values <= q75)]
    return np.mean(iqm_values, axis=0).astype(int)


def get_dpf(video: VideoClass, watch_cords: dict[RectType, list[CordType]], keys: KeysPairType) -> list[list]:
    black_key_colors = np.array([get_average_color(video.current_frame, watch_cords[key]) for key in keys[1]])
    white_key_colors = np.array([get_average_color(video.current_frame, watch_cords[key]) for key in keys[0]])

    black_key_color = interquartile_mean(black_key_colors)
    white_key_color = interquartile_mean(white_key_colors)

    original_colors = np.array([
        white_key_color if key in keys[0] else black_key_color
        for key in watch_cords
    ])

    difference_per_frame = []
    while video.read_next():
        current_colors = np.array([get_average_color(video.current_frame, cords) for cords in watch_cords.values()])
        difference = np.array([color_diff(orig, curr) for orig, curr in zip(original_colors, current_colors)])
        difference_per_frame.append(difference.tolist())
        draw_keys(video.current_frame, difference, list(watch_cords))
        video.display_current_frame()

    # Convert to numpy array for further operations and ensure differences are integers
    dpf = np.diff(np.array(difference_per_frame), axis=0)
    dpf = dpf.tolist()
    return dpf
