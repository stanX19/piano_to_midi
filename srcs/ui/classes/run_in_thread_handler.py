from typing import Callable, Any, Union, Optional
import customtkinter as ctk
from threading import Thread
from .queue_manager import QueueData, QueueManager
from algo.process_class import ProcessingClass


class RunInThreadHandler(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass,
                 target: Callable,
                 args: tuple = (),
                 func_end_callback: Optional[Callable] = None,
                 kwargs: Optional[dict[str, Any]] = None):
        super().__init__(master)
        self._func: Callable = target
        self._args: tuple = args
        self._kwargs: dict[str, Any] = kwargs if kwargs is not None else {}
        self._func_end_callback: Optional[Callable] = func_end_callback
        self._thread: Optional[Thread] = Thread(target=self._thread_func)
        self._thread.start()

    def _thread_func(self):
        try:
            self._func(*self._args, **self._kwargs)
        except BaseException as exc:
            print(exc)
        self.after(1000, self._thread.join)
        if self._func_end_callback is not None:
            self.after(1000, self._func_end_callback)



