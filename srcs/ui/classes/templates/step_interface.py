from typing import Callable, Any, Optional

import customtkinter as ctk

BACK_STR = "BACK"


class StepInterface(ctk.CTkFrame):
    def __init__(self, master,
                 title: str,
                 result_handler_func: Callable[[str], Any],
                 back_btn_text: Optional[str] = "Back",
                 next_btn_text: Optional[str] = "Next"):
        super(StepInterface, self).__init__(master)
        self.master: ctk.CTk = master
        self._result_handler_func = result_handler_func
        self._active = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title frame
        self._title_frame = ctk.CTkFrame(self)
        self._title_frame.grid(row=0, pady=(5, 0), padx=5, sticky="ew")

        # Content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, padx=5, pady=(5, 0), sticky='nsew')

        font_size = 32
        self._title_label = ctk.CTkLabel(self._title_frame, text=title, font=("Arial", font_size, "bold"))
        self._title_label.pack(pady=font_size // 2, padx=font_size // 2)

        # Button frame
        self._button_frame = ctk.CTkFrame(self)
        self._button_frame.grid(row=2, column=0, pady=5, padx=5, sticky='ew')

        if back_btn_text:
            self._back_button = ctk.CTkButton(self._button_frame, text=back_btn_text,
                                              command=self._on_back_button_press, width=0)
            self._back_button.pack(side=ctk.LEFT, padx=5)

        if next_btn_text:
            self._next_button = ctk.CTkButton(self._button_frame, text=next_btn_text, command=self._on_next_button_press,
                                              width=0)
            self._next_button.pack(side=ctk.RIGHT, padx=5)

        self._error_label = ctk.CTkLabel(self._button_frame, text="", text_color="red")
        self._error_label.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    def _on_next_button_press(self):
        if not self._active:
            return
        self._next_button.configure(state=ctk.DISABLED)
        self.on_next()
        self._next_button.configure(state=ctk.NORMAL)

    def _on_back_button_press(self):
        if not self._active:
            return
        self._back_button.configure(state=ctk.DISABLED)
        self.on_cancel()
        self._back_button.configure(state=ctk.NORMAL)

    def on_next(self):
        return self._result_handler_func("next")

    def on_cancel(self):
        return self._result_handler_func(BACK_STR)

    def show_error(self, text: str, interval: int = 3000):
        self._error_label.configure(text=text)
        self.after(interval, lambda: self._error_label.configure(text=""))

    def refresh(self):
        pass

    def show(self):
        self._active = True
        self.refresh()
        self.pack(expand=True, fill=ctk.BOTH, padx=5, pady=5)

    def hide(self):
        self._active = False
        self.pack_forget()