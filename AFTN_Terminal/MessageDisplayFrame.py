import os
import re
from tkinter import N, S, W, E, END, BOTTOM, RIGHT, Text, LEFT, BOTH, SINGLE, X, Y, NORMAL, DISABLED
from tkinter import Listbox, Scrollbar, LabelFrame, Frame, PanedWindow, Event, Button, Toplevel
from tkinter.ttk import Style

from AFTN_Terminal.ReadXml import ReadXml
from AFTN_Terminal.WriteXml import WriteXml
from Configuration.EnumerationConstants import MessageTitles, MessageTypes, AdjacentUnits
from Configuration.FieldsInMessage import FieldsInMessage
from IcaoMessageParser.FlightPlanRecord import FlightPlanRecord
from IcaoMessageParser.ParseMessage import ParseMessage


class MessageDisplayFrame(Frame):
    """This class builds the message display area along with its associated error list as well as
    providing functionality to display a message and any associated errors and highlighting erroneous
    items in a displayed message. This frame is subclassed in the message text editor that has additional
    buttons to validate, apply changes and save new messages; these buttons are bound to
    methods in this class.
    """
    message_text_frame = None
    """Stores an instance of the MessageTextFrame used to display a message, (also implemented
    in this file)."""

    error_message_frame = None
    """Stores an instance of the ErrorMessageFrame used to display errors associated with a message,
    (also implemented in this file)."""

    xml_message_file_path: str = ""
    """The absolute path to an XML file containing an ATS message. This path is different to
    the 'message_path' member in so far it is used by the text editor to apply and save messages
    rather than being derived from a selected message."""

    fpr: FlightPlanRecord = None
    """An instance of a flight plan record"""

    is_new: bool = False
    """A flag indicating if the message being displayed is being created, (new, True) or a read only
    message display, (False)"""

    message_path: str = ""
    """The absolute path to an XML file containing an ATS message. This path is different to
    the 'xml_message_file_path' member in so far it is the path derived from a message selected
    in either the tree view or the message list."""

    def __init__(self, parent, enabled, is_new, message_title):
        # type: (Toplevel | PanedWindow, bool, bool, MessageTitles) -> None
        """This constructor builds a Frame containing two frames (MessageTextFrame & ErrorMessageFrame)
        to display a message and any associated error messages.
        The MessageTextFrame contains a text widget to display the message and a list widget to display
        any associated errors.

        If the text editor is opened to create a new message, the message title parameter is used
        to determine the which message template to display.

        :param parent: Handle to the parent window; will be either the main applications paned window or
               a MessageTextEditorFrame used to create a new message or edit an existing message.
        :param enabled: Indicates if the message text widget is enabled or not; when this class is
               used to display a message in the main application window, it cannot be edited, (False).
               When used in a MessageTextEditorFrame the message is editable, (True).
        :param is_new: Indicates if the MessageTextEditorFrame is opened on an existing message (False)
               or a new message is being created (True).
        :param message_title: An enumeration of the MessageTitles class containing the message title
               of a message when the message editor is opened to create a 'new' message;
        """
        super().__init__(parent)

        self.is_new = is_new

        # Set up a single column, two row grid on the parent
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=8)
        self.rowconfigure(1, weight=1)

        # Add row 0, an instance of MessageTextFrame at the top row of the grid
        self.message_text_frame = MessageTextFrame(self, message_title)  # MessageTitles.UNKNOWN)
        self.message_text_frame.grid(column=0, row=0, sticky=N + E + W + S)
        self.message_text_frame.enable_text_editor(enabled)

        # Add row 1, the error message frame at the bottom of 'this' frame
        self.error_message_frame = ErrorMessageFrame(self)
        self.error_message_frame.grid(column=0, row=1, sticky=N + E + W + S)

        # Set the message template if this editor is opened as a 'new' message
        if self.is_new:
            self.set_template(message_title)

    def set_template(self, message_title):
        # type: (MessageTitles) -> None
        """This class displays a simple template when a new message is created. The template is specific
        for a message based on its title passed into this method as a parameter.

        :param message_title: An enumeration of the MessageTitles class containing the message title
               of a message when the message editor is opened to create a 'new' message;
        :return: None
        """
        # Get the field list for the message title, contains a list of ICAO fields for a given title
        fim = FieldsInMessage()
        md = fim.get_message_content(MessageTypes.ATS, AdjacentUnits.DEFAULT, message_title)

        # Build the template string
        template_string = "PRIORITY_INDICATOR ADDRESS: 1 or more" + os.linesep + \
                          "FILING_TIME ORIGINATOR" + os.linesep + \
                          "ADADDRESS: zero or more, if zero delete line" + os.linesep + \
                          "("
        for field_id in md.get_message_fields():
            if message_title == MessageTitles.ALR and re.fullmatch("F7|F9|F13|F15|F16|F18|F19|F20", field_id.name):
                template_string = template_string + os.linesep + "-" + field_id.name
            elif (message_title == MessageTitles.CPL or message_title == MessageTitles.FPL) and \
                    re.fullmatch("F9|F13|F15|F16|F18", field_id.name):
                template_string = template_string + os.linesep + "-" + field_id.name
            elif message_title == MessageTitles.SPL and re.fullmatch("F16|F18|F19", field_id.name):
                template_string = template_string + os.linesep + "-" + field_id.name
            elif re.fullmatch("F3", field_id.name):
                template_string = template_string + message_title.name
            else:
                template_string = template_string + "-" + field_id.name
        template_string = template_string + ")"

        # Display the template
        self.message_text_frame.set_text(template_string)

    def set_message_path(self, message_path):
        # type: (str) -> None
        """This method sets the absolute path to an XML file containing an ATS message. This path
        differs from the 'xml_message_file_path' member in so far it is the path derived from 
        a message selected in either the tree view or the message list.
        
        :param message_path: The absolute path to a file containing a message that was selected
               in the list of messages or the tre view;
        :return: None
        """
        self.message_path = message_path

    def set_message(self, xml_message_file_path):
        # type: (str) -> None
        """This method sets the absolute path to an XML file containing an ATS message. This path
        differs from the 'message_path' member in so far it is used by the text editor to apply
        and save messages rather than being derived from a selected message.

        :param xml_message_file_path: The absolute path to a file containing a message resulting
               from applying a change or saving a new message;
        :return: None
        """
        self.xml_message_file_path = xml_message_file_path

        # Sets a message into the editor and if errors are present, lists the errors in the error frame
        if len(xml_message_file_path) == 0:
            # Nothing to open, clear the message display
            self.clear_text_and_errors()
            return

        # Read the XML file and display it
        rx = ReadXml(xml_message_file_path)
        # Check if the message was successfully read...
        if not rx.is_message_ok():
            self.clear_text_and_errors()
            return

        # Set the message text into the text widget to display the selected message
        self.message_text_frame.set_text(rx.get_original_message())
        # Set any associated errors in the message error frame
        self.error_message_frame.set_errors(rx.get_all_errors())

    def clear_text_and_errors(self):
        # type: () -> None
        """This method clears the text widget and the error list.

        :return: None
        """
        # Clear down the text and error list
        self.message_text_frame.set_text("")
        self.error_message_frame.set_errors([])

    def highlight_text(self, start_index, end_index):
        # type: (int, int) -> None
        """This method highlights text in the text editor text widget; the range of text highlighted
        is specified bt the start and end index parameters.

        :param start_index: A zero based index to the first character that will be highlighted;
        :param end_index: A zero based index to the last character + 1 that will be highlighted;
        :return: None
        """
        self.message_text_frame.highlight_text(start_index, end_index)

    def apply_message(self):
        # type: () -> None
        """This method saves a modified message to the same XML file that the message was extracted
        from.

        :return: None
        """
        write_xml = WriteXml()
        write_xml.update_existing_message(self.xml_message_file_path, self.fpr.as_xml())

    def save_message(self):
        # type: () -> None
        """This method saves a new message to a new XML file.

        :return: None
        """
        write_xml = WriteXml()
        write_xml.write_new_message(self.fpr.as_xml(), self.message_path)

    def validate_message(self, apply_button, save_button):
        # type: (Button, Button) -> None
        """This method validates a message by parsing a message displayed in the message text editor.
        The 'Validate' and 'Save' buttons are enabled/disabled such that a message with errors
        cannot be saved.

        :param apply_button: Handle to the 'Apply' button;
        :param save_button: Handle to the 'Save' button;
        :return: None
        """
        # Parse the message displayed in the editor
        self.fpr = FlightPlanRecord()
        pm = ParseMessage()
        pm.parse_message(self.fpr, self.message_text_frame.get_text())

        # Set any associated errors in the message display error frame
        self.error_message_frame.set_errors(self.fpr.get_all_errors())

        # Enable / disable the Save or Apply buttons
        # Can only save or apply a change if no errors exist
        if len(self.fpr.get_all_errors()) > 0:
            if save_button is not None:
                save_button.config(state=DISABLED)
            if apply_button is not None:
                apply_button.config(state=DISABLED)
        else:
            if save_button is not None:
                save_button.config(state=NORMAL)
            if apply_button is not None:
                apply_button.config(state=NORMAL)


