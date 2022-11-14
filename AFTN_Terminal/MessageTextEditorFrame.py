from datetime import datetime
from tkinter import Tk, N, S, W, E, Toplevel, Frame, Button, DISABLED, Label, Y
from tkinter.ttk import Treeview, Separator

from AFTN_Terminal.MessageDisplayFrame import MessageDisplayFrame
from Configuration.EnumerationConstants import MessageTitles


class MessageTextEditorFrame(MessageDisplayFrame):
    """This class displays a message text editor with the text editor and error messages provided
    by the base class MessageDisplayFrame; this class adds a status and button bar that displays
    either a 'Apply' or 'Save' button depending on if an existing message is being edited or
    a new message is being created."""

    is_new: bool = False
    """A flag indicating if this editor is being opened to create a new message, (True) or 
    an existing message (False)."""

    def __init__(self, parent, is_new, message_title, creation_date, modification_date, app_root_message_path):
        # type: (Tk | Treeview, bool, MessageTitles, str, str, str) -> None
        """This constructor builds a message text editor with the text editor and error messages provided
        by the base class MessageDisplayFrame; this constructor adds a status and button bar that displays
        either a 'Apply' or 'Save' button depending on if an existing message is being edited or
        a new message is being created.

        :param parent: Handle to a parent window, this will be the tree view in the main application window
               if a message is being opened via double-click on a tree view leaf/file, or the parent window
               if opened from the message list.
        :param is_new: True if this message text editor is being opened to create a new message, False
               if an existing message is being edited;
        :param message_title: An enumeration value from the MessageTitles class used to determined the message
               template when anew message is created.
        :param creation_date: The creation timestamp of the XML file for the message being edited, or the
               current date and time if a new message is being created;
        :param modification_date: The modification timestamp of the XML file for the message being edited,
               or the current date and time if a new message is being created;
        :param app_root_message_path: The full absolute working directory path; used to store new messages
               in the Outbox;
        """
        # Get a handle to the top level widget
        top_level = Toplevel(parent)

        # Construct a frame for this instance
        super().__init__(top_level, True, is_new, message_title)

        self.is_new = is_new
        self.set_message_path(app_root_message_path)

        # Set the dialogue title
        if self.is_new:
            top_level.title(message_title.name + ' Plain Text Message Editor')
        else:
            top_level.title('Plain Text Message Editor')

        # Set up a single column, two row grid on the parent
        top_level.columnconfigure(0, weight=1)
        top_level.rowconfigure(0, weight=1)
        top_level.rowconfigure(1, weight=0)
        top_level.rowconfigure(2, weight=0)

        # Add 'this' instance to the top row of the grid
        self.grid(column=0, row=0, sticky=N + E + W + S)

        # Add the status bar
        message_status_bar = MessageStatusBar(top_level, creation_date, modification_date)
        message_status_bar.grid(column=0, row=1, sticky=N + E + W + S)

        # Add the frame containing the buttons (OK, Check and Cancel) to the third row of the grid
        button_frame = ButtonFrame(top_level, self)
        button_frame.grid(column=0, row=2, sticky=N + E + W + S)


class ButtonFrame(Frame):
    """This class builds a frame containing the following buttons:

        - 'Close'
        - 'Save' or 'Apply': (depends on if a new or existing message is being created/edited)
        - 'Validate'
    """
    message_text_editor_frame: MessageTextEditorFrame = None
    """Handle to a the MessageTextEditorFrame that this button frame is displayed in;"""

    save_button = None
    """Handle to the 'Save' button, this is needed so it can be enabled/disabled based on the 
    the type of message being edited, new or existing. The 'Save' button is enabled when a new
    message is being edited."""

    apply_button = None
    """Handle to the 'Apply' button, this is needed so it can be enabled/disabled based on the 
    the type of message being edited, new or existing. The 'Apply' button is enabled when an
    existing message is being edited."""

    def __init__(self, parent, message_text_editor_frame):
        # type: (Toplevel, MessageTextEditorFrame) -> None
        """This constructor builds a frame containing four buttons, 'Close', 'Save' or 'Apply' and 'Validate';

        :param parent: Handle to the parent window, will the top level of the MessageTextEditorFrame;
        :param message_text_editor_frame: Handle to an instance of MessageTextEditorFrame;
        """
        super().__init__(parent)

        # Save the handle to the MessageTextEditorFrame
        self.message_text_editor_frame = message_text_editor_frame

        # Add the buttons
        close_button = Button(self, text="Close", command=parent.destroy)
        close_button.pack(side="right", anchor="ne", pady=3, padx=3)

        # The 'Save' button is added if a new message is being created
        if self.message_text_editor_frame.is_new:
            self.save_button = Button(self, text="Save", state=DISABLED,
                                      command=self.message_text_editor_frame.save_message)
            self.save_button.pack(side="right", pady=3, padx=3)
        else:
            self.apply_button = Button(self, text="Apply Changes", state=DISABLED,
                                       command=self.message_text_editor_frame.apply_message)
            self.apply_button.pack(side="right", pady=3, padx=3)

        validate_button = Button(self, text="Validate Message",
                                 command=lambda: self.message_text_editor_frame.validate_message(
                                     self.apply_button, self.save_button))
        validate_button.pack(side="right", pady=3, padx=3)


class MessageStatusBar(Frame):
    """This class builds a frame containing label widgets to display some status information
    about the message being created/edited."""

    def __init__(self, parent, creation_date, modification_date):
        # type: (Toplevel, str, str) -> None
        """This constructor builds a frame containing label widgets to display some status information
        about the message being created/edited.

        :param parent: The top level window handle;
        :param creation_date: The creation timestamp of the XML file for the message being edited, or the
               current date and time if a new message is being created;
        :param modification_date: The modification timestamp of the XML file for the message being edited,
               or the current date and time if a new message is being created;
        """
        super().__init__(parent, borderwidth=2, relief="groove")

        # Create the date/time format strings
        if len(creation_date) == 0:
            creation_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            creation_dt = creation_date

        if len(modification_date) == 0:
            modification_dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            modification_dt = modification_date

        # Add the labels
        creation_date_value = Label(self, text=creation_dt)
        creation_date_value.pack(side="right", anchor="ne", pady=3, padx=3)

        creation_date_label = Label(self, text="Message Created on:")
        creation_date_label.pack(side="right", anchor="ne", pady=3, padx=3)

        # Add a seperator
        separator = Separator(self, orient='vertical')
        separator.pack(side="right", pady=3, padx=3, fill=Y)

        modification_date_value = Label(self, text=modification_dt)
        modification_date_value.pack(side="right", anchor="ne", pady=3, padx=3)

        modification_date_label = Label(self, text="Message Last Modified on:")
        modification_date_label.pack(side="right", anchor="ne", pady=3, padx=3)

        # Add a seperator
        separator = Separator(self, orient='vertical')
        separator.pack(side="right", pady=3, padx=3, fill=Y)
