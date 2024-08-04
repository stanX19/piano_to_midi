import pathlib
from typing import Callable, Any, Union

import customtkinter as ctk

# Set appearance and theme

CANCEL_STR = "cancel"


class StepInterface(ctk.CTkFrame):
    def __init__(self, root: ctk.CTk, title: str, result_handler_func: Callable[[str], Any]):
        super(StepInterface, self).__init__(root)
        self.root: ctk.CTk = root
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

        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.grid(row=2, column=0, sticky="ew")

        font_size = 32
        self.title_label = ctk.CTkLabel(self.title_frame, text=title, font=("Arial", font_size, "bold"))
        self.title_label.pack(pady=font_size // 2, padx=font_size // 2)

        # Button frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=3, column=0, pady=5, padx=5, sticky='ew')

        self.next_button = ctk.CTkButton(self.button_frame, text="Next", command=self._on_next, width=0)
        self.next_button.pack(side=ctk.RIGHT, padx=5)

        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel", command=self._on_cancel, width=0)
        self.cancel_button.pack(side=ctk.LEFT, padx=5)

    def _on_next(self):
        if not self._active:
            return
        self.on_next()

    def _on_cancel(self):
        if not self._active:
            return
        self.on_cancel()

    def on_next(self):
        if not self._active:
            return
        return self._result_handler_func("next")

    def on_cancel(self):
        self.reset()
        return self._result_handler_func(CANCEL_STR)

    def reset(self):
        pass

    def show(self):
        self._active = True
        self.pack(expand=True, fill=ctk.BOTH, padx=5, pady=5)

    def hide(self):
        self._active = False
        self.pack_forget()


#
# class InterfaceManager:
#     def __init__(self, root: ctk.CTk, steps: list[StepInterface]):
#         self.root: ctk.CTk = root
#         self.steps: list[StepInterface] = steps
#         self.current_index: int = 0
#
#         for step in self.steps:
#             step.manager = self
#
#     def start(self):
#         if self.steps:
#             self.steps[0].show()
#
#     def next_step(self):
#         if self.current_index < len(self.steps) - 1:
#             self.steps[self.current_index].hide()
#             self.current_index += 1
#             self.steps[self.current_index].show()
#         else:
#             self.steps[self.current_index].hide()
#             for step in self.steps:
#                 print(step.content_widgets)
#
#
#     def previous_step(self):
#         if self.current_index > 0:
#             self.steps[self.current_index].hide()
#             self.current_index -= 1
#             self.steps[self.current_index].show()
#
#
# class FirstStep(StepInterface):
#     def create_content(self):
#         label = ctk.CTkLabel(self.content_frame, text="Content for the first step.")
#         label.pack(pady=10)
#         self.content_widgets['entry'] = ctk.CTkEntry(self.content_frame)
#         self.content_widgets['entry'].pack(pady=10)
#
#     def check_function(self):
#         return bool(self.content_widgets['entry'].get())  # Example check: Entry should not be empty
#
#
# class SecondStep(StepInterface):
#     def create_content(self):
#         label = ctk.CTkLabel(self.content_frame, text="Content for the second step.")
#         label.pack(pady=10)
#         self.content_widgets['checkbox'] = ctk.CTkCheckBox(self.content_frame, text="Check me")
#         self.content_widgets['checkbox'].pack(pady=10)
#
#     def check_function(self):
#         return self.content_widgets['checkbox'].get()  # Example check: Checkbox should be checked
#
#
# class ThirdStep(StepInterface):
#     def create_content(self):
#         label = ctk.CTkLabel(self.content_frame, text="Content for the third step.")
#         label.pack(pady=10)
#         self.content_widgets['radio_var'] = ctk.IntVar()
#         radiobutton1 = ctk.CTkRadioButton(self.content_frame, text="Option 1",
#                                           variable=self.content_widgets['radio_var'], value=1)
#         radiobutton2 = ctk.CTkRadioButton(self.content_frame, text="Option 2",
#                                           variable=self.content_widgets['radio_var'], value=2)
#         radiobutton1.pack(pady=5)
#         radiobutton2.pack(pady=5)
#
#     def check_function(self):
#         return self.content_widgets['radio_var'].get() in {1, 2}
#
#
# class FourthStep(StepInterface):
#     def create_content(self):
#         label = ctk.CTkLabel(self.content_frame, text="Content for the fourth step.")
#         label.pack(pady=10)
#         self.content_widgets['slider'] = ctk.CTkSlider(self.content_frame, from_=0, to=100)
#         self.content_widgets['slider'].pack(pady=10)
#
#     def check_function(self):
#         return self.content_widgets['slider'].get() > 50  # Example check: Slider value should be greater than 50
#
#
# class TextEntryStep(StepInterface):
#     def create_content(self):
#         label = ctk.CTkLabel(self.content_frame, text="Enter text and press Enter to proceed:")
#         label.pack(pady=10)
#         self.content_widgets['entry'] = ctk.CTkEntry(self.content_frame)
#         self.content_widgets['entry'].pack(pady=10)
#         self.content_widgets['entry'].bind("<Return>", lambda event: self.on_next())
#
#     def check_function(self):
#         return bool(self.content_widgets['entry'].get())  # Example check: Entry should not be empty


class OptionFrame(StepInterface):
    def __init__(self, root: ctk.CTk, title: str, options: list[str], result_handler_func: Callable[[str], Any],
                 default=None, cancel: str = "cancel"):
        if not options:
            raise ValueError("Options cannot be empty")

        super().__init__(root, title, result_handler_func)

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
    def __init__(self, root: ctk.CTk, title: str, result_handler_func: Callable[[str], Any],
                 description="Input:", default=""):
        super().__init__(root, title, result_handler_func)
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
        self.string_var = ctk.StringVar()
        self._on_write = lambda s: s
        self.string_var.trace_add("write", lambda _: self._on_write(self.get()))
        super(MonitoredEntry, self).__init__(master, *args, **kwargs)

    def hook_on_write(self, func: Callable[[str], Any]):
        self._on_write = func


class HomeFrame(StepInterface):
    """
    Behaviour1:
    - one local video file, no pop up

    Behaviour2:
    - multiple local videos, pop up below

    Behaviour3:
    - Youtube video url, pop up below
    """

    def __init__(self, root: ctk.CTk, result_handler_func: Callable[[str], Any]):
        super().__init__(root, "Home", result_handler_func)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.entry_frame = ctk.CTkFrame(self.content_frame)
        self.entry_frame.grid(row=0, column=0, padx=5, pady=(5, 0), ipadx=15, ipady=15, sticky="new")

        self.entry_frame.grid_columnconfigure(0, weight=1)  # Configure column 0 to expand
        self.top_left_label = ctk.CTkLabel(self.entry_frame,
                                           text="Please enter a valid file path or YouTube video URL:")
        self.top_left_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=(5, 0))
        self.entry = ctk.CTkEntry(self.entry_frame, corner_radius=100,
                                  placeholder_text="C:/Downloads/piano_synthesia_video.mp4")
        self.entry.grid(row=1, column=0, ipadx=32, ipady=12, sticky="ew", padx=(5, 0), pady=5)
        self.entry.bind("<Return>", lambda event: self.add_to_queue())

        self.convert_button = ctk.CTkButton(self.entry_frame, text="Add to queue", command=self.add_to_queue, width=0,
                                            corner_radius=10000)
        self.convert_button.grid(row=1, column=1, ipadx=32, ipady=12)

        self.select_file_button = ctk.CTkButton(self.entry_frame, text="Select file", command=self.select_file, width=0,
                                                corner_radius=10000)
        self.select_file_button.grid(row=1, column=2, ipadx=32, ipady=12, padx=(0, 5))

        self.queue_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.queue_frame.grid(row=1, column=0, padx=5, pady=(5, 5), ipadx=15, ipady=15, sticky="ew")

        self.queue = []

        self._force_extension = "mp4"

    def get_extension_pattern(self):
        return f"*.{self._force_extension}" if self._force_extension else '*.*'

    def select_file(self):
        if self._force_extension:
            filetypes = [(f"{self._force_extension.upper()} files", self.get_extension_pattern())]
        else:
            filetypes = [("All Files", "*.*")]
        filepath = ctk.filedialog.askopenfilename(title="Select file", filetypes=filetypes)
        if filepath == "":
            return
        self.entry.delete(0, ctk.END)
        self.entry.insert(0, filepath)

    def add_to_queue(self):
        path = pathlib.Path(self.entry.get())
        if path.is_file() and path.match(self.get_extension_pattern()):
            self.queue.append(str(path))
            self.entry.delete(0, ctk.END)
        else:
            self.error_label.configure(text="Invalid path or url")

    def on_next(self):
        if not self.queue:
            self.add_to_queue()
        if self.queue:
            super().on_next()


