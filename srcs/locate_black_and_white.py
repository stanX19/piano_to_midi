import math
import statistics
import numpy as np
from p2m_types import *
from process_rects import remove_duplicate_rectangles
from typing import Optional, Union
import utils
import cv2
from validate_keys import validate_keys


def preprocess_image(img: ImageType) -> ImageType:
    # Use Canny edge detection
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.Canny(img, 150, 200)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    _, img = cv2.threshold(img, 0, 255, 0)
    return img


def detect_rects(edges: ImageType) -> list[RectType]:
    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    rects: list[RectType] = []
    for contour in contours:
        # Approximate the contour to a polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Filter for rectangles (keys)
        if len(approx) >= 4:
            x, y, w, h = cv2.boundingRect(approx)
            rects.append((x, y, w, h))

    return remove_duplicate_rectangles(rects)


def display(y_classified, yh_classified):
    result = []
    for i, row in enumerate(yh_classified):
        result.append((y_classified[i][0][1], len(row), len(y_classified[i]), len(row) / len(y_classified[i])))
    result.sort(key=lambda x: x[3])
    print("y-pos\t\tgroup_count\tbox_count\tpriority")
    for row in result:
        print(*row[:3], f"{1.0 - row[3]:.2f}", sep="\t\t\t")


def classify_keys(keys: list[RectType]) -> KeysPairType:
    keys = [k for k in keys if k[2] * 1.5 < k[3]]
    y_classified: list[list[RectType]] = utils.group_data(keys, key=lambda k: k[1])
    yh_classified: list[list[list[RectType]]] = [utils.group_data(row, key=lambda k: k[3]) for row in y_classified]
    # display(y_classified, yh_classified)
    ret = None
    entropy = 1.0  # from 0.0 to 1.0, lower the better
    for i, row in enumerate(yh_classified):
        if len(row) < 2:
            continue
        for j in range(len(row) - 1):
            black_keys = row[j]
            white_keys = row[j + 1]
            if validate_keys(white_keys, black_keys) is None:
                continue
            this_entropy = 1 / (len(white_keys) + len(black_keys))
            if this_entropy > entropy:
                continue
            ret = (white_keys, black_keys)
            entropy = this_entropy

    return ret


def locate_white_and_black(image: ImageType) -> KeysPairType:
    image = preprocess_image(image)
    keys = detect_rects(image)
    ret = classify_keys(keys)
    return ret
