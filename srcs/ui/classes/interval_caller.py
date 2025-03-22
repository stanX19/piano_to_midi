import queue
import customtkinter as ctk


class IntervalCaller(ctk.CTkFrame):
    def __init__(self, parent, interval=1000, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._queue = queue.Queue()
        self._call_interval = interval
        self._after_id = None

    def add_to_queue(self, func, *args, **kwargs):
        self._queue.put((func, args, kwargs))
        if not self._after_id:
            self._after_id = self.after(self._call_interval, self._process_queue)

    def set_call_interval(self, val):
        self._call_interval = val

    def _process_queue(self):
        if self._queue.empty():
            self._after_id = None
            return
        func, args, kwargs = self._queue.get()
        try:
            func(*args, **kwargs)
            # print(f"func called: {func}")
        finally:
            self._after_id = self.after(self._call_interval, self._process_queue)

    def stop(self):
        if self._after_id is not None:
            self.after_cancel(self._after_id)  # Cancel the ongoing after call
            self._after_id = None
