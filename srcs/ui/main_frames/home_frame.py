import pathlib
from typing import Callable, Any, Union

import customtkinter as ctk

from ui.classes import StepInterface
from ui.classes import QueueManager
from ui.classes import QueueContainerFrame, QueueProcessContainerFrame
from algo.download_videos import is_valid_url


class PathEntryFrame(ctk.CTkFrame):
    def __init__(self, master, add_to_queue_func: Callable):
        super().__init__(master)
        self._func_add_to_queue = add_to_queue_func

        self.grid_columnconfigure(0, weight=1)  # Configure column 0 to expand
        self.top_left_label = ctk.CTkLabel(self,
                                           text="Please enter a valid file path or YouTube video URL:")
        self.top_left_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(5, 0))
        self.entry = ctk.CTkEntry(self, corner_radius=100)
        self.entry.grid(row=1, column=0, ipadx=32, ipady=12, sticky="ew", padx=(15, 0), pady=5)
        self.entry.bind("<Return>", self.call_add_to_queue)

        # btn_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        # bg_color = self.cget('fg_color')
        # background_corner_colors=(bg_color, btn_color, btn_color, bg_color))
        self.convert_button = ctk.CTkButton(self, text="Add to queue", command=self.call_add_to_queue,
                                            corner_radius=1000, width=0)
        self.convert_button.grid(row=1, column=1, ipadx=12, ipady=12)

        self.select_file_button = ctk.CTkButton(self, text="Select file", command=self.select_file,
                                                corner_radius=1000, width=0)
        self.select_file_button.grid(row=1, column=2, ipadx=12, ipady=12, padx=(0, 15))
        self.mode_label = ctk.CTkLabel(self, text="", text_color=self.convert_button.cget("fg_color"),
                                       justify=ctk.RIGHT, font=ctk.CTkFont(weight="bold"))
        self.mode_label.bind("<Button-1>", lambda _: self.change_mode())
        self.mode_label.grid(row=2, column=0, columnspan=3, sticky="nse", padx=20, pady=(0, 5))
        self.change_mode()
        self._force_extension = "mp4"

    def change_mode(self):
        TO_MIDI = "MP4 to midi"
        DOWNLOAD = "URL to MP4"
        self.mode_label.focus()
        if self.mode_label.cget('text') != TO_MIDI:
            self.mode_label.configure(text=TO_MIDI)
            self.entry.configure(placeholder_text="C:/Downloads/piano_synthesia_video.mp4")
        else:
            self.mode_label.configure(text=DOWNLOAD)
            self.entry.configure(placeholder_text="youtube.com/watch?v=YoU-tuBe_24")

    def clear(self):
        self.entry.delete(0, ctk.END)

    def call_add_to_queue(self, *args, **kwargs):
        self._func_add_to_queue()

    def get_extension_pattern(self):
        return f"*.{self._force_extension}" if self._force_extension else '*.*'

    def select_file(self):
        if self._force_extension:
            filetypes = [(f"{self._force_extension.upper()} files", self.get_extension_pattern())]
        else:
            filetypes = [("All Files", "*.*")]
        filepaths = ctk.filedialog.askopenfilenames(title="Select file", filetypes=filetypes)
        if not filepaths:
            return
        # if len(filepaths) == 1:
        #     self.entry.delete(0, ctk.END)
        #     self.entry.insert(0, filepaths[0])
        #     return
        for filepath in filepaths:
            self.clear()
            self.entry.insert(0, filepath)
            self.call_add_to_queue()


class HomeFrame(StepInterface):
    def __init__(self, master: ctk.CTk, result_handler_func: Callable[[str], Any], queue_manager: QueueManager):
        super().__init__(master, "Home", result_handler_func, cancel_btn_text=None)
        self.queue_manager = queue_manager

        self.content_frame.grid_rowconfigure(0, weight=0)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.entry_frame = PathEntryFrame(self.content_frame, self.add_to_queue)
        self.entry_frame.grid(row=0, column=0, padx=5, pady=(5, 0), ipadx=0, ipady=0, sticky="nsew")

        self.queue_frame = QueueContainerFrame(self.content_frame, queue_manager)
        self.queue_frame.grid(row=1, column=0, padx=5, pady=(5, 5), ipadx=15, ipady=15, sticky="nsew")

    def check_valid_path(self, path: str):
        path = pathlib.Path(path)
        if not path.is_file():
            self.show_error("Invalid path or url")
            return False
        if not path.match(self.entry_frame.get_extension_pattern()):
            self.show_error("Is not MP4 file")
            return False
        return True

    def add_to_queue(self):
        raw = self.entry_frame.entry.get().strip(" \"'")
        if not raw:
            return
        if is_valid_url(raw):
            self.queue_manager.add_url(raw)
        elif self.check_valid_path(raw):
            self.queue_manager.add_path(raw)
        else:
            return
        self.queue_frame.refresh()
        self.entry_frame.clear()
        self.show_error("")

    def on_next(self):
        if not self.queue_manager.selected_list:
            self.add_to_queue()
        if self.queue_manager.selected_list:
            super().on_next()

    def refresh(self):
        self.queue_frame.refresh()