class App(ctk.CTk):
    def __init__(self, width=400, height=240):
        super(App, self).__init__()
        self.geometry(f"{width}x{height}")
        self.title('Piano to midi')
        self.width = width
        self.height = height
        self.queue = []
        self._current_frame: Union[None, StepInterface] = None
        self._frames: list[StepInterface] = [
            HomeFrame(self, self.choose_frame),
            InputFrame(self, "Save as", self.choose_frame, f"Name: ", default="Unnamed"),
            StepInterface(self, "Confirmation", self.choose_frame),
        ]
        self._idx: int = 0
        self.current_frame = self._frames[0]

    def choose_frame(self, ret_val):
        if ret_val == CANCEL_STR:
            self._idx -= 1
        else:
            self._idx += 1
        if self._idx < 0 or self._idx >= len(self._frames):
            self.quit()
        self.current_frame = self._frames[self._idx]

    @property
    def current_frame(self):
        return self._current_frame

    @current_frame.setter
    def current_frame(self, new_frame):
        if isinstance(self._current_frame, StepInterface):
            self._current_frame.hide()
        self._current_frame = new_frame
        if isinstance(new_frame, StepInterface):
            new_frame.show()


def main():
    app = App(width=800, height=480)
    app.mainloop()


if __name__ == "__main__":
    ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
    ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
    main()
