import cv2
from p2m.p2m_types import *
from algo.video_class import VideoClass
from algo.locate_black_and_white import locate_white_and_black, preprocess_image, classify_keys, detect_rects


def wait_and_find_keys(video: VideoClass) -> KeysPairType:
    while video.read_next():
        ret = locate_white_and_black(video.current_frame)
        if ret is not None:
            return ret
        video.display_current_frame()

    raise RuntimeError("piano to midi: Failed to locate keys")


def draw_keys(img: ndarray, white_keys: list[RectType], black_keys: list[RectType], all_keys: list[RectType]):
    WIDTH = 2
    all_keys.sort(key=lambda k: k[0])
    for i, (x, y, w, h) in enumerate(all_keys):
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), WIDTH)
    # Draw white keys
    for i, (x, y, w, h) in enumerate(white_keys):
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), WIDTH)
    # Draw black keys
    for i, (x, y, w, h) in enumerate(black_keys):
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), WIDTH)

    return img


def test():
    video = VideoClass(r"D:\Downloads\Arcaea Testify _ void.mp4")
    # video = VideoClass(r"../assets/amygdala_piano.mp4")
    video.skip_to_frame(0)
    while video.read_next():
        print(f"\n==frame {video.current_frame_count}==")
        image = preprocess_image(video.current_frame)
        keys = detect_rects(image)
        keys = [k for k in keys if k[2] * 1.5 < k[3]]
        ret = classify_keys(keys)
        video.current_frame = cv2.cvtColor(preprocess_image(video.current_frame), cv2.COLOR_GRAY2BGR)
        if ret is not None:
            white, black = ret
        else:
            white, black = [], []
        draw_keys(video.current_frame, white, black, keys)
        video.display_current_frame(1)


if __name__ == '__main__':
    test()
