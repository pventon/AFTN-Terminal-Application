import os.path
from tkinter.filedialog import askdirectory
from tkinter import Tk, N, E, W, S
from tkinter.messagebox import askyesno, showerror

from AFTN_Terminal.CentralPanedWindow import CentralPanedWindow
from AFTN_Terminal.ToolBar import ToolBar
from AFTN_Terminal.StatusBar import StatusBar
from AFTN_Terminal.MenuBar import MenuBar


class ApplicationMainWindow:

    root: Tk = None
    app_root_message_path = ""

    def __init__(self, app_root_message_path):
        # type: (str) -> None
        self.app_root_message_path = app_root_message_path

    def start_application(self):

        # Check if the path to the file/message folder exists and is correct
        if not self.verify_working_directory():
            return

        # Create the main window
        self.root = Tk()
        self.root.title('AFTN Terminal Application')
        self.root.geometry("1000x700+700+200")

        # The main window contains four primary display artifacts, a menu bar, a toolbar, a central frame
        # (containing a message tree view, a list of messages with errors) and a status bar.
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)

        # Add the menu bar
        menu_bar = MenuBar(self.root, self.app_root_message_path)

        # Add row 0...
        # Add the toolbar
        ToolBar(self.root)

        # Add row 1...
        # Add the frame containing a message tree view, a list of messages and a message display area
        # with a list of errors associated to a message on display
        middle_frame = CentralPanedWindow(self.root, self.app_root_message_path, menu_bar)
        middle_frame.grid(column=0, row=1, sticky=N + E + W + S)

        # Add row 2...
        # Add the status bar at the bottom
        StatusBar(self.root)

        # Run the event loop
        self.root.mainloop()

    def verify_working_directory(self):
        # type: () -> bool

        # Check if the path to the file/message folder exists and is correct
        if os.path.isdir(self.app_root_message_path):
            # Ensure all the compulsory subdirectories exist, if not create as necessary
            return self.verify_working_subdirectories()
        else:
            # A valid working directory was not provided, prompt the user to select one
            answer = askyesno("Working Directory Missing",
                              "A working directory to store messages has not been provided as a startup parameter."
                              + os.linesep +
                              "Do you want to select a working directory now?")
            if answer:
                # Yes was selected, created prompt for a working directory
                self.app_root_message_path = askdirectory(initialdir=os.getcwd(),
                                                          title="Message Working Directory Selection")
                if len(self.app_root_message_path) == 0:
                    return False

                # Working directory selected, check if the overall message
                # structure exists and create it if not.
                return self.verify_working_subdirectories()
            else:
                return False

    def verify_working_subdirectories(self):
        # type: () -> bool
        required_root_directories = ["Inbox", "Outbox", "Trash"]
        required_sub_directories = ["DD", "FF", "GG", "KK", "SS"]
        for req_dir in required_root_directories:
            if not os.path.exists(self.app_root_message_path + os.sep + req_dir):
                if not os.path.isdir(self.app_root_message_path + os.sep + req_dir):
                    # Create the required root working directory
                    try:
                        os.mkdir(self.app_root_message_path + os.sep + req_dir)
                    except FileExistsError | IsADirectoryError:
                        showerror("Working Directory Creation Error 1",
                                  "Unable to create a required working directory:" + os.linesep +
                                  self.app_root_message_path + os.sep + req_dir)
                        return False
        for req_dir in required_sub_directories:
            if not os.path.exists(self.app_root_message_path + os.sep + "Inbox" + os.sep + req_dir):
                if not os.path.isdir(self.app_root_message_path + os.sep + "Inbox" + os.sep + req_dir):
                    # Create the required working subdirectory
                    try:
                        os.mkdir(self.app_root_message_path + os.sep + "Inbox" + os.sep + req_dir)
                    except FileExistsError | IsADirectoryError:
                        showerror("Working Directory Creation Error 2",
                                  "Unable to create a required working subdirectory:" + os.linesep +
                                  self.app_root_message_path + os.sep + "Inbox" + os.sep + req_dir)
                        return False

        return True
