import cv2
from my_types import *
from video_class import VideoClass
from locate_black_and_white import locate_white_and_black


def draw_keys(img, white_keys, black_keys):
    WIDTH = 2
    # Draw white keys
    for x, y, w, h in white_keys:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), WIDTH)
    # Draw black keys
    for x, y, w, h in black_keys:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), WIDTH)

    return img


def wait_and_find_keys(video: VideoClass) -> KeysPairType:
    while video.read_next():
        ret = locate_white_and_black(video.current_frame)
        if ret is not None:
            return ret
        video.display_current_frame()

    raise RuntimeError("piano to midi: Failed to locate keys")
