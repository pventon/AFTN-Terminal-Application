from tkinter import Tk, Frame, Label, N, S, W, E, Y

import datetime as dt
from tkinter.ttk import Separator


class StatusBar(Frame):
    """This class build a status bar displayed in the main application window.
    More items will be added to this status bar when further updates are made to the AFTN
    Terminal Application."""

    time_label = None
    """A label widget displaying the current time;"""

    def __init__(self, parent):
        # type: (Tk) -> None
        """This constructor builds the main application status bar.

        :param parent: Handle to the parent window;
        """
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
        # type: () -> None
        """This method updates the time displayed in the status bar; The label widget is created
        with a 'timer' to call this method every second.

        :return: None
        """
        date = dt.datetime.now()
        self.time_label.config(text=f"{date:%A, %B %d, %Y %H:%M:%S}")
        self.time_label.after(1000, self.update_time)