class ErrorMessageFrame(LabelFrame):
    """This class builds a frame containing the list widget that displays errors associated with
    a message currently displayed in the MessageDisplayFrame. The class contains a method to
    populate the list with errors and a callback for double-clicking a list entry causing the
    erroneous field to be highlighted in the MessageDisplayFrame.

    """
    error_list_box = None
    """Handle to the list box widget that displays message errors"""

    errors = None
    """A list of errors, each entry is itself a list with index 0 = the error message,
    index 1 = the zero based index of the first character of an erroneous field and
    index 2 = the zero based index of the last character + 1 of an erroneous field."""

    parent = None
    """Handle to the parent window; will be the MessageDisplayFrame"""

    def __init__(self, parent):
        # type: (any) -> None
        """This constructor builds a frame containing the list widget that displays errors
        associated with a message currently displayed in the MessageDisplayFrame.

        :param parent: Handle to the parent window; will be the MessageDisplayFrame
        """
        # Create the error message frame
        super().__init__(parent, text="Error Messages for Selected Message",
                         font=("Arial", 11), padx=5, pady=5)
        # Store the handle to the parent window
        self.parent = parent

        # Add the scroll bars to the error message frame
        error_vertical = Scrollbar(self, orient='vertical')
        error_vertical.pack(side=RIGHT, fill=Y)
        error_horizontal = Scrollbar(self, orient='horizontal')
        error_horizontal.pack(side=BOTTOM, fill=X)

        # Add the list box to display any errors to the error message frame
        self.error_list_box = Listbox(self,
                                      yscrollcommand=error_vertical.set,
                                      xscrollcommand=error_horizontal.set, height=5, font=("Arial", 11))
        self.error_list_box.selectmode = SINGLE
        self.error_list_box.bind('<Double-1>', self.on_double_click)
        error_vertical.config(command=self.error_list_box.yview)
        error_horizontal.config(command=self.error_list_box.xview)
        self.error_list_box.pack(side=LEFT, fill=BOTH, expand=1)

    def on_double_click(self, event):
        # type: (Event) -> None
        """This is a callback method bound to the list box widget invoked by a double click
        on an error list entry.

        :param event: Unused by this callback;
        :return: None
        """
        current_selection = self.error_list_box.curselection()[0]
        self.parent.highlight_text(self.errors[current_selection][1], self.errors[current_selection][2])

    def set_errors(self, errors):
        # type: ([[str, int, int]]) -> None
        """This method stores a list of errors passed to it in the 'errors' parameter and displays
        the errors in the list box widget displayed by MessageDisplayFrame.

        :param errors: A list of errors, each entry is itself a list with index 0 = the error message,
               index 1 = the zero based index of the first character of an erroneous field and
               index 2 = the zero based index of the last character + 1 of an erroneous field.
        :return: None
        """
        self.errors = errors
        self.error_list_box.delete(0, END)
        if self.errors is None:
            return
        for error in errors:
            self.error_list_box.insert(END, error[0])


