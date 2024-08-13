import cv2


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


# Assuming 'frame' is your original frame
def cv2_imshow_resized(name, frame, screen_width=1280, screen_height=720):
    resized_frame = cv2_resize_to_fit(frame, screen_width, screen_height)

    # Display the resized frame
    cv2.imshow(name, resized_frame)
