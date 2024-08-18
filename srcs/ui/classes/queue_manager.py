import pathlib
import os

import customtkinter as ctk
from p2m import p2m_path
from algo.video_class import VideoClass
from algo.processing_class import ProcessingClass
from algo.download_videos import get_playlist_urls, UrlData, get_video_title
from algo.utils import SettableCachedProperty


class QueueData:
    def __init__(self, _str: str, title=None, is_url=False):
        _str = str(_str)
        self.src_str: str = _str
        self._is_url = is_url
        if title is not None:
            self.default_title = title
        self.processor: ProcessingClass = ProcessingClass(self.src_str)
        self.src_path_var = ctk.StringVar(value=self.src_str)
        self.is_selected_var: ctk.BooleanVar = ctk.BooleanVar(value=True)
        self.title_var: ctk.StringVar = ctk.StringVar(value=self.default_title)                     # save as
        self.displayed_src_var: ctk.StringVar = ctk.StringVar(value=self.displayed_source)  # displayed source

    def __str__(self):
        return f"QueueData: [title='{self.title_var.get()}',\
selected={self.is_selected_var.get()}, status={self.processor.state}]"

    def __repr__(self):
        return self.__str__()

    def get_save_path(self):
        return os.path.join(p2m_path.DATA_DIR, self.title_var.get()).rstrip(".") + ".mid"

    def reset_title(self):
        self.title_var.set(self.default_title)

    def is_selected(self):
        return self.is_selected_var.get()

    @SettableCachedProperty
    def default_title(self):
        if self._is_url:
            return get_video_title(self.src_str)
        return pathlib.Path(self.src_str).stem

    @SettableCachedProperty
    def displayed_source(self):
        if self._is_url:
            return self.default_title
        return pathlib.Path(self.src_str).name


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
        return [q.src_str for q in self._queue_list]

    @property
    def selected_list(self) -> list[QueueData]:
        return [q for q in self._queue_list if q.is_selected()]

    def add_path(self, path: str) -> None:
        if path in self.path_list:
            return
        data = QueueData(path)
        self._queue_list.append(data)

    def add_url(self, url: str):
        print("add url called")
        datas = get_playlist_urls(url)
        for url_data in datas:
            data = QueueData(url_data.url, url_data.title, is_url=True)
            self._queue_list.append(data)

    def get_running_tasks(self) -> list[str]:
        running_tasks: list[str] = []
        for q in self._queue_list:
            if not q.processor.is_idle():
                running_tasks.append(q.title_var.get())
        return running_tasks

    def has_running_task(self) -> bool:
        return bool(self.get_running_tasks())

    def __len__(self):
        return self._queue_list.__len__()
