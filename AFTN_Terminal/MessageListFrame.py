import os
from tkinter import PanedWindow, END, VERTICAL, Scrollbar, RIGHT, Y, CENTER, Menu, Event
from tkinter.messagebox import askyesno
from tkinter.ttk import Treeview

from AFTN_Terminal.ErsListFrame import ErsListFrame
from AFTN_Terminal.ReadXml import ReadXml
from AFTN_Terminal.MenuBar import MenuBar
from AFTN_Terminal.MessageDisplayFrame import MessageDisplayFrame
from AFTN_Terminal.MessageTextEditorFrame import MessageTextEditorFrame
from Configuration.EnumerationConstants import MessageTitles


class MessageListFrame(Treeview):
    selected_item: str = None
    selected_path: str = ""
    popup_menu: Menu = None
    menu_bar: MenuBar = None
    message_display_frame: MessageDisplayFrame = None

    def __init__(self, parent, menu_bar):
        # type: (PanedWindow, MenuBar) -> None

        # Define columns
        columns = ('priority', 'filing_time', 'title', 'callsign', 'type', 'wtc', 'adep', 'eobt', 'ades', 'field-15')

        # Call super init and pass the headings to it...
        super().__init__(parent, columns=columns, show='headings')

        # Define headings
        self.heading(columns[0], text='Prio.')
        self.heading(columns[1], text='Fil. Time')
        self.heading(columns[2], text='Title')
        self.heading(columns[3], text='Callsign')
        self.heading(columns[4], text='A/C Type')
        self.heading(columns[5], text='WTC')
        self.heading(columns[6], text='ADEP')
        self.heading(columns[7], text='EOBT')
        self.heading(columns[8], text='ADES')
        self.heading(columns[9], text='Field 15')
        self.column(0, width=40, stretch=False, anchor=CENTER)
        self.column(1, width=60, stretch=False, anchor=CENTER)
        self.column(2, width=60, stretch=False, anchor=CENTER)
        self.column(3, width=80, stretch=False, anchor=CENTER)
        self.column(4, width=80, stretch=False, anchor=CENTER)
        self.column(5, width=60, stretch=False, anchor=CENTER)
        self.column(6, width=70, stretch=False, anchor=CENTER)
        self.column(7, width=70, stretch=False, anchor=CENTER)
        self.column(8, width=70, stretch=False, anchor=CENTER)
        # Column 9 fills the remaining space, F15...
        # NOTE: Column 10 (which is not displayed) is used to store the path and filename
        # of the message displayed in the list.

        # Create the list popup
        self.popup_create()

        # Handle to the menu bar
        self.menu_bar = menu_bar

        # Add a scrollbar
        vertical = Scrollbar(self, orient=VERTICAL, command=self.yview)
        vertical.pack(side=RIGHT, fill=Y)
        self.configure(yscrollcommand=vertical.set)

        # Bind the callbacks for single and double clicks
        self.bind('<Button-1>', self.on_single_click)
        self.bind('<ButtonRelease-1>', self.on_release_click)
        self.bind('<Double-1>', self.on_double_click)
        self.bind('<Button-3>', self.on_right_click)

    def display_ers(self):
        ErsListFrame(self, self.selected_path)

    def on_release_click(self, event):
        # type: (Event) -> None

        # Get the selected item
        self.selected_item = self.identify('item', event.x, event.y)

        # If nothing is selected, clear the message display area and bail out
        if self.selected_item is None or len(self.selection()) == 0:
            # Nothing selected, disable the main menu 'Open Message' item
            self.menu_bar.set_open_message_menu_state(False)
        else:
            # Message selected, enable the main menu 'Open Message' item
            self.menu_bar.set_open_message_menu_state(True)

    def on_single_click(self, event):
        # type: (Event) -> None

        # Get the selected item
        self.selected_item = self.identify('item', event.x, event.y)

        # If there is no selection then bail out
        if self.selected_item is None or len(self.selected_item) == 0:
            return

        # Store the path and filename for the currently selected message
        self.set_selected_path()

        # Display the selected message in the message display area
        self.message_display_frame.set_message(self.selected_path)

        # Pass the path and filename to the menu bar in case a message is opened from the menu
        self.menu_bar.set_selected_path(self.selected_path)

    def on_double_click(self, event):
        # type: (Event) -> None

        # Get the selected item
        self.selected_item = self.identify('item', event.x, event.y)

        # If there is no selection then bail out
        if self.selected_item is None or self.selected_item == "":
            return

        # Store the path and filename for the currently selected message
        self.set_selected_path()

        # Display the selected message in the message display area
        self.message_display_frame.set_message(self.selected_path)

        # Pass the path and filename to the menu bar in case a message is opened from the menu
        self.menu_bar.set_selected_path(self.selected_path)

        # Open the message editor with the selected message
        rx = ReadXml(self.selected_path)
        if rx.is_message_ok():
            mte = MessageTextEditorFrame(self, False, MessageTitles.UNKNOWN,
                                         rx.get_creation_time(), rx.get_modification_time(), "")
            mte.set_message(self.selected_path)

    def on_right_click(self, event):
        # type: (Event) -> None

        # Get the selected item
        self.selected_item = self.identify('item', event.x, event.y)

        # If there is no selection then bail out
        if self.selected_item is None or self.selected_item == "":
            return

        # Store the path and filename for the currently selected message
        self.set_selected_path()

        # Highlight the selection in the GUI that the right click occurred on
        self.selection_set(self.selected_item)

        # Display the popup menu
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # Make sure to release the grab (Tk 8.0a1 only)
            self.popup_menu.grab_release()

    def on_open_file(self):
        # type: () -> None

        rx = ReadXml(self.selected_path)
        if rx.is_message_ok():
            # Display the message editor
            mtep = MessageTextEditorFrame(self, False, MessageTitles.UNKNOWN,
                                          rx.get_creation_time(), rx.get_modification_time(), "")
            # Pass the full path and filename to the editor
            mtep.set_message(self.selected_path)

    def on_delete(self):
        # type: () -> None

        # The list entries should all be files, but check if it is...
        isdir = os.path.isdir(self.selected_path)
        if not isdir:
            # Delete a file, display a confirmation dialogue
            answer = askyesno("Delete Message Confirmation",
                              "Are you sure you want to delete the Message:\n"
                              + self.selected_path, parent=self)
            if answer:
                # Delete the node from the tree
                self.delete(self.selection()[0])

    def popup_focus_out(self, event):
        # type: (Event) -> None

        # Close the popup when it loses the focus
        self.popup_menu.unpost()

    def popup_create(self):
        # type: () -> None

        # Create menu
        self.popup_menu = Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Open Message...", command=self.on_open_file)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Delete Message", command=self.on_delete)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Display ERS...", command=self.display_ers)
        self.popup_menu.bind("<FocusOut>", self.popup_focus_out)

    def set_selected_path(self):
        # type: () -> None

        # Get the index where the full path for the message is stashed
        index = len(self.item(self.selected_item)["values"])

        # Store the path and file name of the current selected message
        self.selected_path = self.item(self.selected_item)["values"][index - 1]

    def set_message_display_frame(self, message_display_frame):
        # type: (MessageDisplayFrame) -> None
        self.message_display_frame = message_display_frame

    def update_list_entries(self, file_paths):
        # type: ([str]) -> None

        # Delete all the list entries currently on display
        for row in self.get_children():
            self.delete(row)

        # Clear the editor if there are no messages to display
        if len(file_paths) == 0:
            self.message_display_frame.set_message("")
            self.menu_bar.set_open_message_menu_state(False)
            return

        # Loop over the list of tree child nodes and add the message
        # files to the list of messages
        for file_path in file_paths:
            isdir = os.path.isdir(file_path)
            if not isdir:
                rx = ReadXml(file_path)
                if rx.is_message_ok():
                    self.insert('', END,
                                values=(rx.get_priority_indicator(),
                                        rx.get_filing_time(),
                                        rx.get_f3a(),
                                        rx.get_f7a(),
                                        rx.get_f9b(),
                                        rx.get_f9c(),
                                        rx.get_f13a(),
                                        rx.get_f13b(),
                                        rx.get_f16a(),
                                        rx.get_f15(),
                                        file_path))
