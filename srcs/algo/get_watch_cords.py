from p2m.p2m_types import *


def rect_contains(rect: RectType, cord: CordType, x_margin=11, y_margin=11) -> bool:
    x, y, width, height = rect
    cord_x, cord_y = cord
    return x - x_margin <= cord_x <= x + width + x_margin and y - y_margin <= cord_y <= y + height + y_margin


# obejctive 1: no overlap
# objective 2: large area
def get_watch_cords_dict(white_keys: list[RectType], black_keys: list[RectType]) -> dict[RectType, list[CordType]]:
    all_keys = sorted(white_keys + black_keys, key=lambda k: k[0])
    ret = {}
    for key in all_keys:
        x, y, w, h = key
        points = [
            (x + 0.2 * w, y + 0.2 * h),
            (x + 0.2 * w, y + 0.5 * h),
            (x + 0.2 * w, y + 0.8 * h),
            (x + 0.5 * w, y + 0.2 * h),
            (x + 0.5 * w, y + 0.5 * h),
            (x + 0.5 * w, y + 0.8 * h),
            (x + 0.8 * w, y + 0.2 * h),
            (x + 0.8 * w, y + 0.5 * h),
            (x + 0.8 * w, y + 0.8 * h),
        ]
        points = [(int(p[0]), int(p[1])) for p in points]
        curr_points = []
        for point in points:
            if key in white_keys and any(rect_contains(rect, point) for rect in black_keys):
                continue
            curr_points.append(point)
        ret[key] = curr_points
    return ret
