from tkinter import END, VERTICAL, Scrollbar, RIGHT, Y, CENTER, messagebox, BOTH, Frame, Toplevel, Button, X
from tkinter.ttk import Treeview

from AFTN_Terminal.ReadXml import ReadXml


class ErsListFrame(Frame):

    def __init__(self, parent, selected_path):
        # type (Tk, str) -> None

        # Get a handle to the top level widget
        top_level = Toplevel(parent)
        # Set a few things...
        top_level.minsize(width=700, height=200)
        top_level.title("Extracted Route Sequence")

        # Initialise the super instance
        super().__init__(top_level)

        # Create and add the ERS list
        ers_list = ErsList(top_level, selected_path)
        ers_list.pack(expand=1, fill=BOTH)

        # Create and add the button panel
        ers_button_frame = ErsButtonFrame(top_level)
        ers_button_frame.pack(expand=0, fill=X)


class ErsList(Treeview):
    selected_path = ""

    def __init__(self, parent, selected_path):
        # type: (Toplevel, str) -> None

        # Define columns
        columns = ('item', 'speed', 'altitude', 'bearing', 'distance', 'rules', 'break_text')

        # Call super init and pass the headings to it...
        super().__init__(parent, columns=columns, show='headings')

        # Save the path for the message containing the ERS
        self.selected_path = selected_path

        # Define headings
        self.heading(columns[0], text='Item')
        self.heading(columns[1], text='Speed')
        self.heading(columns[2], text='Altitude')
        self.heading(columns[3], text='Bearing')
        self.heading(columns[4], text='Distance')
        self.heading(columns[5], text='Rules')
        self.heading(columns[6], text='Break Text')
        self.column(0, width=90, stretch=False, anchor=CENTER)
        self.column(1, width=70, stretch=False, anchor=CENTER)
        self.column(2, width=80, stretch=False, anchor=CENTER)
        self.column(3, width=90, stretch=False, anchor=CENTER)
        self.column(4, width=90, stretch=False, anchor=CENTER)
        self.column(5, width=50, stretch=False, anchor=CENTER)
        # Column 6 fills the remaining space, contains the 'break text'

        # Populate the ERS list
        if not self.get_ers_records():
            # Error
            messagebox.showerror(
                title="ERS Display Error",
                message="The selected ATS Message does not contain an Extracted Route Sequence")

        # Add a scrollbar
        vertical = Scrollbar(self, orient=VERTICAL, command=self.yview)
        self.configure(yscrollcommand=vertical.set)
        vertical.pack(side=RIGHT, fill=Y)

    def get_ers_records(self):
        # type: () -> bool

        # Read the message file
        rx = ReadXml(self.selected_path)

        if rx.is_message_ok():
            records = rx.get_ers_list_items()
            for record in records:
                self.insert('', END, values=record)
            return True
        else:
            return False


class ErsButtonFrame(Frame):

    def __init__(self, parent):
        # type: (Toplevel) -> None
        super().__init__(parent)

        # Add the buttons
        cancel_button = Button(self, text="Cancel", command=parent.destroy)
        cancel_button.pack(side="right", anchor="ne", pady=3, padx=3)
