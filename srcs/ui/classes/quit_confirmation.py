import customtkinter as ctk
from typing import Callable


class QuitConfirmationPopup(ctk.CTkToplevel):
    def __init__(self, parent: ctk.CTk, running_tasks: list[str], on_confirm: Callable):
        super().__init__(parent)
        self.grab_set()
        self.title("Confirm Quit")
        self.parent: ctk.CTk = parent
        self.running_tasks: list[str] = running_tasks
        self.on_confirm: Callable = on_confirm

        # self.grid_rowconfigure(1, weight=1)
        # Label with the confirmation message
        message = "Some tasks are still running, are you sure you want to quit?"
        label = ctk.CTkLabel(self, text=message, wraplength=250)
        label.grid(row=0, pady=(5, 0), padx=10)

        self.show_details_button = ctk.CTkButton(self, text="Details",
                                                 command=self.show_details, text_color="black",
                                                 fg_color="transparent")
        self.show_details_button.grid(row=1)
        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, pady=5)

        # Confirm button
        confirm_button = ctk.CTkButton(button_frame, text="Quit", command=self.confirm)
        confirm_button.pack(side=ctk.RIGHT, padx=5)

        # Cancel button
        cancel_button = ctk.CTkButton(button_frame, text="Back", command=self.destroy)
        cancel_button.pack(side=ctk.LEFT, padx=5)

    def show_details(self):
        self.show_details_button.grid_forget()
        if not self.running_tasks:
            no_tasks_running = ctk.CTkLabel(self, text="No tasks running, safe to quit")
            no_tasks_running.grid(row=1, padx=5, pady=0)
            return

        tasks_frame = ctk.CTkFrame(self, fg_color="transparent")
        tasks_frame.grid(row=1, pady=0, padx=0, sticky="nsew")

        for task in self.running_tasks:
            task_container = ctk.CTkFrame(tasks_frame)
            task_container.pack(anchor='w', padx=5, pady=(5, 0), fill=ctk.X)
            task_label = ctk.CTkLabel(task_container, text=f"{task}")
            task_label.pack(anchor='w', fill=ctk.X)

    def confirm(self):
        self.on_confirm()
        self.after(0, self.destroy)
