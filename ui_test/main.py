import pathlib
import time
from typing import Callable, Any, Union
import customtkinter as ctk
import tkinter as tk
from ui_test.ui_classes import StepInterface, CANCEL_STR, QueueManager
from ui_test.main_frames import HomeFrame, ConfirmationFrame, ProcessingFrame


class ScalableApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._scaling_in_queue = False
        self._current_scaling = ctk.ScalingTracker.get_widget_scaling(self)
        self.bind("<Control-MouseWheel>", self.resize)
        self.apply_scaling()

    def resize(self, arg: tk.Event):
        FACTOR = 1.1
        if self._scaling_in_queue:
            return
        if arg.delta > 0:
            self._current_scaling *= FACTOR
        else:
            self._current_scaling /= FACTOR
        if self._scaling_in_queue:
            return
        self._scaling_in_queue = True
        self.after(400, self.apply_scaling)

    def apply_scaling(self):
        ctk.set_widget_scaling(self._current_scaling)
        self.update_idletasks()
        self._scaling_in_queue = False


class App(ScalableApp):
    def __init__(self, width=400, height=240):
        super().__init__()
        self.geometry(f"{width}x{height}")
        self.title('Piano to midi')
        self.width = width
        self.height = height
        self.queue_manager: QueueManager = QueueManager()
        self._current_frame: Union[None, StepInterface] = None
        self._frames: list[StepInterface] = [
            HomeFrame(self, self.choose_frame, self.queue_manager),
            ConfirmationFrame(self, self.choose_frame, self.queue_manager),
            ProcessingFrame(self, self.choose_frame, self.queue_manager),
        ]
        self._idx: int = 0
        self.current_frame = self._frames[0]

    def choose_frame(self, ret_val):
        if ret_val == CANCEL_STR:
            self._idx -= 1
        else:
            self._idx += 1
        if self._idx < 0 or self._idx >= len(self._frames):
            print(self.queue_manager)
            self.quit()
            return
        self.current_frame = self._frames[self._idx]

    @property
    def current_frame(self):
        return self._current_frame

    @current_frame.setter
    def current_frame(self, new_frame):
        if isinstance(self._current_frame, StepInterface):
            self._current_frame.hide()
        self._current_frame = new_frame
        if isinstance(new_frame, StepInterface):
            new_frame.show()


def main():
    app = App(width=1280, height=720)
    app.mainloop()


if __name__ == "__main__":
    # ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
    ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
    main()
