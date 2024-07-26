import cv2
import numpy as np
from my_types import *
from video_class import VideoClass


def get_average_color(image: ImageType, cords: list[CordType]) -> np.ndarray:
    pixel_values = np.array([image[y, x] for x, y in cords])  # [[b, g, r], [b, g, r], ..., [b, g, r]]
    sum_color = np.sum(pixel_values, axis=0, dtype=np.int32)  # [b_sum, g_sum, r_sum]
    average_color = sum_color // len(pixel_values)            # [b, g, r]
    return average_color


# def color_diff(color1: np.ndarray, color2: np.ndarray) -> int:
#     return int(np.sum(np.abs(color1 - color2)))


def draw_keys(img: ImageType, difference: np.ndarray, keys: list[RectType]):
    WIDTH1 = 2
    WIDTH2 = 3
    COLOR1 = (0, 255, 0)  # Green
    COLOR2 = (0, 0, 255)  # Red
    THRESHOLD = 80  # Threshold for significant difference in brightness

    for idx, key in enumerate(keys):
        x, y, w, h = key
        diff_value = int(difference[idx])  # Convert difference to int
        color = COLOR2 if diff_value > THRESHOLD else COLOR1
        width = WIDTH2 if diff_value > THRESHOLD else WIDTH1
        cv2.rectangle(img, (x, y), (x + w, y + h), color, width)
        cv2.putText(img, str(diff_value), (x + w // 3, y - 1000 // h), cv2.FONT_HERSHEY_SIMPLEX, 0.3, color)

    return img


def interquartile_rgb_mean(values: np.ndarray) -> np.ndarray:
    # Calculate luminance for each RGB triplet
    # [[b, g, r], [b, g, r], ..., [b, g, r]] --> [brightness, brightness, ..., brightness]
    luminance = np.dot(values, [3, 6, 1])

    # Sort the values based on luminance
    sorted_indices = np.argsort(luminance)  # gives the index to sort values
    sorted_values = values[sorted_indices]  # when sorted_indices is int it acts as reordering index

    # Calculate the indices for the 25th and 75th percentiles
    n = len(sorted_values)
    q25_idx = n // 4
    q75_idx = 3 * n // 4

    # Filter the middle 50% of the sorted values
    interquartile_values = sorted_values[q25_idx:q75_idx + 1]  # [[b, g, r], [b, g, r], ..., [b, g, r]]

    # Compute the mean of the interquartile values
    iqm_values = np.mean(interquartile_values, axis=0)  # [b_mean, g_mean, r_mean]

    # Convert to integers
    return iqm_values.astype(int)


def get_dpf(video: VideoClass, watch_cords: dict[RectType, list[CordType]], keys: KeysPairType) -> list[list]:
    difference_per_frame = []
    watch_cords_list = list(watch_cords.values())
    cord_type = np.array([1 if cord in keys[1] else 0 for cord in watch_cords])
    original_colors = np.full((len(watch_cords), 3), 0)  # [[b, g, r], [b, g, r], ..., [b, g, r]]

    while video.read_next():
        current_colors = np.array([get_average_color(video.current_frame, cords) for cords in watch_cords_list],
                                  dtype=np.int32)  # [[b, g, r], [b, g, r], ..., [b, g, r]]

        # Separate black and white key colors
        black_key_colors = current_colors[cord_type == 1]  # [[b, g, r], [b, g, r], ..., [b, g, r]]
        white_key_colors = current_colors[cord_type == 0]  # [[b, g, r], [b, g, r], ..., [b, g, r]]

        # Calculate interquartile RGB mean for black and white keys
        black_key_color = interquartile_rgb_mean(black_key_colors)  # [b, g, r]
        white_key_color = interquartile_rgb_mean(white_key_colors)  # [b, g, r]

        # Determine the original colors for each key
        original_colors[cord_type == 1] = black_key_color
        original_colors[cord_type == 0] = white_key_color

        # [int, int, ..., int]
        difference = np.sum(np.abs(current_colors - original_colors), axis=1).astype(int)
        # print(difference)
        difference_per_frame.append(difference.tolist())

        # Draw keys and display current frame
        draw_keys(video.current_frame, difference, list(watch_cords))
        video.display_current_frame()

    # Convert to numpy array for further operations and ensure differences are integers
    dpf = np.diff(np.array(difference_per_frame), axis=0)
    dpf = dpf.tolist()  # convert to list
    return dpf
