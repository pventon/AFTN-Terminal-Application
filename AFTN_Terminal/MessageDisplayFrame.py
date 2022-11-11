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
    message_text_frame = None
    error_message_frame = None
    xml_message_file_path = ""
    fpr = None
    is_new: bool = False
    message_path: str = ""

    def __init__(self, parent, enabled, is_new, message_title):
        # type: (Toplevel | PanedWindow, bool, bool, MessageTitles) -> None
        super().__init__(parent)

        self.is_new = is_new

        # Set up a single column, two row grid on the parent
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=8)
        self.rowconfigure(1, weight=1)

        # Add row 0...
        # Add 'this' instance to the top row of the grid
        self.message_text_frame = MessageTextFrame(self, message_title)  # MessageTitles.UNKNOWN)
        self.message_text_frame.grid(column=0, row=0, sticky=N + E + W + S)
        self.message_text_frame.enable_text_editor(enabled)

        # Add row 1...
        # Add the error message frame
        self.error_message_frame = ErrorMessageFrame(self)
        self.error_message_frame.grid(column=0, row=1, sticky=N + E + W + S)

        # Set the message template if this editor is opened as a 'new' message
        if self.is_new:
            self.set_template(message_title)

    def set_template(self, message_title):
        # type: (MessageTitles) -> None
        # Get the field list for the message title
        fim = FieldsInMessage()
        md = fim.get_message_content(MessageTypes.ATS, AdjacentUnits.DEFAULT, message_title)
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
        self.message_text_frame.set_text(template_string)

    def set_message_path(self, message_path):
        self.message_path = message_path

    def set_message(self, xml_message_file_path):
        # type: (str) -> None
        self.xml_message_file_path = xml_message_file_path

        # Sets a message into the editor and if errors are present, lists the errors in the error frame
        if len(xml_message_file_path) == 0:
            # Nothing to open, clear the message display
            self.clear_text_and_errors()
            return

        # Read the XML file and display it
        rx = ReadXml(xml_message_file_path)
        # Check it the message was successfully read...
        if not rx.is_message_ok():
            self.clear_text_and_errors()
            return

        # Set the message text into the text widget to display the selected message
        self.message_text_frame.set_text(rx.get_original_message())
        # Set any associated errors in the display message and error frame
        self.error_message_frame.set_errors(rx.get_all_errors())

    def clear_text_and_errors(self):
        # type: () -> None
        # Clear down the text and error list
        self.message_text_frame.set_text("")
        self.error_message_frame.set_errors([])

    def highlight_text(self, start_index, end_index):
        # type: (int, int) -> None
        self.message_text_frame.highlight_text(start_index, end_index)

    def apply_message(self):
        write_xml = WriteXml()
        write_xml.update_existing_message(self.xml_message_file_path, self.fpr.as_xml())

    def save_message(self):
        write_xml = WriteXml()
        write_xml.write_new_message(self.fpr.as_xml(), self.message_path)

    def validate_message(self, apply_button, save_button):
        # type: (Button, Button) -> None

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
    error_list_box = None
    errors = None
    parent = None

    def __init__(self, parent):
        # type: (any) -> None
        # Create the error message frame
        super().__init__(parent, text="Error Messages for Selected Message",
                         font=("Arial", 11), padx=5, pady=5)
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
        current_selection = self.error_list_box.curselection()[0]

        print(self.errors[current_selection][0],
              self.errors[current_selection][1],
              self.errors[current_selection][2])

        self.parent.highlight_text(self.errors[current_selection][1], self.errors[current_selection][2])

    def set_errors(self, errors):
        # type: ([[str, int, int]]) -> None
        self.errors = errors
        self.error_list_box.delete(0, END)
        if self.errors is None:
            return
        for error in errors:
            self.error_list_box.insert(END, error[0])


class MessageTextFrame(LabelFrame):
    text: Text = None
    message_title: MessageTitles = MessageTitles.UNKNOWN

    def __init__(self, parent, message_title):
        # type: (Frame, MessageTitles) -> None
        if message_title == MessageTitles.UNKNOWN:
            title = "ATS Message Content for Selected Message"
        else:
            title = "Create new " + message_title.name + " ATS Message"
        super().__init__(parent, text=title, font=("Arial", 11), padx=5, pady=5)
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
        if enabled:
            self.text.config(state=NORMAL)
        else:
            self.text.config(state=DISABLED)

    def set_text(self, text):
        # type: (str) -> None
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
        return self.text.get(1.0, END)

    def highlight_text(self, start_index, end_index):
        # type: (int, int) -> None
        print("Text highlight at (start,end): (" + str(start_index) + "," + str(end_index) + ")")
        self.text.tag_add("highlight",
                          self.get_row_column_index(start_index),
                          self.get_row_column_index(end_index))
        # for line in self.text.get(0.0, END).splitlines():
        #    print("Length: " + str(len(line)))

    def clear_highlight(self, event):
        # type: (Event) -> None
        self.text.tag_remove("highlight", 0.0, END)

    def get_row_column_index(self, index):
        # type: (int) -> str
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
