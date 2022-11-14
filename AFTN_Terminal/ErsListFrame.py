from tkinter import Tk, END, VERTICAL, Scrollbar, RIGHT, Y, CENTER, messagebox, BOTH, Frame, Toplevel, Button, X
from tkinter.ttk import Treeview

from AFTN_Terminal.ReadXml import ReadXml


class ErsListFrame(Frame):
    """This class builds a dialogue window to display the extracted route for a flight plan. The ERS
    window uses a Treeview list to display the extracted route records.
    """

    def __init__(self, parent, selected_path):
        # type: (Tk, str) -> None
        """This method builds the ERS dialogue using a Frame; the dialogue window is populated with a
        Treeview list and a frame containing a cancel button.

        :param parent: Handle to the parent window;
        :param selected_path: The path to a file for a message selected in the message list window or the main
               application window tree view;
        """
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
    """This method builds a Treeview list as a list used to display a flight plan extracted route sequence.
    """

    selected_path = ""
    """The path to a file for a message selected in the message list window or the main
    application window tree view;"""

    def __init__(self, parent, selected_path):
        # type: (Toplevel, str) -> None
        """This constructor builds a Treeview as a list used to display a flight plan extracted route sequence.

        :param parent: Handle to the parent window;
        :param selected_path: The path to a file for a message selected in the message list window or the main
               application window tree view. The file contains a flight plan containing the extracted route
               sequence to display.
        """
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
        """This method retrieves the ERS records from a flight plan record and adds the ERS records
        to 'this' Treeview list.

        :return: True if the file specified by the 'selected_path' contains an extracted route sequence,
                 False if the file did not contain an ERS.
        """
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
    """This class creates a from containing a single 'Cancel' button to close the ErrListFrame in
    which this frame is displayed.
    """

    def __init__(self, parent):
        # type: (Toplevel) -> None
        """This constructor adds a 'Cancel' button to 'this' Frame;

        :param parent: Handle to the parent window;
        """
        super().__init__(parent)

        # Add the buttons
        cancel_button = Button(self, text="Cancel", command=parent.destroy)
        cancel_button.pack(side="right", anchor="ne", pady=3, padx=3)
