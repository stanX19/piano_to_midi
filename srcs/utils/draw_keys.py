import cv2


def draw_keys(img, white_keys, black_keys):
    WIDTH = 2
    # Draw white keys
    for x, y, w, h in white_keys:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), WIDTH)
    # Draw black keys
    for x, y, w, h in black_keys:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), WIDTH)

    return img
