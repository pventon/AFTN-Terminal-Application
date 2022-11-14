from tkinter import Tk, Menu, Toplevel, Button, Label, LEFT, NORMAL, DISABLED

from AFTN_Terminal.ReadXml import ReadXml
from Configuration.EnumerationConstants import MessageTitles
from AFTN_Terminal.MessageTextEditorFrame import MessageTextEditorFrame


class MenuBar(Menu):
    """This class builds the main application menu displayed below the main application window title bar."""

    parent: Tk = None
    """Handle to the parent window"""

    message_menu: Menu = None
    """Handle to the 'Message' menu"""

    selected_path: str = ""
    """The path to a file for a message selected in the message list window or the main
    application window tree view;"""

    working_directory_path: str = ""
    """The working directory used by this application to store messages in"""

    def __init__(self, parent, working_directory_path):
        # type: (Tk, str) -> None
        """This constructor builds the main application menu displayed below the main application window title bar.
        Event handlers are bound to the menu items.

        :param parent: Handle to the parent window;
        :param working_directory_path: The working directory used by this application to store messages in;
        """
        # Get a handle to the root window menu bar
        super().__init__(parent)

        self.parent = parent
        self.working_directory_path = working_directory_path

        # Create and add the file menu
        self.message_menu = Menu(self, tearoff=0)
        self.message_menu.add_cascade(label="New Message...", menu=self.create_new_submenu())
        self.message_menu.add_command(label="Open Selected Message...", command=self.open_message_text_editor)
        self.message_menu.add_separator()
        self.message_menu.add_command(label="Exit", command=self.parent.destroy)
        self.add_cascade(label="Message", menu=self.message_menu)

        # Create and add the edit menu
        edit_menu = Menu(self, tearoff=0)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: self.event_generate('<Control-z>'))
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=lambda: self.event_generate('<Control-x>'))
        edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=lambda: self.event_generate('<Control-c>'))
        edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=lambda: self.event_generate('<Control-v>'))
        edit_menu.add_command(label="Delete", command=self.do_nothing)
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A",
                              command=lambda: self.event_generate('<Control-a>'))
        self.add_cascade(label="Edit", menu=edit_menu)

        # Create and add the help menu
        help_menu = Menu(self, tearoff=0)
        help_menu.add_command(label="Help Index", command=self.do_nothing)
        help_menu.add_command(label="About...", command=self.about)
        self.add_cascade(label="Help", menu=help_menu)

        # Set the initial menu states
        self.set_open_message_menu_state(False)

        self.parent.config(menu=self)

    def create_new_submenu(self):
        # type: () -> Menu
        """This method builds the submenu for the 'New Message' menu item. There is a unique submenu
        item for each supported ATS message title. Bindings are set up to call a dedicated handler method
        to open a message editor window for a specific message title; the new message editor window
        is displayed with a template for a given message title that displays the field content for the
        message title.

        :return: A Menu containing as many submenu items as there are supported ATS messages;
        """
        # Creates the submenu for the 'New Message...' menu item, one for each supported message title
        sub_menu = Menu(self, tearoff=0)
        sub_menu.add_command(label="Message Title ACH...", command=self.new_message_text_editor_ach)
        sub_menu.add_command(label="Message Title ACP...", command=self.new_message_text_editor_acp)
        sub_menu.add_command(label="Message Title AFP...", command=self.new_message_text_editor_afp)
        sub_menu.add_command(label="Message Title ALR...", command=self.new_message_text_editor_alr)
        sub_menu.add_command(label="Message Title APL...", command=self.new_message_text_editor_apl)
        sub_menu.add_command(label="Message Title ARR...", command=self.new_message_text_editor_arr)
        sub_menu.add_command(label="Message Title CDN...", command=self.new_message_text_editor_cdn)
        sub_menu.add_command(label="Message Title CHG...", command=self.new_message_text_editor_chg)
        sub_menu.add_command(label="Message Title CNL...", command=self.new_message_text_editor_cnl)
        sub_menu.add_command(label="Message Title CPL...", command=self.new_message_text_editor_cpl)
        sub_menu.add_command(label="Message Title DEP...", command=self.new_message_text_editor_dep)
        sub_menu.add_command(label="Message Title DLA...", command=self.new_message_text_editor_dla)
        sub_menu.add_command(label="Message Title EST...", command=self.new_message_text_editor_est)
        sub_menu.add_command(label="Message Title FPL...", command=self.new_message_text_editor_fpl)
        sub_menu.add_command(label="Message Title FNM...", command=self.new_message_text_editor_fnm)
        sub_menu.add_command(label="Message Title MFS...", command=self.new_message_text_editor_mfs)
        sub_menu.add_command(label="Message Title RCF...", command=self.new_message_text_editor_rcf)
        sub_menu.add_command(label="Message Title RQP...", command=self.new_message_text_editor_rqp)
        sub_menu.add_command(label="Message Title RQS...", command=self.new_message_text_editor_rqs)
        sub_menu.add_command(label="Message Title SPL...", command=self.new_message_text_editor_spl)
        return sub_menu

    def new_message_text_editor(self, message_title):
        # type: (MessageTitles) -> None
        """This method is a generic helper method that opens the new message editor window passing
        the message title given in the parameter 'message_title'. The message title is used by the
        message editor window to determine which field list template to display in the message editor
        window.

        :param message_title: One of the supported ATS message titles as an enumeration value
               from the MessageTitles class;
        :return: None
        """
        MessageTextEditorFrame(self.parent, True, message_title, "", "", self.working_directory_path)

    def new_message_text_editor_ach(self):
        # type: () -> None
        """Helper method to open the new message editor window with the ACH message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.ACH)

    def new_message_text_editor_acp(self):
        # type: () -> None
        """Helper method to open the new message editor window with the ACP message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.ACP)

    def new_message_text_editor_afp(self):
        # type: () -> None
        """Helper method to open the new message editor window with the AFP message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.AFP)

    def new_message_text_editor_alr(self):
        # type: () -> None
        """Helper method to open the new message editor window with the ALR message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.ALR)

    def new_message_text_editor_apl(self):
        # type: () -> None
        """Helper method to open the new message editor window with the APL message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.APL)

    def new_message_text_editor_arr(self):
        # type: () -> None
        """Helper method to open the new message editor window with the ARR message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.ARR)

    def new_message_text_editor_cdn(self):
        # type: () -> None
        """Helper method to open the new message editor window with the CDN message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.CDN)

    def new_message_text_editor_chg(self):
        # type: () -> None
        """Helper method to open the new message editor window with the CHG message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.CHG)

    def new_message_text_editor_cnl(self):
        # type: () -> None
        """Helper method to open the new message editor window with the CNL message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.CNL)

    def new_message_text_editor_cpl(self):
        # type: () -> None
        """Helper method to open the new message editor window with the CPL message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.CPL)

    def new_message_text_editor_dep(self):
        # type: () -> None
        """Helper method to open the new message editor window with the DEP message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.DEP)

    def new_message_text_editor_dla(self):
        # type: () -> None
        """Helper method to open the new message editor window with the DLA message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.DLA)

    def new_message_text_editor_est(self):
        # type: () -> None
        """Helper method to open the new message editor window with the EST message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.EST)

    def new_message_text_editor_fpl(self):
        # type: () -> None
        """Helper method to open the new message editor window with the FPL message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.FPL)

    def new_message_text_editor_fnm(self):
        # type: () -> None
        """Helper method to open the new message editor window with the FNM message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.FNM)

    def new_message_text_editor_mfs(self):
        # type: () -> None
        """Helper method to open the new message editor window with the MFS message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.MFS)

    def new_message_text_editor_rcf(self):
        # type: () -> None
        """Helper method to open the new message editor window with the RCF message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.RCF)

    def new_message_text_editor_rqp(self):
        # type: () -> None
        """Helper method to open the new message editor window with the RQP message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.RQP)

    def new_message_text_editor_rqs(self):
        # type: () -> None
        """Helper method to open the new message editor window with the RQS message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.RQS)

    def new_message_text_editor_spl(self):
        # type: () -> None
        """Helper method to open the new message editor window with the SPL message title.

        :return: None
        """
        self.new_message_text_editor(MessageTitles.SPL)

    def set_selected_path(self, selected_path):
        # type: (str) -> None
        """Sets the absolute path and filename for a file containing a message selected in the message
        list or tre view.

        :param selected_path: The absolute path of a file containing the currently selected message;
        :return: None
        """
        self.selected_path = selected_path

    def do_nothing(self):
        # type: () -> None
        """Dummy method to set up menu item bindings where the specific function has not yet been implemented.
        This method will be deleted once all functions for all menu items are implemented.

        :return:
        """
        top_level = Toplevel(self.parent)
        button = Button(top_level, text="Do nothing button")
        button.pack()

    def open_message_text_editor(self):
        # type: () -> None
        """This method opens a message selected in the message list; when the message was selected the path to
        the file for the selected message is stored in the 'selected_path' member.

        :return: None
        """
        rx = ReadXml(self.selected_path)
        if rx.is_message_ok():
            mtep = MessageTextEditorFrame(self.parent, False, MessageTitles.UNKNOWN,
                                          rx.get_creation_time(), rx.get_modification_time(), "")
            mtep.set_message(self.selected_path)

    def about(self):
        # type: () -> None
        """This method displays an 'About' dialogue;

        :return: None
        """
        top_level = Toplevel(self.parent)
        label = Label(top_level, font="Arial, 11", justify=LEFT, padx=10, pady=10,
                      text="AFTN Terminal Application;\n"
                           "Version: 1.0\n"
                           "Release Date: December 2022\n"
                           "Author: Peter Venton\n"
                           "Software: Python 3.8.10\n"
                           "License: GPL")
        label.pack()

    def set_open_message_menu_state(self, state):
        # type: (bool) -> None
        """This method enables or disables the 'open selected message' menu item depending on whether a message
        is selected in the message display list. A selected message can only be opened if one is selected.

        :param state: The state to set the 'open selected message' menu item, True to enable, False to disable.
        :return: None
        """
        if state:
            self.message_menu.entryconfig(1, state=NORMAL)
        else:
            self.message_menu.entryconfig(1, state=DISABLED)
