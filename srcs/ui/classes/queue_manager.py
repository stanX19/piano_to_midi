import concurrent
import pathlib
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, Any

import customtkinter as ctk
from p2m import p2m_path
from algo.video_class import VideoClass
from algo.processing_class import ProcessingClass, ProcessStates
from algo.download_videos import get_playlist_urls, UrlData, get_video_title
from algo.utils import SettableCachedProperty
from .process_display_frame import CtkProcessDisplayFrame


class QueueData:
    def __init__(self, master, _str: str, submit_to_executor: Callable[[Callable], Any], title=None, is_url=False):
        _str = str(_str)
        self.master: ctk.CTk = master
        self.src_str: str = _str
        self._submit_to_executor: Callable[[Callable], Any] = submit_to_executor
        self._is_url: bool = is_url
        self._is_running: bool = False
        self._start_hooks: set[tuple[Callable, Any]] = set()
        self._end_hooks: set[tuple[Callable, Any]] = set()
        if title is not None:
            self.default_title = title
        self.processor: ProcessingClass = ProcessingClass(self.src_str)

        # vars
        # once set to true, queue manager will add it to processing queue
        self.src_str_var = ctk.StringVar(value=self.src_str)
        self.is_selected_var: ctk.BooleanVar = ctk.BooleanVar(value=True)
        self.title_var: ctk.StringVar = ctk.StringVar(value=self.default_title)             # name of save as
        self.save_path_var: ctk.StringVar = ctk.StringVar(value=self.default_title)         # save as
        self.displayed_src_var: ctk.StringVar = ctk.StringVar(value=self.displayed_source)  # displayed source
        self.status_var: ctk.StringVar = ctk.StringVar(value=self.processor.state)

        # hooks
        self.processor.state_hooks.hook(self.update_status_text)
        self.title_var.trace_add("write", self.update_save_path)
        self.update_save_path()

    def __str__(self):
        return f"QueueData: [title='{self.title_var.get()}',\
selected={self.is_selected_var.get()}, status={self.processor.state}]"

    def __repr__(self):
        return self.__str__()

    def update_save_path(self, *args):
        # TODO:
        #   use download path instead
        save_path = os.path.join(p2m_path.DATA_DIR, self.title_var.get()).rstrip(".") + ".mid"
        self.save_path_var.set(save_path)

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

    def update_status_text(self):
        self.status_var.set(self.processor.state)

    @property
    def is_running(self) -> bool:
        return self._is_running

    def hook_start_func(self, func: Callable, *args):
        self._start_hooks.add((func, args))

    def hook_end_func(self, func: Callable, *args):
        self._end_hooks.add((func, args))

    def save_at_save_path(self):
        self._is_running = True
        self.processor.state = ProcessStates.RUNNING
        print("started saving")
        for func, args in self._start_hooks:
            print(f"called {func.__name__}")
            self.master.after(100, func, *args)
        try:
            print("getting midi")
            print(self.processor.midi)
            self.processor.save_as(self.save_path_var.get())
        except BaseException as exc:
            print(exc)
            return
        finally:
            self._is_running = False
        for func, args in self._end_hooks:
            self.master.after(0, func, *args)

    def start_processing(self):
        self.processor.state = ProcessStates.QUEUED
        self._submit_to_executor(self.save_at_save_path)

    def cancel_processing(self):
        self.processor.kill()


class QueueManager:
    def __init__(self, master: ctk.CTk):
        self.master: ctk.CTk = master
        self._queue_list: list[QueueData] = []
        self._max_threads: int = 3
        self._executor = ThreadPoolExecutor(max_workers=self._max_threads)

    def __repr__(self) -> str:
        return f"{{QueueManager: {len(self._queue_list)}}}: {self._queue_list}"

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def queue_list(self) -> list[QueueData]:
        return self._queue_list[:]

    @property
    def srcs_list(self) -> list[str]:
        return [q.src_str for q in self._queue_list]

    @property
    def selected_list(self) -> list[QueueData]:
        return [q for q in self._queue_list if q.is_selected()]

    def _add_queue_data(self, data: QueueData):
        self._queue_list.append(data)

    def add_path(self, path: str) -> None:
        if path in self.srcs_list:
            return
        data = QueueData(self.master, path, self.submit_to_executor)
        self._add_queue_data(data)

    def add_url(self, url: str):
        if url in self.srcs_list:
            return
        datas = get_playlist_urls(url)
        for url_data in datas:
            data = QueueData(self.master, url_data.url, self.submit_to_executor, url_data.title, is_url=True)
            self._add_queue_data(data)

    def get_running_tasks(self) -> list[QueueData]:
        return [q for q in self._queue_list if not q.processor.is_idle()]

    def get_running_tasks_names(self) -> list[str]:
        return [q.title_var.get() for q in self.get_running_tasks()]

    def has_running_task(self) -> bool:
        return bool(self.get_running_tasks)

    def submit_to_executor(self, func: Callable):
        self._executor.submit(func)

    def terminate_all(self):
        self._executor.shutdown(wait=False, cancel_futures=True)
        for q in self.get_running_tasks():
            q.cancel_processing()
        for q in self._queue_list:
            if q.processor.state is ProcessStates.QUEUED:
                q.processor.state = ProcessStates.NOT_STARTED
        self._executor = ThreadPoolExecutor(max_workers=self._max_threads)

    def __len__(self):
        return self._queue_list.__len__()
