from typing import Callable, Any, Optional

import customtkinter as ctk

CANCEL_STR = "cancel"


class StepInterface(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk,
                 title: str,
                 result_handler_func: Callable[[str], Any],
                 cancel_btn_text: Optional[str] = "Cancel",
                 next_btn_text: Optional[str] = "Next"):
        super(StepInterface, self).__init__(master)
        self.master: ctk.CTk = master
        self._result_handler_func = result_handler_func
        self._active = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title frame
        self.title_frame = ctk.CTkFrame(self)
        self.title_frame.grid(row=0, pady=(5, 0), padx=5, sticky="ew")

        # Content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, padx=5, pady=(5, 0), sticky='nsew')

        font_size = 32
        self.title_label = ctk.CTkLabel(self.title_frame, text=title, font=("Arial", font_size, "bold"))
        self.title_label.pack(pady=font_size // 2, padx=font_size // 2)

        # Button frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, pady=5, padx=5, sticky='ew')

        if cancel_btn_text:
            self.cancel_button = ctk.CTkButton(self.button_frame, text=cancel_btn_text,
                                               command=self._on_cancel_button_press, width=0)
            self.cancel_button.pack(side=ctk.LEFT, padx=5)

        if next_btn_text:
            self.next_button = ctk.CTkButton(self.button_frame, text=next_btn_text, command=self._on_next_button_press,
                                             width=0)
            self.next_button.pack(side=ctk.RIGHT, padx=5)

        self.error_label = ctk.CTkLabel(self.button_frame, text="", text_color="red")
        self.error_label.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    def _on_next_button_press(self):
        if not self._active:
            return
        self.next_button.configure(state=ctk.DISABLED)
        self.on_next()
        self.next_button.configure(state=ctk.NORMAL)

    def _on_cancel_button_press(self):
        if not self._active:
            return
        self.cancel_button.configure(state=ctk.DISABLED)
        self.on_cancel()
        self.cancel_button.configure(state=ctk.NORMAL)

    def on_next(self):
        if not self._active:
            return
        return self._result_handler_func("next")

    def on_cancel(self):
        self.reset()
        return self._result_handler_func(CANCEL_STR)

    def show_error(self, text: str, interval: int = 3000):
        self.error_label.configure(text=text)
        self.after(interval, lambda: self.error_label.configure(text=""))

    def reset(self):
        pass

    def show(self):
        self._active = True
        self.pack(expand=True, fill=ctk.BOTH, padx=5, pady=5)

    def hide(self):
        self._active = False
        self.pack_forget()


class OptionFrame(StepInterface):
    def __init__(self, master: ctk.CTk, title: str, options: list[str], result_handler_func: Callable[[str], Any],
                 default=None, cancel: str = "cancel"):
        if not options:
            raise ValueError("Options cannot be empty")

        super().__init__(master, title, result_handler_func)

        self.options = options
        self.default = default if isinstance(default, str) else options[0]
        self.cancel = cancel
        self.selected_idx = ctk.IntVar()
        self.radio_buttons = []
        self._init_radio_buttons()

    def _init_radio_buttons(self):
        for idx, key in enumerate(self.options):
            btn = ctk.CTkRadioButton(self.content_frame, text=key, variable=self.selected_idx, value=idx, height=0)
            btn.pack(pady=(15, 0))
            if key == self.default:
                btn.invoke()
            self.radio_buttons.append(btn)

    def on_next(self):
        self.error_label.configure(text="")
        self._result_handler_func(self.options[self.selected_idx.get()])


class InputFrame(StepInterface):
    def __init__(self, master: ctk.CTk, title: str, result_handler_func: Callable[[str], Any], description="Input:",
                 default=""):
        super().__init__(master, title, result_handler_func)
        self.description_label = ctk.CTkLabel(self.content_frame, text=description, justify=ctk.LEFT, height=32)
        self.description_label.pack(side=ctk.TOP, anchor=ctk.NW, pady=5, padx=5, fill=ctk.BOTH, expand=True)
        self.entry = ctk.CTkEntry(self.content_frame)
        self.entry.insert(0, default)
        self.entry.pack(side=ctk.TOP, fill=ctk.BOTH, pady=5, padx=5)

    def on_next(self):
        self.error_label.configure(text="")
        return self._result_handler_func(self.entry.get())


class MonitoredEntry(ctk.CTkEntry):
    def __init__(self, master, *args, **kwargs):
        super(MonitoredEntry, self).__init__(master, *args, **kwargs)
        self.string_var = ctk.StringVar()
        self._on_write = lambda s: s
        self.string_var.trace_add("write", lambda _a, _b, _c: self._on_write(self.get()))

    def hook_on_write(self, func: Callable[[str], Any]):
        self._on_write = func


class CtkEntryLabel(ctk.CTkEntry):
    def __init__(self, master, *args, text="", **kwargs):
        super().__init__(master, border_width=0, fg_color="transparent", *args, **kwargs)
        self.insert(0, text)
        self.configure(state="readonly")
