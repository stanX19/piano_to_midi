import pathlib
from typing import Callable, Any, Union

import customtkinter as ctk

from ui.classes import StepInterface
from ui.classes import QueueManager
from ui.classes import QueueEditContainerFrame


class ConfirmationFrame(StepInterface):
    def __init__(self, master: ctk.CTk, result_handler_func: Callable[[str], Any], queue_manager: QueueManager):
        super().__init__(master, "Preparation", result_handler_func)
        self.queue_manager = queue_manager

        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.queue_frame = QueueEditContainerFrame(self.content_frame, queue_manager)
        self.queue_frame.grid(row=0, column=0, padx=5, pady=(5, 5), ipadx=15, ipady=15, sticky="nsew")

    def show(self):
        self.queue_frame.refresh()
        super().show()
