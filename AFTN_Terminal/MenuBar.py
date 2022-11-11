from tkinter import Tk, Menu, Toplevel, Button, Label, LEFT, NORMAL, DISABLED

from AFTN_Terminal.ReadXml import ReadXml
from Configuration.EnumerationConstants import MessageTitles
from AFTN_Terminal.MessageTextEditorFrame import MessageTextEditorFrame


class MenuBar(Menu):

    parent: Tk = None
    file_menu: Menu = None
    selected_path: str = ""
    app_root_message_path: str = ""

    def __init__(self, parent, app_root_message_path):
        # type: (Tk, str) -> None

        # Get a handle to the root window menu bar
        super().__init__(parent)

        self.parent = parent
        self.app_root_message_path = app_root_message_path

        # Create and add the file menu
        self.file_menu = Menu(self, tearoff=0)
        self.file_menu.add_cascade(label="New Message...", menu=self.create_new_submenu())
        self.file_menu.add_command(label="Open Selected Message...", command=self.open_message_text_editor)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.parent.destroy)
        self.add_cascade(label="Message", menu=self.file_menu)

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
        MessageTextEditorFrame(self.parent, True, message_title, "", "", self.app_root_message_path)

    def new_message_text_editor_ach(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.ACH)

    def new_message_text_editor_acp(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.ACP)

    def new_message_text_editor_afp(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.AFP)

    def new_message_text_editor_alr(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.ALR)

    def new_message_text_editor_apl(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.APL)

    def new_message_text_editor_arr(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.ARR)

    def new_message_text_editor_cdn(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.CDN)

    def new_message_text_editor_chg(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.CHG)

    def new_message_text_editor_cnl(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.CNL)

    def new_message_text_editor_cpl(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.CPL)

    def new_message_text_editor_dep(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.DEP)

    def new_message_text_editor_dla(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.DLA)

    def new_message_text_editor_est(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.EST)

    def new_message_text_editor_fpl(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.FPL)

    def new_message_text_editor_fnm(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.FNM)

    def new_message_text_editor_mfs(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.MFS)

    def new_message_text_editor_rcf(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.RCF)

    def new_message_text_editor_rqp(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.RQP)

    def new_message_text_editor_rqs(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.RQS)

    def new_message_text_editor_spl(self):
        # type: () -> None
        self.new_message_text_editor(MessageTitles.SPL)

    def do_nothing(self):
        top_level = Toplevel(self.parent)
        button = Button(top_level, text="Do nothing button")
        button.pack()

    def set_selected_path(self, selected_path):
        # type: (str) -> None
        self.selected_path = selected_path

    def open_message_text_editor(self):
        # type: () -> None
        rx = ReadXml(self.selected_path)
        if rx.is_message_ok():
            mtep = MessageTextEditorFrame(self.parent, False, MessageTitles.UNKNOWN,
                                          rx.get_creation_time(), rx.get_modification_time(), "")
            mtep.set_message(self.selected_path)

    def about(self):
        # type: () -> None
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
        if state:
            self.file_menu.entryconfig(1, state=NORMAL)
        else:
            self.file_menu.entryconfig(1, state=DISABLED)
