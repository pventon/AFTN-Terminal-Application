from tkinter import Frame, Label, N, S, W, E, Y

import datetime as dt
from tkinter.ttk import Separator


class StatusBar(Frame):

    time_label = None

    def __init__(self, parent):
        super().__init__(parent, borderwidth=2, relief="groove")
        self.grid(column=0, row=2, sticky=N + E + W + S)

        # Create Label to display the Date
        self.time_label = Label(self, font="Arial, 10")
        self.time_label.after(1000, self.update_time)
        self.time_label.pack(side="right", pady=3, padx=3)

        # Add a seperator
        separator = Separator(self, orient='vertical')
        separator.pack(side="right", pady=3, padx=3, fill=Y)

    def update_time(self):
        date = dt.datetime.now()
        self.time_label.config(text=f"{date:%A, %B %d, %Y %H:%M:%S}")
        self.time_label.after(1000, self.update_time)
