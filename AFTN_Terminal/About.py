import os
from tkinter import Tk, Frame, Toplevel, Label, LEFT


class About(Frame):
    """This class builds an 'About' dialogue instantiated from the menu or toolbar;"""

    def __init__(self, parent):
        # type: (Tk) -> None
        """This constructor builds an 'About' dialogue instantiated from the menu and toolbar;"""

        super().__init__(parent)

        top_level = Toplevel(parent)
        label = Label(top_level, font="Arial, 11", justify=LEFT, padx=10, pady=10, width=40,
                      text="AFTN Terminal Application;" + os.linesep +
                           "Version: 1.0" + os.linesep +
                           "Release Date: December 2022" + os.linesep +
                           "Author: Peter Venton" + os.linesep +
                           "Software: Python 3.8.10" + os.linesep +
                           "License: GPL")
        label.pack()
