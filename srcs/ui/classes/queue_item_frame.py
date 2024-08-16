from typing import Callable, Any, Union
import customtkinter as ctk
from threading import Thread
from .queue_manager import QueueData, QueueManager
from .templates import CtkEntryLabel, CtkWrappingLabel
from .process_display_frame import CtkProcessDisplayFrame
from .run_in_thread_handler import RunInThreadHandler


class QueueItemBaseFrame(ctk.CTkFrame):
    def __init__(self, master, data: QueueData, idx: int):
        super().__init__(master)
        self.data: QueueData = data
        self.idx: int = int(idx)

    def show(self):
        if self.winfo_viewable():
            return
        self.grid_forget()
        self.grid(row=self.idx, column=0, ipadx=0, ipady=0, padx=(5, 0), pady=(5, 0), sticky="nsew")

    def hide(self):
        self.grid_forget()

    def set_idx(self, idx: int):
        if idx == self.idx:
            return
        self.idx = idx
        self._refresh_idx()

    def _refresh_idx(self):
        pass


class QueueItemFrame(QueueItemBaseFrame):
    def __init__(self, master, data: QueueData, idx: int):
        super().__init__(master, data, idx)
        self.container_frame = ctk.CTkFrame(self)
        self.container_frame.pack(fill=ctk.BOTH)
        self.container_frame.grid_columnconfigure(0, weight=0)  # index_frame
        self.container_frame.grid_columnconfigure(1, weight=1)  # content_label
        self.container_frame.grid_columnconfigure(2, weight=0)  # checkbox
        self.container_frame.grid_rowconfigure(0, weight=1)
        self.container_frame.grid_rowconfigure(1, weight=0)

        self.index_frame = ctk.CTkFrame(self.container_frame, width=40, height=40)
        self.index_label = ctk.CTkLabel(self.index_frame, text=f"{idx}")
        self.content_entry = CtkEntryLabel(self.container_frame, textvariable=data.src_filename_var, width=100000)
        self.checkbox = ctk.CTkCheckBox(self.container_frame, text="", width=0, variable=data.is_selected_var)
        self.checkbox.select()

        self.index_label.pack(expand=True)
        self.index_frame.grid(row=0, rowspan=2, column=0, padx=(5, 0), pady=5, ipadx=15, ipady=5, sticky="nsew")
        self.content_entry.grid(row=1, column=1, padx=(5, 5), pady=5, ipadx=5, ipady=5, sticky="nsew")
        self.checkbox.grid(row=0, rowspan=2, column=2, padx=0, pady=5, ipady=5, sticky="nsew")

    def _refresh_idx(self):
        self.index_label.configure(text=str(self.idx))


class QueueItemEditFrame(QueueItemBaseFrame):
    def __init__(self, master, data: QueueData, idx: int, unselect_callback_func: Callable):
        super().__init__(master, data, idx)
        self._unselect_callback_func = unselect_callback_func

        # Initialize container frame
        self.container_frame = ctk.CTkFrame(self)
        self.container_frame.pack(fill=ctk.BOTH)
        self.container_frame.grid_columnconfigure(0, weight=0, minsize=80)  # index_frame
        self.container_frame.grid_columnconfigure(1, weight=0)  # labels and entries
        self.container_frame.grid_columnconfigure(2, weight=1)  # entries
        self.container_frame.grid_columnconfigure(3, weight=0, minsize=80)  # checkbox
        self.container_frame.grid_rowconfigure(0, weight=1)
        self.container_frame.grid_rowconfigure(1, weight=1)
        # self.container_frame.grid_rowconfigure(2, weight=1)

        # Index frame and label
        self.index_frame = ctk.CTkFrame(self.container_frame, width=100, height=100)
        self.index_label = ctk.CTkLabel(self.index_frame, text=f"{idx}")

        # Source path label and entry (readonly)
        self.src_label = CtkEntryLabel(self.container_frame, text="Source Path:", width=100)
        self.save_as_label = CtkEntryLabel(self.container_frame, text="Save As:", width=100)
        self.src_path_label = CtkEntryLabel(self.container_frame, text=data.src_path, width=0)

        # Save as label and entry (editable)
        self.save_as_entry = ctk.CTkEntry(self.container_frame, textvariable=data.title_var,
                                          state="normal", width=0)

        # Checkbox
        self.remove_button = ctk.CTkButton(self.container_frame, text="Unselect", width=0, command=self._on_unselect)
        self.reset_button = ctk.CTkButton(self.container_frame, text="Reset", width=0, command=self.data.reset_title)

        # Pack and grid all components
        self.index_label.pack(expand=True)
        self.index_frame.grid(row=0, rowspan=3, column=0, padx=(5, 0), pady=5, ipadx=15, ipady=5, sticky="nsew")
        self.src_label.grid(row=0, column=1, padx=(5, 5), pady=(5, 0), sticky="nsew")
        self.src_path_label.grid(row=0, column=2, padx=(5, 5), pady=(5, 0), ipadx=5, ipady=0, sticky="nsew")
        self.save_as_label.grid(row=1, column=1, padx=(5, 5), pady=(0, 5), sticky="nsew")
        self.save_as_entry.grid(row=1, column=2, padx=(5, 5), pady=(0, 5), ipadx=5, ipady=0, sticky="nsew")
        self.remove_button.grid(row=0, column=3, padx=5, pady=(10, 5), ipady=5, ipadx=5, sticky="nsew")
        self.reset_button.grid(row=1, column=3, padx=5, pady=(0, 5), ipady=5, ipadx=5, sticky="nsew")

    def _on_unselect(self):
        self.remove_button.configure(state=ctk.DISABLED)
        self.data.is_selected_var.set(False)
        self._unselect_callback_func()

    def _refresh_idx(self):
        self.index_label.configure(text=str(self.idx))


