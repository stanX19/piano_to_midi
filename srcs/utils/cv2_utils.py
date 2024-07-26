import cv2
import numpy as np


def cv2_resize_to_fit(frame, max_width=1280, max_height=720):
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    if frame_width == max_width and frame_height == max_height:
        return frame

    # Calculate the scaling factors for width and height
    width_scale = max_width / frame_width
    height_scale = max_height / frame_height

    # Determine the scaling factor based on the maximum screen resolution
    scale_factor = min(width_scale, height_scale)

    # Calculate the scaled width and height
    scaled_width = int(frame_width * scale_factor)
    scaled_height = int(frame_height * scale_factor)

    # Resize the frame using the scaled width and height
    resized_frame = cv2.resize(frame, (scaled_width, scaled_height))

    return resized_frame


def cv2_print_texts(frame: np.ndarray, message: str, top_left: tuple, font_type, scale: float, font_color: tuple,
                    outlining_color: tuple, font_width: int) -> np.ndarray:
    lines = message.split('\n')

    x, y = top_left
    _, line_height = cv2.getTextSize("A", font_type, scale, font_width)[0]
    line_height += 10

    for line in lines:
        cv2.putText(frame, line, (x, y), font_type, scale, outlining_color, int(font_width + 5 * scale), cv2.LINE_AA)
        cv2.putText(frame, line, (x, y), font_type, scale, font_color, font_width, cv2.LINE_AA)
        y += int(line_height)

    return frame


