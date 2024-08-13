
#
# class InterfaceManager:
#     def __init__(self, master: ctk.CTk, steps: list[StepInterface]):
#         self.master: ctk.CTk = master
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
