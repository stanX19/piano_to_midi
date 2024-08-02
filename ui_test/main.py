import customtkinter as ctk
import pathlib
import re
from typing import Callable, Any, Union


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
        self.title_frame = ctk.CTkFrame(self, height=0)
        self.title_frame.grid(row=0, column=0, pady=5, padx=5, sticky='nsew')

        self.title_label = ctk.CTkLabel(self.title_frame, text=title, font=("Arial", 16, "bold"))
        self.title_label.pack(pady=5, padx=5)

        # Content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, padx=5, pady=0, sticky='nsew')

        self.error_label = ctk.CTkLabel(self.content_frame, text="", text_color="red")
        self.error_label.pack(side=ctk.BOTTOM)

        # Button frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, pady=5, padx=5, sticky='ew')

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
        return self._result_handler_func(CANCEL_STR)

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
        self.description_label = ctk.CTkLabel(self.content_frame, text=description, justify=ctk.LEFT)
        self.description_label.pack(side=ctk.TOP, anchor=ctk.NW, pady=5, padx=5, fill=ctk.BOTH, expand=True)
        self.entry = ctk.CTkEntry(self.content_frame)
        self.entry.insert(0, default)
        self.entry.pack(side=ctk.TOP, fill=ctk.BOTH, pady=5, padx=5)

    def on_next(self):
        self.error_label.configure(text="")
        return self._result_handler_func(self.entry.get())


class SelectFileFrame(StepInterface):
    def __init__(self, root: ctk.CTk, title: str, result_handler_func: Callable[[str], Any],
                 force_extension=None):
        super().__init__(root, title, result_handler_func)
        self.entry_frame = ctk.CTkFrame(self.content_frame)
        self.entry_frame.pack(padx=5, pady=5, expand=True, fill=ctk.X)
        self.entry = ctk.CTkEntry(self.entry_frame)
        self.entry.pack(side=ctk.LEFT, expand=True, fill=ctk.X)
        self.entry.bind("<Return>", lambda event: self.next_button.invoke())
        self.select_file_button = ctk.CTkButton(self.entry_frame, text="Select file", command=self.select_file, width=0)
        self.select_file_button.pack(side=ctk.RIGHT)

        self._force_extension = re.sub(r'^[.*]+', '', force_extension) if force_extension else None

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

    def on_next(self):
        filepath = pathlib.Path(self.entry.get())
        if not filepath.exists():
            self.error_label.configure(text="Invalid file path")
        elif not filepath.match(self.get_extension_pattern()):
            self.error_label.configure(text=f"Is not a {self._force_extension} file")
        else:
            self._result_handler_func(filepath.__str__())


class App(ctk.CTk):
    def __init__(self, width=400, height=240):
        super(App, self).__init__()
        self.geometry(f"{width}x{height}")
        self.title('Piano to midi')
        self.width = width
        self.height = height
        self.queue = []
        self._frame_history: list[StepInterface] = []
        self._steps: list[Callable] = [
            self.select_video,
            self.get_details,
            self.process_video
        ]
        self._idx = 0
        self.select_video()

    @property
    def current_frame(self):
        if not self._frame_history:
            return None
        return self._frame_history[-1]

    @current_frame.setter
    def current_frame(self, new_frame):
        if not isinstance(new_frame, StepInterface):
            return
        # start of steps
        if not self._frame_history:
            new_frame.show()
            self._frame_history.append(new_frame)
            return
        # repeated
        if new_frame is self._frame_history[-1]:
            return
        # need to hide and show
        self._frame_history[-1].hide()
        if new_frame not in self._frame_history:
            self._frame_history.append(new_frame)
        else:
            self._frame_history = self._frame_history[:self._frame_history.index(new_frame) + 1]
        new_frame.show()

    def choose_frame(self, ret_val):
        if ret_val == CANCEL_STR:
            self._idx -= 1
            if self._frame_history.__len__() >= 2:
                self.current_frame = self._frame_history[-2]
            return
        elif self._idx + 1 >= self._steps.__len__():
            self.quit()
        else:
            self._idx += 1
        self._steps[self._idx](ret_val)

    def select_video(self, *args):
        self.current_frame = SelectFileFrame(self, "Piano to midi - convert piano videos to midi", self.choose_frame,
                                             force_extension=".mp4")
        self.current_frame.cancel_button.pack_forget()

    def get_details(self, filepath: str):
        default = pathlib.Path(filepath).stem
        self.current_frame = InputFrame(self, "Save as", self.choose_frame,
                                        f"Video path: {filepath}\nName: ", default=default)

    def process_video(self, path):
        self.current_frame = StepInterface(self, "Confirmation", self.choose_frame)
        info_label = ctk.CTkLabel(self.current_frame.content_frame,
                                  text=f"Video path: {path}\nUse history: {False}\nName: {path}",
                                  font=("Consolas", 16),
                                  justify=ctk.LEFT, wraplength=300)
        info_label.pack(fill=ctk.BOTH, pady=(10, 0), expand=True)


def main():
    app = App(width=800, height=480)
    app.mainloop()


if __name__ == "__main__":
    ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
    ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
    main()