class QueueItemProcessFrame(QueueItemBaseFrame):
    def __init__(self, master, data: QueueData, idx: int):
        super().__init__(master, data, idx)

        self.container_frame = ctk.CTkFrame(self)
        self.container_frame.pack(fill=ctk.BOTH)
        # self.container_frame.grid_columnconfigure(0, weight=0)  # labels
        # self.container_frame.grid_columnconfigure(1, weight=1)  # status and save_as
        # self.container_frame.grid_columnconfigure(2, weight=0)  # buttons
        # self.container_frame.grid_rowconfigure(0, weight=1)     # video frame
        # self.container_frame.grid_rowconfigure(1, weight=0)     # progress bar
        # self.container_frame.grid_rowconfigure(2, weight=0)     # line 1
        # self.container_frame.grid_rowconfigure(3, weight=0)     # line 2
        self.container_frame.grid_columnconfigure(0, weight=0)  # video
        self.container_frame.grid_columnconfigure(1, weight=1)  # labels

        self.video_container_frame = ctk.CTkFrame(self.container_frame)
        self.progress_bar = ctk.CTkProgressBar(self.video_container_frame)
        self.video_frame = CtkProcessDisplayFrame(self.video_container_frame, data.processor, height=720, width=1280,
                                                  progress_bar=self.progress_bar)
        self.video_container_frame.grid_rowconfigure(0, weight=1)
        self.video_container_frame.grid_rowconfigure(1, weight=0)

        self.progress_bar.grid(row=1, sticky="nsew")
        self.video_frame.grid(row=0, sticky="sew")

        self.status_label = CtkWrappingLabel(self.container_frame, text="Status", anchor=ctk.SW)
        self.save_as_label = CtkWrappingLabel(self.container_frame, text="Saving as", anchor=ctk.SW)
        self.status_text_label = CtkWrappingLabel(self.container_frame, text="Not Started", anchor=ctk.NW)
        self.save_as_text_label = CtkWrappingLabel(self.container_frame, text=data.get_save_path(), anchor=ctk.NW)

        self.pause_btn = ctk.CTkButton(self.container_frame, text="Start", command=self.on_resume)
        self.change_btn = ctk.CTkButton(self.container_frame, text="Change", command=self.on_change)

        # self.video_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=(5, 0), ipadx=5, sticky="nsew")
        # self.progress_bar.grid(row=1, column=0, columnspan=3, padx=5, pady=(5, 0), ipadx=5, sticky="nsew")
        # self.status_label.grid(row=2, column=0, padx=5, pady=(5, 0), ipadx=5, sticky="nsew")
        # self.save_as_label.grid(row=3, column=0, padx=5, pady=(5, 0), ipadx=5, sticky="nsew")
        # self.status_text_label.grid(row=2, column=1, padx=5, pady=(5, 0), ipadx=5, sticky="nsew")
        # self.save_as_text_label.grid(row=3, column=1, padx=5, pady=(5, 0), ipadx=5, sticky="nsew")
        # self.pause_btn.grid(row=2, column=2, padx=5, pady=(5, 0), ipadx=5, sticky="nsew")
        # self.change_btn.grid(row=3, column=2, padx=5, pady=(5, 5), ipadx=5, sticky="nsew")
        self.video_container_frame.grid(row=0, column=0, rowspan=5, padx=5, pady=(5, 5), ipadx=5, sticky="nsew")
        self.status_label.grid(row=0, column=1, padx=5, pady=(5, 0), ipadx=5, sticky="nsew")
        self.status_text_label.grid(row=1, column=1, padx=(5, 5), pady=(5, 0), ipadx=5, sticky="nsew")
        self.save_as_label.grid(row=2, column=1, padx=5, pady=(5, 0), ipadx=5, sticky="nsew")
        self.save_as_text_label.grid(row=3, column=1, padx=(5, 5), pady=(5, 0), ipadx=5, sticky="nsew")
        self.pause_btn.grid(row=4, column=1, padx=5, pady=(5, 0), ipadx=5, sticky="ew")

    def on_pause(self):
        print("pause!")
        self.pause_btn.configure(text="Resume", command=self.on_resume)

    def on_resume(self):
        # self.video_frame.expand_canvas()
        self.video_frame.play()
        RunInThreadHandler(self, target=self.data.processor.save_as, args=(self.data.get_save_path(), ))
        self.after(500, self.update_status_text)
        # self.pause_btn.configure(text="Pause", command=self.on_pause)
        self.pause_btn.configure(state=ctk.DISABLED)

    def update_status_text(self):
        self.status_text_label.configure(text=self.data.processor.state)
        if self.data.processor.is_completed():
            return
        self.after(500, self.update_status_text)

    def on_change(self):
        print("change? no change")
        self.change_btn.configure(state=ctk.DISABLED)

    def update_progress_bar(self):
        pass

    def show(self):
        super().show()
        self.update_idletasks()
        self.video_frame.update_frame()
        self.video_frame.update_progress_bar()
