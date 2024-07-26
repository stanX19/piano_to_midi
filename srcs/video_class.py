import cv2
import time
import numpy as np
import pathlib
import utils

class VideoClass:
    def __init__(self, video_path: str):
        self.name = pathlib.Path(video_path).stem
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame_count = 0
        self._current_frame = None
        self._start_time = time.time()

    def read_next(self):
        """Read the next frame from the video."""
        ret, frame = self.cap.read()
        if ret:
            self.current_frame_count += 1
            self._current_frame = frame
            return True
        return False

    @property
    def current_frame(self):
        return self._current_frame

    @current_frame.setter
    def current_frame(self, img: np.ndarray):
        if not isinstance(img, np.ndarray):
            raise ValueError("current frame must be image")
        self._current_frame = img

    def skip_to_frame(self, frame_number: int):
        """Skip to a specific frame in the video."""
        if not (0 <= frame_number < self.total_frames):
            raise ValueError("Frame number out of range")
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.current_frame_count = frame_number
        ret, frame = self.cap.read()
        if ret:
            self._current_frame = frame

    def get_time_remaining_str(self):
        estimated_time_remaining = self.get_estimated_time_remaining()
        if estimated_time_remaining >= 60:
            minutes_remaining = int(estimated_time_remaining // 60)
            seconds_remaining = int(estimated_time_remaining % 60)
            return "{:02d}:{:02d}".format(minutes_remaining, seconds_remaining)
        else:
            return "{:.2f}s".format(estimated_time_remaining)

    def display_current_frame(self, show_info=True):
        """Display the current frame using OpenCV."""
        if self._current_frame is None:
            raise ValueError("No frame data available to display")

        frame = self._current_frame.copy()
        frame = utils.cv2_resize_to_fit(frame)
        if show_info:
            message = "Frame:{:>7}/{}\nProgress:{:>7.2f}%\nEstimated Time Remaining: {}".format(
                self.current_frame_count, self.total_frames,
                round(self.current_frame_count / self.total_frames * 100, 2),
                self.get_time_remaining_str()
            )
            utils.cv2_print_texts(frame, message, (200, 200),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), (200, 200, 200), 1)

        cv2.imshow('Current Frame', frame)
        cv2.waitKey(1)  # Display the frame for 1 millisecond

    def set_start_time(self):
        """Set the start time for processing."""
        self._start_time = time.time()

    def get_estimated_time_remaining(self):
        """Get the estimated time remaining for the video processing."""
        if self._start_time is None:
            raise ValueError("Start time not set. Use set_start_time() to set the start time.")

        elapsed_time = time.time() - self._start_time
        processed_frames = self.current_frame_count
        remaining_frames = self.total_frames - processed_frames

        if processed_frames == 0:
            return float('inf')  # Avoid division by zero

        estimated_remaining_time = (elapsed_time / processed_frames) * remaining_frames
        return estimated_remaining_time

    def release(self):
        """Release the video capture object."""
        self.cap.release()
        cv2.destroyAllWindows()

# Example usage:
# video = VideoClass("path_to_video.mp4")
# video.set_start_time()
# while video.read_next():
#     # Process the frame
#     print(video.current_frame)
#     video.display_current_frame()
#     print(f"Estimated time remaining: {video.get_estimated_time_remaining()} seconds")
# video.release()
