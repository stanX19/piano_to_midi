from typing import Callable, Any, Union
import customtkinter as ctk
from threading import Thread
from .queue_manager import QueueData, QueueManager
from .templates import *
from .queue_item_frame import QueueItemBaseFrame
from .queue_item_frame import QueueItemFrame
from .queue_item_frame import QueueItemEditFrame
from .queue_item_frame import QueueItemProcessFrame
from .interval_caller import IntervalCaller


class QueueContainerFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, queue_manager: QueueManager, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # self._scrollbar.grid_forget()
        self.queue_manager: QueueManager = queue_manager
        self.queue_frame_list: list[QueueItemBaseFrame] = []

        default_font = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        default_colors1 = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        default_colors2 = ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"]
        text_color = default_colors1 if self.cget('fg_color') is not default_colors1 else default_colors2
        self.queue_is_empty_label: ctk.CTkLabel = ctk.CTkLabel(self, text="Queue is empty",
                                                               font=(default_font[0], 36, "bold"),
                                                               text_color=text_color)
        self.grid_columnconfigure(0, weight=1)
        self.refresh()

    def refresh(self) -> None:
        queue_list = self.get_queue_data()
        frame_dict: dict[QueueData, QueueItemBaseFrame] = {
            frame.data: frame for frame in self.queue_frame_list
        }
        self.queue_frame_list = []
        for idx, data in enumerate(queue_list, start=1):
            if data in frame_dict:
                frame = frame_dict[data]
            else:
                frame = self.get_new_item_frame(data)
            frame.set_idx(idx)
            self.queue_frame_list.append(frame)

        for idx, frame in enumerate(self.queue_frame_list):
            self.after(0, frame.show)

        for frame in frame_dict.values():
            if frame not in self.queue_frame_list:
                self.after(0, frame.destroy)

        # queue empty text
        if not self.queue_frame_list:
            self.queue_is_empty_label.grid(row=0, pady=0)
        else:
            self.queue_is_empty_label.grid_forget()

    def get_queue_data(self):
        return self.queue_manager.queue_list

    def get_new_item_frame(self, data) -> QueueItemBaseFrame:
        return QueueItemFrame(self, data, len(self.queue_frame_list) + 1)


class QueueEditContainerFrame(QueueContainerFrame):
    def __init__(self, master, queue_manager: QueueManager, *args, **kwargs):
        super().__init__(master, queue_manager, *args, **kwargs)

    def get_queue_data(self):
        return self.queue_manager.selected_list

    def get_new_item_frame(self, data):
        return QueueItemEditFrame(self, data, len(self.queue_frame_list) + 1,
                                  unselect_callback_func=self.refresh)


class QueueProcessContainerFrame(QueueContainerFrame):
    def __init__(self, master, queue_manager: QueueManager, *args, **kwargs):
        super().__init__(master, queue_manager, *args, **kwargs)

    def get_queue_data(self):
        return self.queue_manager.selected_list

    def get_new_item_frame(self, data):
        return QueueItemProcessFrame(self, data, len(self.queue_frame_list) + 1, self.refresh)

    def toggle_start_for_all(self):
        for f in self.queue_frame_list:
            if isinstance(f, QueueItemProcessFrame):
                f.on_start()

    def toggle_pause_for_all(self):
        self.queue_manager.terminate_all()
        for f in self.queue_frame_list:
            if isinstance(f, QueueItemProcessFrame):
                f.on_pause()
