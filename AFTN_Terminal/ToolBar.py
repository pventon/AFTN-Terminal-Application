import os
from idlelib.tooltip import Hovertip
from tkinter import Tk, Frame, N, W, S, E, Button, Y, NORMAL, DISABLED
from tkinter.messagebox import askyesno
from tkinter.ttk import Separator, Treeview

from PIL.ImageTk import PhotoImage

from AFTN_Terminal.About import About
from AFTN_Terminal.ErsListFrame import ErsListFrame
from AFTN_Terminal.MessageTextEditorFrame import MessageTextEditorFrame
from AFTN_Terminal.ReadXml import ReadXml
from Configuration.EnumerationConstants import MessageTitles


class ToolBar(Frame):
    """This class builds the main application window toolbar.
    Note: this class will be enhanced as further development on this application is made.
    Currently, the toolbar contains no active functionality."""

    parent: Tk = None
    """Handle to the parent window"""

    selected_path: str = ""
    """The path to a file for a message selected in the message list window or the main
    application window tree view;"""

    icon_root_path = os.path.split(os.getcwd())[0] + os.sep + "Icons" + os.sep + "Icon32" + os.sep
    """Absolute path to the Icons needed for the Tool bar"""

    working_directory_path: str = ""
    """The working directory used by this application to store messages in"""

    new_doc_button: Button = None
    """Button handle for the New Message button"""

    open_doc_button: Button = None
    """Button handle for the Open Currently Selected Message button"""

    delete_doc_button: Button = None
    """Button handle for the Delete Currently Selected Message button"""

    ers_button: Button = None
    """Button handle for the Display ERS button"""

    print_button: Button = None
    """Button handle for the Print Currently Selected Message button"""

    tree_view: Treeview = None
    """Handle to the Treeview widget displaying messages in the main application window"""

    def __init__(self, parent, working_directory_path):
        # type: (Tk, str) -> None
        """This constructor builds the toolbar frame and populates it with buttons to provide access
        to a number of message related functions.

        :param parent: Handle to the main application window;
        :param working_directory_path: The full absolute path to the working directory used by this
        application to store messages in;
        """

        super().__init__(parent, borderwidth=2, relief="groove")

        self.parent = parent
        self.working_directory_path = working_directory_path
        self.grid(column=0, row=0, sticky=N + E + W + S)

        # Create the icon images
        self.exit_icon = PhotoImage(file=self.icon_root_path + 'exit.png')
        self.new_doc_icon = PhotoImage(file=self.icon_root_path + 'document_add.png')
        self.open_doc_icon = PhotoImage(file=self.icon_root_path + 'document.png')
        self.delete_doc_icon = PhotoImage(file=self.icon_root_path + 'document_delete.png')
        self.ers_icon = PhotoImage(file=self.icon_root_path + 'document_info.png')
        self.print_icon = PhotoImage(file=self.icon_root_path + 'printer2.png')
        self.find_icon = PhotoImage(file=self.icon_root_path + 'find.png')
        self.about_icon = PhotoImage(file=self.icon_root_path + 'about.png')

        exit_button = Button(self, image=self.exit_icon, command=parent.destroy)
        exit_button.pack(side='left', anchor='nw', padx=2, pady=2)
        Hovertip(exit_button, "Close/Exit the Application", 300)

        separator = Separator(self, orient='vertical')
        separator.pack(side='left', pady=3, padx=3, fill=Y)

        self.new_doc_button = Button(self, image=self.new_doc_icon, command=self.open_new_message)
        self.new_doc_button.pack(side="left", anchor=N, padx=2, pady=2)
        Hovertip(self.new_doc_button, "Create New Message...", 300)

        self.open_doc_button = Button(self, image=self.open_doc_icon, command=self.open_message)
        self.open_doc_button.pack(side="left", anchor=N, padx=2, pady=2)
        Hovertip(self.open_doc_button, "Open Selected Message...", 300)

        self.delete_doc_button = Button(self, image=self.delete_doc_icon, command=self.delete_message)
        self.delete_doc_button.pack(side="left", anchor=N, padx=2, pady=2)
        Hovertip(self.delete_doc_button, "Delete Selected Message...", 300)

        self.ers_button = Button(self, image=self.ers_icon, command=self.display_ers)
        self.ers_button.pack(side="left", anchor=N, padx=2, pady=2)
        Hovertip(self.ers_button, "Display ERS for Selected Message...", 300)

        separator = Separator(self, orient='vertical')
        separator.pack(side='left', pady=3, padx=3, fill=Y)

        self.print_button = Button(self, image=self.print_icon)  # , command=.about)
        self.print_button.pack(side="left", anchor=N, padx=2, pady=2)
        Hovertip(self.print_button, "Print Selected Message...", 300)

        separator = Separator(self, orient='vertical')
        separator.pack(side='left', pady=3, padx=3, fill=Y)

        find_button = Button(self, image=self.find_icon)  # , command=.about)
        find_button.pack(side="left", anchor=N, padx=2, pady=2)
        Hovertip(find_button, "Search Messages...", 300)

        separator = Separator(self, orient='vertical')
        separator.pack(side='left', pady=3, padx=3, fill=Y)

        about_button = Button(self, image=self.about_icon, command=self.about)
        about_button.pack(side="left", anchor=N, padx=2, pady=2)
        Hovertip(about_button, "About this Application...", 300)

        # Set the message button states
        self.set_message_buttons_state(False)

    def about(self):
        # type: () -> None
        """This method displays an 'About' dialogue;

        :return: None
        """
        About(self.parent)

    def delete_message(self):
        # type: () -> None
        """This method deletes a message displayed and selected in the main application window tree view list
        widget.

        :return: None
        """
        # Delete a file, display a confirmation dialogue
        answer = askyesno("Delete Message Confirmation",
                          "Are you sure you want to delete the Message:" + os.linesep
                          + self.selected_path, parent=self)
        if answer:
            # Delete the node from the tree
            self.tree_view.delete(self.tree_view.selection()[0])

    def display_ers(self):
        # type: () -> None
        """Display the ERS for a message displayed and selected in the main application window tree view list
        widget.

        :return: None
        """
        ErsListFrame(self, self.selected_path)

    def open_message(self):
        # Open the message editor with the selected message
        """Open a message displayed and selected in the main application window tree view list widget.

        :return: None
        """
        rx = ReadXml(self.selected_path)
        if rx.is_message_ok():
            mte = MessageTextEditorFrame(self, False, MessageTitles.UNKNOWN,
                                         rx.get_creation_time(), rx.get_modification_time(), "")
            mte.set_message(self.selected_path)

    def open_new_message(self):
        # type: () -> None
        """Create a new message by opening the message editor; a default temple for an FPL message is displayed;

        :return: None
        """
        MessageTextEditorFrame(self.parent, True, MessageTitles.FPL, "", "", self.working_directory_path)

    def set_message_buttons_state(self, state):
        # type (bool) -> None
        """This method sets the enabled/disabled state of the buttons dealing with messages; if a message
        is selected in the message display list, the button are enabled, otherwise they are disabled.
        The button enabled/disabled are:

            - Open currently selected document
            - Delete currently selected document
            - Display ERS
            - Print currently selected message

        :param state: True to enable the buttons, False to disable the buttons;
        :return: None
        """
        if state:
            self.open_doc_button['state'] = NORMAL
            self.delete_doc_button['state'] = NORMAL
            self.ers_button['state'] = NORMAL
            self.print_button['state'] = NORMAL
        else:
            self.open_doc_button['state'] = DISABLED
            self.delete_doc_button['state'] = DISABLED
            self.ers_button['state'] = DISABLED
            self.print_button['state'] = DISABLED

    def set_selected_path(self, selected_path):
        # type: (str) -> None
        """Sets the absolute path and filename for a file containing a message selected in the message
        list or tre view. This method also enables / disables the toolbar button based on the
        path validity, if a selected message exists then button are enabled.

        :param selected_path: The absolute path of a file containing the currently selected message;
        :return: None
        """
        self.selected_path = selected_path
        if os.path.exists(self.selected_path):
            self.set_message_buttons_state(True)
        else:
            self.set_message_buttons_state(False)

    def set_tree_view(self, tree_view):
        # type(Treeview) -> None
        """Set a tree view that is the message list displayed in the main application window;

        :param tree_view: Handle to the tree view list widget displayed in the main application window;
        :return: None
        """
        self.tree_view = tree_view
