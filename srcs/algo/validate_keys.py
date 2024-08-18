import math
import statistics
import numpy as np
from p2m.p2m_types import RectType
from typing import Optional, Union
from algo import utils


def is_outlier(data: list[int]) -> list[bool]:
    if not data:
        return []
    iq_data = utils.get_iq_data(data)
    iq_mean: float = statistics.mean(iq_data)
    # stddev: float = statistics.stdev(widths)
    k1 = max(7.0, iq_mean * 0.1)
    k2 = 1.5 * (iq_data[-1] - iq_data[0])  # the smaller the number the less tolerance
    k = max(k1, k2)
    lower_bound = math.floor(iq_data[0] - k)
    upper_bound = math.ceil(iq_data[-1] + k)
    # # print(k1, k2)
    # # print(k)
    # # print(lower_bound)
    # # print(upper_bound)
    return [w < lower_bound or w > upper_bound for w in data]


def has_uneven_width(keys: list[RectType], bounds=(0, 1280)) -> bool:
    widths = [k[2] for k in keys if k[0] > bounds[0] + 3 and k[0] + k[2] < bounds[1] - 3]

    if any(is_outlier(widths)):
        return True
    return False


def keys_is_connected(keys: list[RectType]) -> bool:
    if len(keys) < 2:
        return False
    widths = [k[2] for k in keys]
    width_mean = int(statistics.mean(utils.get_iq_data(widths)))
    keys_xdis = [keys[i][0] - keys[i - 1][0] for i in range(1, len(keys))]
    keys_xdis_grouped = utils.group_data(keys_xdis, tolerance=min(keys_xdis) * 0.5)
    lowest_xdis = int(statistics.mean(keys_xdis_grouped[0]))

    # if keys gap is more than width * k, reject
    if lowest_xdis > max(width_mean * 1.5, width_mean + 10):
        # print(f"{lowest_xdis=} > {width_mean * 1.5=}")
        return False
    # if keys gap is less than width * k, reject
    if lowest_xdis < min(width_mean * 0.6, width_mean - 10):
        # print(f"{lowest_xdis=} < {width_mean * 0.6=}")
        return False
    # TODO:
    #    add expansion to left and right
    #    now will miss some keys
    idx = 0
    while idx < len(keys) - 1:
        if keys[idx + 1][0] - keys[idx][0] > lowest_xdis * 1.5:
            x = keys[idx][0] + max(lowest_xdis, keys[idx][2])
            y = keys[idx][1]
            w = min(width_mean, keys[idx + 1][0] - keys[idx][0] - keys[idx][2])
            h = keys[idx][3]
            keys.insert(idx + 1, (x, y, w, h))
        idx += 1

    # recalculate
    tolerance = max(keys_xdis_grouped[0]) - min(keys_xdis_grouped[0]) + 5
    keys_xdis = [keys[i][0] - keys[i - 1][0] for i in range(1, len(keys))]
    keys_xdis_grouped = utils.group_data(keys_xdis, tolerance=tolerance)
    # # print(f"{keys_xdis=}")
    # # print(f"{keys_xdis_grouped=}")

    if len(keys_xdis_grouped) > 1:  # if there's missing keys
        # print("still have missing keys")
        return False
    return True


def black_is_correct(white_keys: list[RectType], black_keys: list[RectType]) -> bool:
    # loop through white and black with index using while loop
    # record 2 3 2 3 2 in process, last_break = 3 means current break must be 2, vice versa, left right exclude
    # black x > white x means next
    if len(black_keys) < 5:
        # print("not enough black keys")
        return False
    black_idx = 0
    white_idx = 0
    group_record: list[int] = []
    consecutive_black = 0
    while white_idx < len(white_keys) and black_idx < len(black_keys):
        white_key = white_keys[white_idx]
        black_key = black_keys[black_idx]
        if black_key[0] < white_key[0]:
            black_idx += 1
            consecutive_black += 1
        else:
            group_record.append(consecutive_black)
            consecutive_black = 0
        white_idx += 1
    # only allow one extra black key at edge of screen
    if (len(black_keys) - 1) - black_idx > 1:
        return False
    # add remaining
    group_record.append(consecutive_black)
    if group_record[0] == 0:
        group_record.pop(0)
    if group_record[-1] == 0:
        group_record.pop(-1)

    # TODO:
    #   must add keys completion below, white keys now looks at undetected black keys
    if len(group_record) < 2:
        return False
    if group_record[0] + group_record[1] > 5:
        return False
    if group_record[-1] + group_record[-2] > 5:
        return False
    for idx, group in enumerate(group_record[1:-2], start=1):
        if group != 2 and group != 3:
            return False
        if group + group_record[idx + 1] != 5:
            return False
    max_height = max(k[3] for k in black_keys)
    for idx, (x, y, w, h) in enumerate(black_keys):
        black_keys[idx] = (x, y, w, max_height)
    # # print(f"{group_record=}")
    return True


def validate_keys(white_keys: list[RectType], black_keys: list[RectType])\
        -> Union[None, tuple[list[RectType], list[RectType]]]:
    if not white_keys or not black_keys:
        return None
    white_keys.sort(key=lambda k: k[0])
    black_keys.sort(key=lambda k: k[0])
    # step1: black AND white width check
    if has_uneven_width(white_keys) or has_uneven_width(black_keys):
        # print("uneven width")
        return None

    # step2: white check: all connected
    if not keys_is_connected(white_keys):
        # print("white key not connected")
        return None

    # step 3: black check: is between white keys, follows 2 3 2 3
    if not black_is_correct(white_keys, black_keys):
        # print("black is wrong")
        return None

    return white_keys, black_keys
