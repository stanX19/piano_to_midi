from typing import Callable, Any, Union, Optional
import customtkinter as ctk
from threading import Thread
from .queue_manager import QueueData, QueueManager
from algo.process_class import ProcessingClass


class RunInThreadHandler(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, func: Callable, *args, **kwargs):
        super().__init__(master)
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._thread: Optional[Thread] = Thread(target=self._thread_func)
        self._thread.start()

    def _thread_func(self):
        self._func(*self._args, **self._kwargs)
        self.after(0, self._thread.join)



