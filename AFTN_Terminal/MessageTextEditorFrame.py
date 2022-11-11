from datetime import datetime
from tkinter import Tk, N, S, W, E, Toplevel, Frame, Button, DISABLED, Label, Y
from tkinter.ttk import Treeview, Separator

from AFTN_Terminal.MessageDisplayFrame import MessageDisplayFrame
from Configuration.EnumerationConstants import MessageTitles


class MessageTextEditorFrame(MessageDisplayFrame):
    is_new: bool = False

    def __init__(self, parent, is_new, message_title, creation_date, modification_date, app_root_message_path):
        # type: (Tk | Treeview, bool, MessageTitles, str, str, str) -> None

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
    message_text_editor_frame: MessageTextEditorFrame = None
    save_button = None
    apply_button = None

    def __init__(self, parent, message_text_editor_frame):
        # type: (Toplevel, MessageTextEditorFrame) -> None
        super().__init__(parent)

        self.message_text_editor_frame = message_text_editor_frame

        # Add the buttons
        cancel_button = Button(self, text="Close", command=parent.destroy)
        cancel_button.pack(side="right", anchor="ne", pady=3, padx=3)

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

    def __init__(self, parent, creation_date, modification_date):
        # type: (Toplevel, str, str) -> None
        super().__init__(parent, borderwidth=2, relief="groove")

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