class MessageTextFrame(LabelFrame):
    """This class builds the message text frame; the frame contains a text widget in which messages
    are displayed. The frame text is set dependent on the message title passed into the constructor.

    """
    text: Text = None
    """The text widget to display a message in"""

    message_title: MessageTitles = MessageTitles.UNKNOWN
    """A MessageTitles enumeration value; this is used to determine a message template 
    when using the MessageTextFrame for creating a message."""

    def __init__(self, parent, message_title):
        # type: (Frame, MessageTitles) -> None
        """This constructor builds the message text frame; the frame contains a text widget in which messages
        are displayed.

        :param parent: Handle to the parent window; this will be an instance of MessageDisplayFrame in which
               this MessageTextFrame is displayed;
        :param message_title: A MessageTitles enumeration value; this is used to determine a message template
               when using the MessageTextFrame for creating a message.
        """
        # Set the frame text/title based on the usage; if a new message is created the
        # message title is included in the text
        if message_title == MessageTitles.UNKNOWN:
            title = "ATS Message Content for Selected Message"
        else:
            title = "Create new " + message_title.name + " ATS Message"

        # Call the super;
        super().__init__(parent, text=title, font=("Arial", 11), padx=5, pady=5)

        # Save the message title to this class
        self.message_title = message_title

        # Add vertical and horizontal Scrollbars to 'this' frame
        vertical = Scrollbar(self, orient='vertical')
        vertical.pack(side=RIGHT, fill=Y)
        horizontal = Scrollbar(self, orient='horizontal')
        horizontal.pack(side=BOTTOM, fill=X)

        # Create a text widget
        self.text = Text(self, font=("Courier", 12), wrap='none',
                         yscrollcommand=vertical.set,
                         xscrollcommand=horizontal.set)

        # Get the Tkinter default selection color
        style = Style()
        def_color = style.map('Treeview')['background'][1][1]
        self.text.tag_configure("highlight", background=def_color, foreground="white")
        self.text.bind("<ButtonRelease-1>", self.clear_highlight)
        self.text.config(spacing1=4)

        # Attach the scrollbar with the text widget to 'this' frame
        vertical.config(command=self.text.yview)
        horizontal.config(command=self.text.xview)
        self.text.pack(expand=True, fill=BOTH)

    def display_message_template(self):
        # type: () -> None
        """This method displays a template for a message being created; the template displayed is
        determined using the enumeration value passed into this classes constructor as an enumeration
        value from the MessageTitles class.

        :return: None
        """
        fim = FieldsInMessage()
        md = fim.get_message_content(MessageTypes.ATS, AdjacentUnits.DEFAULT, self.message_title)
        if md is not None:
            self.configure(text=md.get_message_title() + " - " + md.get_message_description())
            template = ""
            for field_id in md.get_message_fields():
                template = template + field_id.name + "-"
            template = template.rstrip("-")
            self.text.insert(0.0, "Message Template...\n(" + template + ")")

    def enable_text_editor(self, enabled):
        # type: (bool) -> None
        """This method enables or disables the text editor; The text widget is disabled when displaying
        a message in the main window and enabled when a message is displayed in an editor dialogue.

        :param enabled: If True, the text widget is enabled and can be edited; If false the text widget
               is disabled and inhibits editing.
        :return: None
        """
        if enabled:
            self.text.config(state=NORMAL)
        else:
            self.text.config(state=DISABLED)

    def set_text(self, text):
        # type: (str) -> None
        """This method sets the message text in the text widget; if the text widget is disabled,
        (which can happen if the text widget is displayed in the main window) the window state
        is set to enabled, the text written, then the state is set back to disable.

        :param text: The text to set;
        :return: None
        """
        if re.fullmatch('normal', self.text['state']):
            self.text.delete(0.0, END)
            self.text.insert(0.0, text)
        else:
            self.enable_text_editor(True)
            self.text.delete(0.0, END)
            self.text.insert(0.0, text)
            self.enable_text_editor(False)

    def get_text(self):
        # type: () -> str
        """This method gets the text from the text widget;

        :return: The text string in the text widget;
        """
        return self.text.get(1.0, END)

    def highlight_text(self, start_index, end_index):
        # type: (int, int) -> None
        """This method highlights text in the text widget;

        :param start_index: A zero based index to the first character to be highlighted in the text widget;
        :param end_index: A zero based index to the last character + 1 to be highlighted in the text widget;
        :return: None
        """
        self.text.tag_add("highlight",
                          self.get_row_column_index(start_index),
                          self.get_row_column_index(end_index))

    @staticmethod
    def clear_highlight(event):
        # type: (Event) -> None
        """This method removes all highlighted text from the text widget;

        :param event: The event containing the text widget handle of the text widget for the text
               highlighted to be cleared;
        :return: None
        """
        event.widget.tag_remove("highlight", 0.0, END)

    def get_row_column_index(self, index):
        # type: (int) -> str
        """This method determines the row number that text highlighting will be set on.
        The text highlighting in these text widgets works on a row column method rather than an absolute
        zero base index. This method return a string that contains a row and column where the index 'points'
        to, e.g. the return is 3.12, implying the highlight index is row 3, column 12.

        :param index: A zero based index of a character in the string displayed in the text widget;
        :return: A string that contains a row and column where the index 'points' to, e.g. the return
        is 3.12, implying the highlight index is row 3, column 12.
        """
        row_number: int = 1
        number_characters = 0
        last_number_of_characters = 0
        for line in self.text.get(0.0, END).splitlines():
            number_characters = number_characters + len(line) + len(os.linesep)
            if index <= number_characters:
                break
            last_number_of_characters = number_characters
            row_number += 1
        column: float = index - last_number_of_characters
        return str(row_number) + "." + str(column)
