import customtkinter as ctk
import cv2
from typing import Optional, Callable
from PIL import Image, ImageTk

from srcs.algo.processing_class import ProcessingClass
from srcs.algo.utils import cv2_resize_to_fit
from .interval_caller import IntervalCaller


class CtkProcessDisplayFrame(ctk.CTkFrame):
    def __init__(self, master, processor: ProcessingClass, interval_caller: IntervalCaller,
                 width: int = 1280, height: int = 720,
                 progress_bar: Optional[ctk.CTkProgressBar] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.processor: ProcessingClass = processor
        self.interval_caller: IntervalCaller = interval_caller
        self.progress_bar: Optional[ctk.CTkProgressBar] = progress_bar
        self.width: int = width
        self.height: int = height
        self.canvas: ctk.CTkCanvas = ctk.CTkCanvas(self, width=width, height=height)
        self.canvas.pack(fill=ctk.BOTH, expand=True)

        # Placeholder for the image on the canvas
        self._image_on_canvas = self.canvas.create_image(0, 0, anchor=ctk.NW)

        # Reference to the current image to prevent garbage collection
        self._current_image = None
        self._play_schedule = None

    def reinit_canvas(self):
        self.canvas.configure(width=self.width, height=self.height)

    def set_width(self, width):
        self.width = width
        self.reinit_canvas()

    def set_height(self, height):
        self.height = height
        self.reinit_canvas()

    def update_frame(self):
        """Update the canvas with the current frame from the video."""
        array_img = self.processor.get_displayed_frame()
        if array_img is None:
            return
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        # print(f"update_frame {self.processor.video_path}")
        try:
            frame = cv2_resize_to_fit(array_img, self.width, self.height)
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
        self.progress_bar.set(self.processor.get_progress())

    def play(self):
        """Start displaying the video frames."""
        self.update_frame()
        self.update_progress_bar()
        if not self.processor.is_idle():
            self._play_schedule = self.interval_caller.add_to_queue(self.play)
        else:
            self._play_schedule = None

    def stop(self):
        """Stop the video playback."""
        self.after_cancel(self._play_schedule)
        self._play_schedule = None


# def test():
#     video = VideoClass("../../../assets/amygdala_piano.mp4")
#     video.read_next()  # Load the first frame
#
#     def read_video():
#         while video.read_next():
#             ...
#
#     root = ctk.CTk()
#     root.geometry(f"{1000}x{300}")
#     video_frame = CtkVideoFrame(root, video)
#     video_frame.pack()
#     video_frame.play()  # Start playing the video
#     from threading import Thread
#     t = Thread(target=read_video)
#     t.start()
#     root.mainloop()
#     t.join()
#     video.release()
#
#
# if __name__ == '__main__':
#     test()
