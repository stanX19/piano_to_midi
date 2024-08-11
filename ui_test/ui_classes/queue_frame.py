from typing import Callable, Any, Union
import customtkinter as ctk
from threading import Thread
from .queue_manager import QueueData, QueueManager
from .templates import *


class QueueItemBaseFrame(ctk.CTkFrame):
    def __init__(self, master, data: QueueData, idx: int):
        super().__init__(master)
        self.data = data
        self.idx = int(idx)

    def show(self):
        if self.winfo_viewable():
            return
        self.grid_forget()
        self.refresh()
        self.update_idletasks()
        self.grid(row=self.idx, column=0, ipadx=0, ipady=0, padx=5, pady=(5, 0), sticky="nsew")

    def hide(self):
        self.grid_forget()

    def change_data(self, data: QueueData):
        if self.data is data:
            return
        self.data = data
        self.refresh()

    def refresh(self):
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

    def refresh(self):
        self.content_entry.configure(textvariable=self.data.src_filename_var)
        self.checkbox.configure(variable=self.data.is_selected_var)
        self.index_label.configure(text=str(self.idx))


class QueueContainerFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, queue_manager: QueueManager, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.queue_manager: QueueManager = queue_manager
        self.queue_frame_list: list[QueueItemBaseFrame] = []

        default_font = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        default_colors1 = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        default_colors2 = ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"]
        text_color = default_colors1 if self.cget('fg_color') is not default_colors1 else default_colors2
        self.queue_is_empty_label: ctk.CTkLabel = ctk.CTkLabel(self, text="Queue is empty",
                                                               font=(default_font[0], 36, "bold"),
                                                               text_color=text_color)
        self.grid_columnconfigure(0, weight=1)
        self._refresh_thread: Union[None, Thread] = None
        self._refresh_needed: bool = False
        self.refresh()

    def refresh(self):
        print("refresh called")
        if self._refresh_thread:
            self._refresh_needed = True
            print("refresh ongoing, queued")
            return
        self._refresh_thread = Thread(target=self._refresh)
        self._refresh_thread.start()

    def _refresh(self) -> None:
        print("refreshing")
        # Update existing frames
        queue_list = self.get_queue_data()
        min_len = min(len(queue_list), len(self.queue_frame_list))

        for idx in range(min_len):
            frame = self.queue_frame_list[idx]
            data = queue_list[idx]
            frame.change_data(data)

        # add missing frames
        for idx in range(min_len, len(queue_list)):
            data = queue_list[idx]
            frame = self.get_new_item_frame(data)
            self.queue_frame_list.append(frame)

        # remove extra frames
        if len(self.queue_frame_list) > len(queue_list):
            for frame in self.queue_frame_list[len(queue_list):]:
                frame.destroy()
            self.queue_frame_list = self.queue_frame_list[:len(queue_list)]

        for frame in self.queue_frame_list:
            frame.show()

        if not self.queue_frame_list:
            self.queue_is_empty_label.grid(row=0, pady=0)
        else:
            self.queue_is_empty_label.grid_forget()
        self.after(0, self._end_refresh)
        print("refresh done")

    def _end_refresh(self):
        self._refresh_thread.join()
        self._refresh_thread = None
        if self._refresh_needed:
            self._refresh_needed = False
            self.refresh()

    def get_queue_data(self):
        return self.queue_manager.queue_list

    def get_new_item_frame(self, data) -> QueueItemBaseFrame:
        return QueueItemFrame(self, data, len(self.queue_frame_list) + 1)


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
        self.container_frame.grid_rowconfigure(2, weight=1)

        # Index frame and label
        self.index_frame = ctk.CTkFrame(self.container_frame, width=100, height=100)
        self.index_label = ctk.CTkLabel(self.index_frame, text=f"{idx}")

        # Source path label and entry (readonly)
        self.src_label = CtkEntryLabel(self.container_frame, text="Source Path:", width=100)
        self.src_path_label = CtkEntryLabel(self.container_frame, text=data.src_path, width=100000)

        # Save as label and entry (editable)
        self.save_as_label = CtkEntryLabel(self.container_frame, text="Save As:", width=100)
        self.save_as_entry = ctk.CTkEntry(self.container_frame, textvariable=data.title_var, width=100000,
                                          state="normal")

        # Checkbox
        self.remove_button = ctk.CTkButton(self.container_frame, text="Remove", width=0)
        self.reset_button = ctk.CTkButton(self.container_frame, text="Reset", width=0)

        # Pack and grid all components
        self.index_label.pack(expand=True)
        self.index_frame.grid(row=0, rowspan=3, column=0, padx=(5, 0), pady=5, ipadx=15, ipady=5, sticky="nsew")
        self.src_label.grid(row=0, column=1, padx=(5, 5), pady=(5, 0), sticky="nsew")
        self.src_path_label.grid(row=0, column=2, padx=(5, 5), pady=(5, 0), ipadx=5, ipady=0, sticky="nsew")
        self.save_as_label.grid(row=1, column=1, padx=(5, 5), pady=(0, 5), sticky="nsew")
        self.save_as_entry.grid(row=1, column=2, padx=(5, 5), pady=(0, 5), ipadx=5, ipady=0, sticky="nsew")
        self.remove_button.grid(row=0, column=3, padx=5, pady=5, ipady=5, ipadx=5, sticky="nsew")
        self.reset_button.grid(row=1, column=3, padx=5, pady=5, ipady=5, ipadx=5, sticky="nsew")

    def on_remove(self):
        self.remove_button.configure(state=ctk.DISABLED)
        self.data.is_selected_var.set(False)
        self._unselect_callback_func()

    def refresh(self):
        self.src_path_label.configure(textvariable=self.data.src_filename_var)
        self.save_as_entry.configure(textvariable=self.data.title_var)
        self.index_label.configure(text=str(self.idx))
        self.remove_button.configure(state=ctk.NORMAL)
        self.remove_button.configure(command=self.on_remove)
        self.reset_button.configure(command=self.data.reset_title)

class QueueEditContainerFrame(QueueContainerFrame):
    def __init__(self, master, queue_manager: QueueManager, *args, **kwargs):
        super().__init__(master, queue_manager, *args, **kwargs)

    def get_queue_data(self):
        return self.queue_manager.selected_list

    def get_new_item_frame(self, data):
        return QueueItemEditFrame(self, data, len(self.queue_frame_list) + 1,
                                  unselect_callback_func=self.unselect_data_callback)

    def unselect_data_callback(self):
        self.refresh()
