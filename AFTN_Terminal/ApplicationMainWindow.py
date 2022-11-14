import os.path
from tkinter.filedialog import askdirectory
from tkinter import Tk, N, E, W, S
from tkinter.messagebox import askyesno, showerror

from AFTN_Terminal.CentralPanedWindow import CentralPanedWindow
from AFTN_Terminal.ToolBar import ToolBar
from AFTN_Terminal.StatusBar import StatusBar
from AFTN_Terminal.MenuBar import MenuBar


class ApplicationMainWindow:
    """This class builds the AFTN Terminal Application main window and validates that a valid working
    directory is provided. If there is an invalid working directory, the user is prompted to enter
    a valid working directory.

    The working directory is used by the application to store AFTN messages received and processed
    by the application.

    To start the application, instantiate this class and call start_application()
    """

    root: Tk = None
    """The root window handle"""

    working_directory_path: str = ""
    """The working directory used by this application to store messages in"""

    def __init__(self, working_directory_path):
        # type: (str) -> None
        """This constructor store the working directory and passes it to other window frames
        used to construct the main application window.

        :param working_directory_path: The working directory used by this application to store messages in;
        """
        self.working_directory_path = working_directory_path

    def start_application(self):
        # type: () -> None
        """This method starts the AFTN Terminal Application. The window is constructed using various frames
        implemented in other classes. The working directory is checked for validity, if its invalid the
        user is prompted to enter a valid working directory.

        The working directory is used by this application to store AFTN message created and processed
        by this application. When started, the application creates a 'standard' set of directories:
            - Inbox: Contains the following subdirectories
                * DD
                * FF
                * GG
                * KK
                * SS
            - Outbox
            - Trash
        If these are not present, they are automatically created.

        :return: None
        """
        # Check if the path to the working directory is valid and the structure is correct
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
        menu_bar = MenuBar(self.root, self.working_directory_path)

        # Add row 0, the toolbar
        ToolBar(self.root)

        # Add row 1, the frame containing a message tree view, a list of messages and a message
        # display area with a list of errors associated to a message on display
        middle_frame = CentralPanedWindow(self.root, self.working_directory_path, menu_bar)
        middle_frame.grid(column=0, row=1, sticky=N + E + W + S)

        # Add row 2, the status bar at the bottom
        StatusBar(self.root)

        # Run the event loop
        self.root.mainloop()

    def verify_working_directory(self):
        # type: () -> bool
        """This method validates that the working directory exists, if its missing, the user is prompted to
        enter a valid working directory. The method verify_working_subdirectories() is used to check that
        the working directory subdirectories are present and correct.

        :return: True if the working directory and its subdirectories are all present and correct, False otherwise;
        """
        # Check if the path to the working directory folder exists and is correct
        if os.path.isdir(self.working_directory_path):
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
                self.working_directory_path = askdirectory(initialdir=os.getcwd(),
                                                           title="Message Working Directory Selection")
                if len(self.working_directory_path) == 0:
                    return False

                # Working directory selected, check if the overall message
                # structure exists and create it if not.
                return self.verify_working_subdirectories()
            else:
                return False

    def verify_working_subdirectories(self):
        # type: () -> bool
        """This method checks if the working directory subdirectories are all present and correct. If any are
        they are created by this method. The subdirectories checked and created if missing are:
            - Inbox
                * DD
                * FF
                * GG
                * KK
                * SS
            - Outbox
            - Trash

        :return: True if the working directory subdirectory structure is correct, False otherwise;
        """
        required_root_directories = ["Inbox", "Outbox", "Trash"]
        required_sub_directories = ["DD", "FF", "GG", "KK", "SS"]
        for req_dir in required_root_directories:
            if not os.path.exists(self.working_directory_path + os.sep + req_dir):
                if not os.path.isdir(self.working_directory_path + os.sep + req_dir):
                    # Create the required root working directory
                    try:
                        os.mkdir(self.working_directory_path + os.sep + req_dir)
                    except FileExistsError | IsADirectoryError:
                        showerror("Working Directory Creation Error 1",
                                  "Unable to create a required working directory:" + os.linesep +
                                  self.working_directory_path + os.sep + req_dir)
                        return False
        for req_dir in required_sub_directories:
            if not os.path.exists(self.working_directory_path + os.sep + "Inbox" + os.sep + req_dir):
                if not os.path.isdir(self.working_directory_path + os.sep + "Inbox" + os.sep + req_dir):
                    # Create the required working subdirectory
                    try:
                        os.mkdir(self.working_directory_path + os.sep + "Inbox" + os.sep + req_dir)
                    except FileExistsError | IsADirectoryError:
                        showerror("Working Directory Creation Error 2",
                                  "Unable to create a required working subdirectory:" + os.linesep +
                                  self.working_directory_path + os.sep + "Inbox" + os.sep + req_dir)
                        return False

        return True
