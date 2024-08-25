import pathlib
from typing import Callable, Any, Union

import customtkinter as ctk

from ui.classes import StepInterface
from ui.classes import QueueManager
from ui.classes import QueueProcessContainerFrame


class HelperButtonsFrame(ctk.CTkFrame):
    def __init__(self, master, func_dict: dict[str, Callable]):
        super().__init__(master)
        self._func_dict: dict[str, Callable] = {}
        self.buttons_dict: dict[str, ctk.CTkButton] = {}
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        for index, (name, func) in enumerate(func_dict.items()):
            btn = ctk.CTkButton(self, text=name, command=func)
            btn.grid(row=0, column=index, padx=5, pady=5, sticky="nse")  # Align buttons to the right
            self.buttons_dict[name] = btn


class ProcessingFrame(StepInterface):
    def __init__(self, master, result_handler_func: Callable[[str], Any], queue_manager: QueueManager):
        super().__init__(master, "Processing", result_handler_func, next_btn_text="")
        self.queue_manager = queue_manager

        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.queue_frame = QueueProcessContainerFrame(self.content_frame, queue_manager)
        self.queue_frame.grid(row=0, column=0, padx=5, pady=(5, 0), sticky="nsew")
        self.helper_button_frame = HelperButtonsFrame(self.content_frame, {
            "Start all": self.queue_frame.toggle_start_for_all,
            "Terminate all": self.queue_frame.toggle_pause_for_all
        })
        self.helper_button_frame.grid(row=1, column=0, padx=5, pady=(5, 5), sticky="nsew")

    def refresh(self):
        self.queue_frame.refresh()
