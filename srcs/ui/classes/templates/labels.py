from typing import Callable, Any, Optional

import customtkinter as ctk


class CtkEntryLabel(ctk.CTkEntry):
    def __init__(self, master, *args, text="", **kwargs):
        super().__init__(master, border_width=0, fg_color="transparent", *args, **kwargs)
        self.insert(0, text)
        self.configure(state="readonly")


class CtkTextBoxLabel(ctk.CTkTextbox):
    def __init__(self, master: ctk.CTkBaseClass, text: str = "", wrap=ctk.CHAR):
        super().__init__(master, border_width=0, border_spacing=0, width=0, height=0, wrap=wrap,
                         fg_color="transparent", activate_scrollbars=False)
        self.insert(ctk.END, text)
        self.configure(state=ctk.DISABLED)


class CtkGridWrappingLabel(ctk.CTkLabel):
    def __init__(self, master=None, height=0, width=0, justify=ctk.LEFT, **kwargs):
        super().__init__(master, height=height, width=width, justify=justify, **kwargs)
        self._last_wrap_length: int = 0
        self._resize_after_id = None
        self.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        new_wrap_length = int(self.winfo_width() / ctk.ScalingTracker.get_widget_scaling(self))
        if new_wrap_length == self._last_wrap_length:
            return
        self._last_wrap_length = new_wrap_length

        # Cancel previous
        if self._resize_after_id is not None:
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(1, self._update_wrap_length)

    def _update_wrap_length(self):
        self.configure(wraplength=self._last_wrap_length)
        self._resize_after_id = None
