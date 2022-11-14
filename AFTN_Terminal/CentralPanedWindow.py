from tkinter import Tk, VERTICAL, HORIZONTAL, RAISED
from tkinter import PanedWindow

from Configuration.EnumerationConstants import MessageTitles
from AFTN_Terminal.MessageDisplayFrame import MessageDisplayFrame
from AFTN_Terminal.MessageListFrame import MessageListFrame
from AFTN_Terminal.MessageTree import MessageTree
from AFTN_Terminal.MenuBar import MenuBar


class CentralPanedWindow(PanedWindow):
    """This class builds a paned window, with a movable sash, containing the tree view in the left pane
    and the message display and list area in the right pane. The right pane, is itself a paned window
    containing the message list in the upper pane and the message display in the lower pane separated by a
    horizontal movable sash.
    """

    def __init__(self, parent, working_directory_path, menu_bar):
        # type: (Tk, str, MenuBar) -> None
        """This method constructs the paned window displayed in the main application window.

        :param parent: Handle to the parent window;
        :param working_directory_path: The path to the applications working directory where the
               application stores messages crated and processed by this application;
        :param menu_bar: Handle to the main application menu, passed to the message list frame;
        """
        super().__init__(parent, sashrelief=RAISED, orient=HORIZONTAL)

        # Add a test label to the LHS of this split pane, minimum width is set
        message_tree_frame = MessageTree(parent, working_directory_path)
        self.add(message_tree_frame, minsize=200)

        # Create a second split pane and add it to the RHS of this split pane
        top_bottom_split_pane = PanedWindow(self, orient=VERTICAL, sashrelief=RAISED)
        self.add(top_bottom_split_pane)

        # Add the list of messages, minimum height is set
        message_list_frame = MessageListFrame(top_bottom_split_pane, menu_bar)
        top_bottom_split_pane.add(message_list_frame, minsize=202)

        # Add the message display area along with an error frame
        message_display_frame = MessageDisplayFrame(top_bottom_split_pane, False, False, MessageTitles.UNKNOWN)
        top_bottom_split_pane.add(message_display_frame)

        # Pass handles for the following frames to classes requiring access to them
        message_tree_frame.set_message_list_frame(message_list_frame)
        message_list_frame.set_message_display_frame(message_display_frame)
