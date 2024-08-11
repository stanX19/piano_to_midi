import pathlib
from typing import Callable, Any, Union
import customtkinter as ctk


class QueueData:
    WAITING = "Waiting"
    PROCESSING = "Processing"
    COMPLETE = "Complete"

    def __init__(self, _str: str):
        _str = str(_str)
        self.src_path: str = _str
        self.src_path_var = ctk.StringVar(value=self.src_path)
        self.is_selected_var: ctk.BooleanVar = ctk.BooleanVar(value=True)
        self.title_var: ctk.StringVar = ctk.StringVar(value=self.get_default_title())
        self.src_filename_var: ctk.StringVar = ctk.StringVar(value=pathlib.Path(self.src_path).name)
        self.status = QueueData.WAITING

    def __str__(self):
        return f"QueueData: [title='{self.title_var.get()}', selected={self.is_selected_var.get()}, status={self.status}]"

    def __repr__(self):
        return self.__str__()

    def reset_title(self):
        self.title_var.set(self.get_default_title())

    def is_selected(self):
        return self.is_selected_var.get()

    def get_default_title(self):
        return pathlib.Path(self.src_path).stem


class QueueManager:
    def __init__(self):
        self._queue_list: list[QueueData] = []

    def __repr__(self) -> str:
        return f"{{QueueManager: {len(self._queue_list)}}}: {self._queue_list}"

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def queue_list(self) -> list[QueueData]:
        return self._queue_list[:]

    @property
    def path_list(self) -> list[str]:
        return[q.src_path for q in self._queue_list]

    @property
    def selected_list(self) -> list[QueueData]:
        return[q for q in self._queue_list if q.is_selected()]

    def add_path(self, path: str) -> None:
        if path in self.path_list:
            return
        data = QueueData(path)
        self._queue_list.append(data)

    def __len__(self):
        return self._queue_list.__len__()
