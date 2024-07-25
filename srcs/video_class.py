import cv2
import time


class VideoClass:
    def __init__(self, video_path: str):
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame_count = 0
        self._current_frame = None
        self._start_time = None

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

    def skip_to_frame(self, frame_number: int):
        """Skip to a specific frame in the video."""
        if not (0 <= frame_number < self.total_frames):
            raise ValueError("Frame number out of range")
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.current_frame_count = frame_number
        ret, frame = self.cap.read()
        if ret:
            self._current_frame = frame

    def display_current_frame(self):
        """Display the current frame using OpenCV."""
        if self._current_frame is not None:
            cv2.imshow('Current Frame', self._current_frame)
            cv2.waitKey(1)  # Display the frame for 1 millisecond
        else:
            raise ValueError("No frame data available to display")

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

        estimated_total_time = (elapsed_time / processed_frames) * remaining_frames
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
