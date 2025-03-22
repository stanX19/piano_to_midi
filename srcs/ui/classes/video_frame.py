import customtkinter as ctk
import cv2
from typing import Optional
from PIL import Image, ImageTk

from srcs.algo.video_class import VideoClass
from srcs.algo.utils import cv2_resize_to_fit


class CtkVideoFrame(ctk.CTkFrame):
    def __init__(self, master, video: VideoClass, width: int = 1280, height: int = 720,
                 progress_bar: Optional[ctk.CTkProgressBar] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.video: VideoClass = video
        self.progress_bar: Optional[ctk.CTkProgressBar] = progress_bar
        self.width: int = width
        self.height: int = height
        self.canvas: ctk.CTkCanvas = ctk.CTkCanvas(self, width=self.width, height=self.height)
        self.canvas.pack(fill=ctk.BOTH, expand=True)

        # Placeholder for the image on the canvas
        self._image_on_canvas = self.canvas.create_image(0, 0, anchor=ctk.NW)

        # Reference to the current image to prevent garbage collection
        self._current_image = None
        self._play_schedule = None

    def update_frame(self):
        """Update the canvas with the current frame from the video."""
        # self.video.read_next()
        if self.video.current_frame is None:
            return

        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        try:
            frame = cv2_resize_to_fit(self.video.current_frame, self.width, self.height)
        except cv2.error:
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        self._current_image = ImageTk.PhotoImage(image=img)

        # center image
        img_width, img_height = self._current_image.width(), self._current_image.height()
        x_offset = (self.width - img_width) // 2
        y_offset = (self.height - img_height) // 2

        self.canvas.coords(self._image_on_canvas, x_offset, y_offset)
        self.canvas.itemconfig(self._image_on_canvas, image=self._current_image)

    def update_progress_bar(self):
        if not isinstance(self.progress_bar, ctk.CTkProgressBar):
            return
        self.progress_bar.set(self.video.current_frame_count / self.video.total_frames)

    def play(self):
        """Start displaying the video frames."""
        self.update_frame()
        self.update_progress_bar()
        if not self.video.eof:
            self._play_schedule = self.after(30, self.play)
        else:
            self._play_schedule = None

    def stop(self):
        """Stop the video playback."""
        self.after_cancel(self._play_schedule)
        self._play_schedule = None

    def release(self):
        """Release resources."""
        self.video.release()


def test():
    video = VideoClass("../../../assets/amygdala_piano.mp4")
    video.read_next()  # Load the first frame

    def read_video():
        while video.read_next():
            ...

    root = ctk.CTk()
    root.geometry(f"{1000}x{300}")
    video_frame = CtkVideoFrame(root, video)
    video_frame.pack()
    video_frame.play()  # Start playing the video
    from threading import Thread
    t = Thread(target=read_video)
    t.start()
    root.mainloop()
    t.join()
    video.release()


if __name__ == '__main__':
    test()
