def group_data(data: list, key=lambda x: x, tolerance=5) -> list[list]:
    # First, sort keys primarily by y-coordinate, secondarily by width, and then by height
    sorted_datas = sorted(data, key=key)

    # Initialize the groups
    classified_groups = []
    current_group = []
    for data in sorted_datas:
        # If the current group is empty, add the first key
        if not current_group:
            current_group.append(data)
            continue
        # Check if the y-coordinate of the current key is within the tolerance of the current group
        if abs(key(current_group[0]) - key(data)) <= tolerance:
            current_group.append(data)
        else:
            # If the current key does not fit the current group, finalize the current group and start a new one
            classified_groups.append(current_group)
            current_group = [data]

    # add the last group
    if current_group:
        classified_groups.append(current_group)

    return classified_groups
