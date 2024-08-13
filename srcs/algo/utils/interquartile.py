def get_iq_data(data: list) -> list:
    """
    Gets interquartile version of data
    """
    idx_q1 = int(len(data) * 0.25)
    idx_q3 = int(len(data) * 0.75)
    return sorted(data)[idx_q1:idx_q3 + 1]
