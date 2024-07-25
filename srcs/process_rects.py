from my_types import RectType


def remove_duplicate_rectangles(rectangles: list[RectType], tolerance: int = 20) -> list[RectType]:
    def is_duplicate(r1: RectType, r2: RectType) -> bool:
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return (abs(x1 - x2) < tolerance and
                abs(y1 - y2) < tolerance and
                abs(w1 - w2) < tolerance and
                abs(h1 - h2) < tolerance)

    unique_rectangles = []
    for rect in rectangles:
        if not any(is_duplicate(rect, unique_rect) for unique_rect in unique_rectangles):
            unique_rectangles.append(rect)

    return unique_rectangles


def remove_overlap_rectangles(rectangles: list[RectType]) -> list[RectType]:
    def is_overlap(r1: RectType, r2: RectType) -> bool:
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2

        # Calculate the edges of the rectangles
        right1 = x1 + w1
        bottom1 = y1 + h1
        right2 = x2 + w2
        bottom2 = y2 + h2

        if x1 >= right2 or x2 >= right1:
            return False
        if y1 >= bottom2 or y2 >= bottom1:
            return False
        return True

    unique_rectangles = []
    for rect in rectangles:
        if not any(is_overlap(rect, unique_rect) for unique_rect in unique_rectangles):
            unique_rectangles.append(rect)

    return unique_rectangles


def get_shape_similarity(rects: list[RectType]) -> float:
    if len(rects) < 2:
        return 1.0  # Similarity score for a single rectangle or empty list is 1.0

    # Extract widths and heights
    widths = [rect[2] for rect in rects]
    heights = [rect[3] for rect in rects]

    # Calculate standard deviations for widths and heights
    std_dev_width = statistics.stdev(widths) if len(widths) > 1 else 0
    std_dev_height = statistics.stdev(heights) if len(heights) > 1 else 0

    # Normalize by the range of widths and heights
    range_width = max(widths) - min(widths) if len(widths) > 1 else 1
    range_height = max(heights) - min(heights) if len(heights) > 1 else 1

    # Calculate normalized standard deviations
    normalized_std_dev_width = std_dev_width / range_width if range_width > 0 else 0
    normalized_std_dev_height = std_dev_height / range_height if range_height > 0 else 0

    # Combine the normalized standard deviations
    avg_normalized_std_dev = (normalized_std_dev_width + normalized_std_dev_height) / 2

    # Similarity score: Lower avg_normalized_std_dev means higher similarity
    similarity_score = 1 - avg_normalized_std_dev

    return similarity_score


def get_centre(rects: list[RectType]) -> list[tuple[int, int]]:
    ret = [
        (round(rect[0] + rect[2] / 2), round(rect[1] + rect[3] / 2)) for rect in rects
    ]
    return ret