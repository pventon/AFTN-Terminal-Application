import os
import re
from tkinter import W, END, VERTICAL, HORIZONTAL, RIGHT, X, Y, BOTTOM, NORMAL, DISABLED
from tkinter import Tk, Scrollbar, Menu, Event, messagebox
from tkinter.messagebox import showinfo, askyesno
from tkinter.simpledialog import askstring
from tkinter.ttk import Treeview

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from AFTN_Terminal.ReadXml import ReadXml
from Configuration.EnumerationConstants import MessageTitles
from AFTN_Terminal.MessageTextEditorFrame import MessageTextEditorFrame
from AFTN_Terminal.MessageListFrame import MessageListFrame
from PIL.ImageTk import PhotoImage
import threading


class MessageTree(Treeview):
    """This class implements the application 'tree' displaying the file system containing files that
    represent the ATS messages. This class subclasses the Tkinter Treeview class and implements the following
    primary functions over and above the standard Treeview:
        - An OS File Listener class running on its own thread to notify this class / tree of underlying
          file or directory updates occurring in the applications root working directory and all its
          subdirectories for this application.
        - A rudimentary drag and drop function to enable files and directories to be dragged around in the
          tree.
    This class adds scrollbars and button event bindings to support display of a tree popup menu
    and drag and drop operations.
    """
    file_change_listener_thread = None
    root_tree_node: str = None
    app_root_message_path: str = ""
    popup_menu: Menu = None
    selected_path: str = ""
    selected_item: str = None
    message_list_frame: MessageListFrame = None
    dnd_source_item: str = ""
    dnd_source_item_parent: str = ""
    dnd_state: int = 0

    icon_root_path24 = os.path.split(os.getcwd())[0] + os.sep + "Icons" + os.sep + "Icon24" + os.sep
    """Absolute path to the Icons needed for the tree view message list"""

    icon_root_path16 = os.path.split(os.getcwd())[0] + os.sep + "Icons" + os.sep + "Icon16" + os.sep
    """Absolute path to the Icons needed for the tree view message list"""

    folder_icon16 = None
    open_doc_icon16 = None
    trash_icon16 = None
    inbox_icon16 = None
    outbox_icon16 = None
    new_folder_icon24 = None
    open_doc_icon24 = None
    delete_folder_icon24 = None
    delete_doc_icon24 = None

    def __init__(self, parent, app_root_message_path):
        # type: (Tk, str) -> None
        """This constructor adds a scrollbar and various button event bindings to the Tkinter Treeview

        :param parent: The parent window handle;
        :param app_root_message_path: The absolute path specifying the 'root' working directory for this application;
        """
        super().__init__(parent, selectmode='browse')
        self.app_root_message_path = app_root_message_path

        # Create the icon images
        self.folder_icon16 = PhotoImage(file=self.icon_root_path16 + 'folder.png')
        self.open_doc_icon16 = PhotoImage(file=self.icon_root_path16 + 'document.png')
        self.trash_icon16 = PhotoImage(file=self.icon_root_path16 + 'garbage_empty.png')
        self.inbox_icon16 = PhotoImage(file=self.icon_root_path16 + 'inbox_into.png')
        self.outbox_icon16 = PhotoImage(file=self.icon_root_path16 + 'outbox_out.png')
        self.open_doc_icon24 = PhotoImage(file=self.icon_root_path24 + 'document.png')
        self.new_folder_icon24 = PhotoImage(file=self.icon_root_path24 + 'folder_add.png')
        self.delete_folder_icon24 = PhotoImage(file=self.icon_root_path24 + 'folder_delete.png')
        self.delete_doc_icon24 = PhotoImage(file=self.icon_root_path24 + 'document_delete.png')

        # Add the scrollbars
        vertical = Scrollbar(self, orient=VERTICAL, command=self.yview)
        horizontal = Scrollbar(self, orient=HORIZONTAL, command=self.xview)
        vertical.pack(side=RIGHT, fill=Y)
        horizontal.pack(side=BOTTOM, fill=X)
        self.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.heading('#0', text="Message Folders", anchor=W)

        # Add the tree content
        abspath = os.path.abspath(self.app_root_message_path)
        self.root_tree_node = self.insert('', END, text=abspath,
                                          image=self.folder_icon16, values=[abspath], open=True)
        self.add_all_tree_nodes(self.root_tree_node, abspath)

        # Bind the callbacks for single and double clicks
        self.bind('<Button-1>', self.on_single_click)
        self.bind('<Double-1>', self.on_double_click)
        self.bind('<Button-3>', self.on_right_click)
        self.bind("<ButtonPress-1>", self.on_button_press, add='+')
        self.bind("<ButtonRelease-1>", self.on_button_up, add='+')
        self.bind("<B1-Motion>", self.on_cursor_move, add='+')

        # Start the file system change thread and listener...
        self.file_system_listener()
        self.popup_create()

    def add_all_tree_nodes(self, tree_node, path):
        # type: (str, str) -> None
        """This method adds a node to the tree for each file and directory found in the root absolute path
        working directory for this application. The root absolute path is specified at application start and
        contains all the files and directories created and manipulated by this application.
        The tree hierarchy is constructed to map the underlying OS File System hierarchy.

        :param tree_node: The tree node to which child nodes representing directories or file
                          will be added to;
        :param path: The root absolute path that recursion is performed on;
        :return: None
        """
        # Loop over the default path and display the OS file system in this tree view
        for item in os.listdir(path):
            abspath = os.path.join(path, item)
            isdir = os.path.isdir(abspath)
            if isdir:
                if re.fullmatch('Trash', item):
                    oid = self.insert(tree_node, END, text=item, image=self.trash_icon16,
                                      values=[abspath], open=False)
                elif re.fullmatch('Inbox', item):
                    oid = self.insert(tree_node, END, text=item, image=self.inbox_icon16,
                                      values=[abspath], open=False)
                elif re.fullmatch('Outbox', item):
                    oid = self.insert(tree_node, END, text=item, image=self.outbox_icon16,
                                      values=[abspath], open=False)
                else:
                    oid = self.insert(tree_node, END, text=item, image=self.folder_icon16,
                                      values=[abspath], open=False)
            else:
                oid = self.insert(tree_node, END, text=item, image=self.open_doc_icon16,
                                  values=[abspath], open=False)
            if isdir:
                self.add_all_tree_nodes(oid, abspath)

    def add_tree_node(self, new_item_path):
        # type: (str) -> None
        """This method adds a new node to the tree; this method is called when the OS file system
        reports that a new file or directory has been created. This event is picked up by the file listener
        class also implemented in this file. A new file or directory can be created for one of two reasons:
            - A new item has been manually added to the tree using the application GUI; when this happens
              a new tree node is added to the tree and a file / directory is created in the file system.
              The file system reports the creation event and this method is called.
            - A file / directory is created outside this application resulting in this method being
              called.
        In the first case we do not need to do anything as both the tree node and file / directory have
        both been created. In the second case we need to locate the directory in which the new file /
        directory has been placed and add this to the tree as a new tree node.

        :param new_item_path: The full absolute path for the newly created file / directory;
        :return: None
        """
        # Get the root tree node
        tree_root_node = self.root_tree_node

        # Recurse through the tree nodes searching for the new item
        node_found = self.item_in_tree(tree_root_node, new_item_path)
        if len(node_found) == 0:
            # The new item is not in the tree, implies the file / directory was not created
            # by this application and has to be added to the tree. The new item path minus the
            # new file / directory must already exist in the file system and hence the tree.
            # The new item needs to be split from the existing path;
            # For example, if the 'new_item_path' is e.g. /home/ls/AFTN-Messages/Test04/Test07/Test08,
            # 'existing_path' will contain /home/ls/AFTN-Messages/Test04/Test07
            existing_path = os.path.split(new_item_path)[0]
            # If the 'new_item_path' is e.g. /home/ls/AFTN-Messages/Test04/Test07/Test08,
            # new_item will contain Test08
            new_item = os.path.split(new_item_path)[1]

            # Recurse over the tree again looking for an existing path that the new item was placed
            # in the file system
            node_found = self.item_in_tree(tree_root_node, existing_path)

            # If the tree contains this path (and it really ought to as it reflects the file system),
            # The new item has to inserted to this node
            if len(node_found) > 0:
                # Add new leaf node to the treeview
                if os.path.isdir(existing_path):
                    self.insert(node_found, 'end', image=self.folder_icon16,
                                text=new_item, values=[new_item_path], open=False)
                else:
                    self.insert(node_found, 'end', image=self.open_doc_icon16,
                                text=new_item, values=[new_item_path], open=False)
            # else:
            # There should not be an else here, if this happens, things have got really messed up;
            # It implies the file system structure changed between the file system creation event
            # and this method being called.
        # else:
        # Nothing to be done as the new item is already in the tree, implies it was manually created
        # using the application GUI.

    def is_compulsory_directory(self):
        # type: () -> bool
        """This method checks if the currently selected tree node represents a directory name
        that cannot be deleted. There are a number of directories this application expects to
        have in place at all times, these are:
            - Inbox: New messages received on the AFTN network interface are placed into this
              directory if the priority indicator is unknown, or one of the subdirectories
              shown below if the priority indicator is known;
            - Outbox: Newly created messages are place in the Outbox ready for transmission on the
              AFTN network interface;
            - Trash: Deleted message are placed in this directory
            - DD, FF, GG, KK, SS: All subdirectories of the Inbox, new messages received on the AFTN
              network interface are placed into these directories if the priority
              indicator is known.

        :return: True if the directory being deleted is a compulsory directory, False otherwise;
        """
        compulsory_text = self.item(self.selected_item)['text']
        if self.selected_item == self.root_tree_node or \
                re.fullmatch("DD|FF|GG|KK|SS|Outbox|Inbox|Trash", compulsory_text):
            return True
        return False

    def delete_tree_node(self, deleted_item_path):
        # type: (str) -> None
        """This method deletes a node from the tree; this method is called when the OS file system
        reports that a file or directory has been deleted. This event is picked up by the file listener
        class also implemented in this file. A file or directory can be deleted for one of two reasons:
            - A tree item / node has been manually deleted from the tree using the application GUI; when
              this happens a tree node is deleted from the tree and the associated file / directory is
              deleted from the file system.
              The file system reports the deletion event and this method is called.
            - A file / directory is created outside this application resulting is this method being
              called.
        In the first case we do not need to do anything as both the tree node and file / directory have
        both been deleted. In the second case, the file was deleted from the OS file system but the node
        still exists in the tree; we need to locate the tree node associated with the deleted file /
        directory in the tree and delete it.

        :param deleted_item_path: The full absolute path for the file / directory that has been deleted;
        :return: None
        """
        # Get the root tree node
        tree_root_node = self.root_tree_node

        # Recurse through the tree nodes searching for the tree node associated with the deleted file/directory
        node_found = self.item_in_tree(tree_root_node, deleted_item_path)
        if len(node_found) > 0:
            # The tree node associated with the deleted file / directory has been found in the tree,
            # implies the file / directory was deleted outside this application and the associated
            # tree node has to be deleted.
            self.delete(node_found)
        # else:
        # Nothing to be done as the tree node does not exist in the tree, implies it was manually deleted
        # from the application GUI.

    def file_system_listener(self):
        # type: () -> None
        """This method starts the system file listener thread

        :return: None
        """
        # Create a thread to listen for file systems changes...
        self.file_change_listener_thread = FileChangeListenerThread(self)

        # Start new Thread and start listening for changes...
        self.file_change_listener_thread.start()

    def item_in_tree(self, tree_node, path_to_find):
        # type: (str, str) -> str
        """This method performs a recursive search over the tree hierarchy searching for
        a tree node item containing the 'values' content matching that in the parameter 'path_to_find'.
        The tree node 'values' content contains the full file system path for the file / directory
        represented by each node in the tree.

        :param tree_node: A node in the tree hierarchy;
        :param path_to_find: An absolute path to a file or directory that this method is searching for;
        :return: The tree node item as a string or an empty string if the absolute path contained
                 in 'path_to_find' could not be found;"""
        # This first check is required to ensure the tree root node is checked
        # Compare the root with the path to find
        if re.fullmatch(path_to_find, self.item(tree_node)['values'][0]):
            return tree_node

        # Get any child nodes
        children = self.get_children(tree_node)

        # Loop over the child nodes
        for child in children:
            # Check if this node matches what we are looking for
            if re.fullmatch(path_to_find, self.item(child)['values'][0]):
                return child
            # Not found, recurse down the tree
            retval = self.item_in_tree(child, path_to_find)
            # Return the tree node if one was found further down the tree
            if len(retval) > 0:
                return retval
        # Nothing found, return an empty string
        return ""

    def move_file_os(self, modified_path):
        # type: (str) -> None
        """This method handles the case when a file is moved using the underlying OS instead of
        the application GUI. In Linux, when the 'mv' command is used, a directory 'modified' event is
        generated twice, once when a file is moved out of a directory and once when a file is added to a
        directory. The only way to deal with this is to rebuild the complete tree node from the path
        provided by the parameter 'modified_path'. This is not optimal, but is a simple way to
        do this, it is not envisaged that files will be moved very often.

        :param modified_path: The path for the directory being modified by the movement of files
                              into or out of this directory;
        :return: None
        """
        # Recurse through the tree nodes searching for the new item
        node_found = self.item_in_tree(self.root_tree_node, modified_path)
        if len(node_found) > 0:
            # Found the tree node that needs to be updated, delete all the child nodes
            children = self.get_children(node_found)
            # Loop over the child nodes and delete them
            for child in children:
                self.delete(child)
            # Rebuild the node
            self.add_all_tree_nodes(node_found, modified_path)

    def move_tree_node(self):
        pass

    def on_button_press(self, event):
        # type: (Event) -> None
        """This method is invoked when the left mouse button is pressed; the event initiates
        the start of a drag and drop operation. The drag and drop is implemented as a simple state
        machine, this method changes the state from '0' to '1' indicating a state change from no DnD
        operation in progress to Dnd start operation. The DnD operation is only started if a tree
        node has been successfully selected. The cursor is set to indicate a DnD drag operation
        is commencing.

        The DnD state machine is maintained with the variable self.dnd_state:
            - 0 Indicates no DnD operation currently is progress; (set by on_button_up()
            - 1 Indicates DnD operation has started;  (set by on_button_press()
            - 2 Indicates drag operation is progress or has occurred; (set by on_cursor_move())

        :param event: Contains the tree widget being selected; used to obtain a selected node from
                      the tree;
        :return: None
        """
        # Save the selected tree item
        treeview = event.widget
        self.dnd_source_item = treeview.identify('item', event.x, event.y)

        # Only start a DnD operation if a valid item was selected
        if len(self.dnd_source_item) > 0:
            # Save the parent of the item being dragged
            self.dnd_source_item_parent = self.parent(self.dnd_source_item)

            # Set the cursor indicating DnD has started
            self.config(cursor="fleur")

            # Set a flag indicating DnD has started
            self.dnd_state = 1

    def on_button_up(self, event):
        """This method is invoked when the left mouse button is released; if the DnD state is correct.
        (state '2') then a valid DnD drop operation is initiated. The target tree node must be different
        from the source and both the source and target nodes must both be valid. The DnD drop operation
        will move the source node to the target node. The cursor is set back to a pointer.
        For this DnD drop operation to succeed the DnD state must be 2.

        The DnD state machine is maintained with the variable self.dnd_state:
            - 0 Indicates no DnD operation currently is progress; (set by on_button_up()
            - 1 Indicates DnD operation has started; (set by on_button_press())
            - 2 Indicates drag operation is progress or has occurred; (set by on_cursor_move())

        :param event: Contains the tree widget being selected; used to obtain a selected node from
                      the tree;
        :return: None
        """
        # Set the cursor back to an arrow as DnD is being terminated
        self.config(cursor="arrow")

        # Check that a DnD operation is in progress, if not bail out
        if self.dnd_state != 2:
            return

        # Get the item under the cursor, this is the 'target' drop item
        treeview = event.widget
        target_drop_item = treeview.identify('item', event.x, event.y)

        # If the target drop item is invalid, bail out
        if target_drop_item == "":
            return

        # The target item must be a folder
        if not os.path.isdir(self.item(target_drop_item)['values'][0]):
            # Get the parent and use it as the drop target
            target_drop_item = self.parent(target_drop_item)

        # If the target item parent is the same as the source item, do nothing;
        # It means we are trying to drop an item into the same folder as its already in
        if target_drop_item == self.dnd_source_item_parent:
            return

        # The source and target items must be valid, (target item checked above) and
        # the source and target items must not be the same item, and
        # it must be a drag and drop operation, indicated by the self.dnd_state
        if self.dnd_source_item != "" \
                and target_drop_item != self.dnd_source_item \
                and self.dnd_state == 2:
            # Save the source and destination paths, so we can move the files on the OS file system
            source_file_path = self.item(self.dnd_source_item)['values'][0]
            destination_file_path = \
                self.item(target_drop_item)['values'][0] + os.sep + self.item(self.dnd_source_item)['text']

            # Insert the source item into the drop target
            if os.path.isdir(self.dnd_source_item):
                self.insert(target_drop_item, END, image=self.folder_icon16,
                            text=self.item(self.dnd_source_item)['text'],
                            values=self.item(self.dnd_source_item)['values'], open=True)
            else:
                self.insert(target_drop_item, END, image=self.open_doc_icon16,
                            text=self.item(self.dnd_source_item)['text'],
                            values=self.item(self.dnd_source_item)['values'], open=True)
            # Delete the source item
            self.delete(self.dnd_source_item)
            # Rename/move the file being dragged and dropped
            try:
                os.rename(source_file_path, destination_file_path)
            except OSError as error:
                self.show_error_box(
                    "Move File Error - 1",
                    "OS Exception " + error.strerror + os.linesep + "Failed to move " + source_file_path + " to:",
                    destination_file_path)

        # Indicate the DnD operation has been completed
        self.dnd_state = 0

    def on_cursor_move(self, event):
        """This method is invoked when the cursor is moved; if the DnD state is greater than zero when this
        method is called, the DnD state is set to '2' to indicate a DnD drag is in progress. As the cursor moves
        over the tree nodes, the nodes are highlighted if they represent a directory. The highlighted node
        is the 'target' node for the drop operation. If the cursor lies over a file node, its parent is
        highlighted instead of the file node.

        The DnD state machine is maintained with the variable self.dnd_state:
            - 0 Indicates no DnD operation currently is progress; (set by on_button_up()
            - 1 Indicates DnD operation has started; (set by on_button_press())
            - 2 Indicates drag operation is progress or has occurred; (set by on_cursor_move())

        :param event: Contains the tree widget being selected; used to obtain a selected node from
                      the tree;
        :return: None
        """
        # Check we are doing a DnD operation
        if self.dnd_state > 0:

            # on_button_press() has been called, set the cursor
            self.config(cursor="fleur")

            # Indicate we are in DnD drag state
            self.dnd_state = 2

            # Get the tree item under the cursor
            tv = event.widget
            item_under_cursor = tv.identify('item', event.x, event.y)

            # If the cursor is not on a valid item, we don't highlight anything
            if item_under_cursor == "":
                return

            # We only highlight the folders, if it's on a file, highlight the parent
            if os.path.isdir(self.item(item_under_cursor)['values'][0]):
                # If it's a directory, highlight on the GUI
                tv.selection_set(item_under_cursor)
            else:
                # Keep a file highlighted until the cursor moves out of the
                # current parent folder
                if self.dnd_source_item_parent == self.parent(item_under_cursor):
                    tv.selection_set(item_under_cursor)
                else:
                    # Get the parent and highlight it
                    tv.selection_set(self.parent(item_under_cursor))

    def on_open_file(self):
        # type: () -> None
        """This method is invoked from the tree popup menu 'open file' menu item; upon selection the message
        text editor is opened displaying the message for the file tree node selected in the tree. The tree
        popup menu is displayed by a right click on a file tree node.

        :return: None
        """
        # Open the message editor invoked by selecting 'Open' in the tree view popup menu
        rx = ReadXml(self.selected_path)
        if rx.is_message_ok():
            mte = MessageTextEditorFrame(self, False, MessageTitles.UNKNOWN,
                                         rx.get_creation_time(), rx.get_modification_time(),
                                         self.app_root_message_path)
            mte.set_message(self.selected_path)

    def on_create_folder(self):
        # type: () -> None
        """This method is invoked from the tree popup menu 'create folder' menu item; a simple dialogue
        is displayed for the user to input a folder name after which this method will create the folder
        in the underlying OS file system and add a new folder node to the tree. The tree
        popup menu is displayed by a right click on a file tree node.

        :return: None
        """
        # Create a new directory in the tree view hierarchy
        dir_name = self.prompt_for_folder_name()
        if dir_name is not None:
            try:
                # Add new leaf node to the tree the treeview
                self.insert(self.selected_item, 'end', text=dir_name, image=self.folder_icon16,
                            values=[self.selected_path + os.sep + dir_name], open=False)
                # Create the new folder
                os.mkdir(self.selected_path + os.sep + dir_name)
            except FileExistsError:
                self.show_error_box(
                    "Create File/Directory Error - 1",
                    "Could not create the file/directory, file/directory already exists:",
                    self.selected_path + os.sep + dir_name)
            except OSError:
                self.show_error_box(
                    "Create Directory Error - 2",
                    "Could not create the directory from the tree view with the following filename:",
                    self.selected_path + os.sep + dir_name)

    def on_delete(self):
        # type: () -> None
        """This method is invoked from the tree popup menu 'delete folder' or 'delete file' menu items;
        A deletion confirmation message box is displayed before the delete operation. If a folder is being deleted,
        it must be empty before it can be deleted. The deletion will delete the file or folder from the
        underlying OS file system and delete the associated tree node from the tree. The tree
        popup menu is displayed by a right click on a file tree node.

        :return: None
        """
        # Delete a file or folder, check if its a folder...
        isdir = os.path.isdir(self.selected_path)
        if isdir:
            # If the folder contains anything, bail out
            if len(self.get_children(self.selected_item)) > 0:
                # Cannot delete because directory is not empty
                self.show_info_box(self, "Delete Directory Error - 1",
                                   "Cannot delete a Folder containing Messages;")
                return

            # All OK, delete the selected directory, display a confirmation dialogue before deleting
            answer = self.show_ask_yes_no_box(self, "Delete Folder Confirmation",
                                              "Are you sure you want to delete the Folder:",
                                              self.selected_path)
            if answer:
                try:
                    # Remove the directory from the file system
                    os.rmdir(self.selected_path)
                    # Delete the node from the tree
                    self.delete(self.selected_item)
                except OSError:
                    self.show_error_box(
                        "Delete Directory Error - 2",
                        "Could not delete the directory from the tree view with the following filename:",
                        self.selected_path)
        else:
            # Delete a file, display a confirmation dialogue before deleting the file
            answer = self.show_ask_yes_no_box(self, "Delete Message Confirmation",
                                              "Are you sure you want to delete the Message:",
                                              self.selected_path)
            if answer:
                try:
                    # Delete the node from the tree
                    self.delete(self.selected_item)
                    # Remove the file from the file system
                    os.remove(self.selected_path)
                except OSError:
                    self.show_error_box(
                        "Delete Message Error - 1",
                        "Could not delete the file from the tree view with the following filename:",
                        self.selected_path)

    def on_double_click(self, event):
        # type: (Event) -> None
        """This method is invoked when a double click occurs on a tree node; if the double click occurs
        on a file node, the message text editor is opened and the selected message displayed.

        :return: None
        """
        # Get the selected item
        self.selected_item = self.identify('item', event.x, event.y)

        # If there is nothing selected, bail out
        if self.selected_item is None or self.selected_item == "":
            return

        # Save the path and filename for the currently selected item
        self.selected_path = self.item(self.selected_item)['values'][0]

        # If this double click was on a file, then open it
        if not os.path.isdir(self.selected_path):
            rx = ReadXml(self.selected_path)
            if rx.is_message_ok():
                mte = MessageTextEditorFrame(self, False, MessageTitles.UNKNOWN,
                                             rx.get_creation_time(), rx.get_modification_time(), "")
                mte.set_message(self.selected_path)

    def on_single_click(self, event):
        # type: (Event) -> None
        """ This method selects a tree node causing it to be displayed in its highlight color, and if the
        selected node is a folder that contains messages, the messages will be displayed in the message list
        area. If the item selected is a file, then the parent directory is used to display all messages
        contained in the parent directory in the message list area.

        :param event: Contains the tree widget being selected; used to obtain a selected node from
                      the tree;
        :return: None
        """
        # Get the selected item
        self.selected_item = self.identify('item', event.x, event.y)

        # If there is nothing selected, bail out
        if self.selected_item is None or self.selected_item == "":
            return

        # Save the path and filename for the currently selected item
        self.selected_path = self.item(self.selected_item)['values'][0]

        # Update the list of messages to reflect the content of the selected folder
        self.update_message_list()

    def on_right_click(self, event):
        # type: (Event) -> None
        """ This method displays the tree popup menu that contains menu items to delete a file/message or folder,
        add a new folder or open a file. The menu items are enabled/disabled depending on the node type selected.
        Once a node is selected, any messages are also displayed in the message list area as is the case when
        a node is selected with a single left mouse button click.

        :param event: Contains the tree widget being selected; used to obtain a selected node from
                      the tree;
        :return: None
        """
        # Get the selected item
        self.selected_item = self.identify('item', event.x, event.y)

        # If there is nothing selected, bail out
        if self.selected_item is None or self.selected_item == "":
            return

        # Highlight the selection in the GUI that the right click occurred on
        self.selection_set(self.selected_item)

        # Save the path and filename for the currently selected item
        self.selected_path = self.item(self.selected_item)['values'][0]

        # Update the list of messages in the message list
        self.update_message_list()

        # Determine and display the tree view popup menu, different for
        # a file and folder
        if os.path.isdir(self.selected_path):
            self.popup_display(event, True)
        else:
            self.popup_display(event, False)

    def popup_focus_out(self, event):
        # type: (Event) -> None
        """This method ensure that the popup menu is removed from display when it loses focus, i.e. another
        window is 'clicked'.

        :param event: Contains the tree widget being selected; used to obtain a selected node from
                      the tree;
        :return: None
        """
        # Release the focus on the popup and close it when it loses the focus
        self.popup_menu.unpost()

    def popup_create(self):
        # type: () -> None
        """This method creates the tree popup menu display on a right click of the mouse.

        :return: None
        """
        # Create menu
        self.popup_menu = Menu(self, tearoff=0)
        self.popup_menu.add_command(label="New Folder...", command=self.on_create_folder,
                                    image=self.new_folder_icon24, compound='left')
        self.popup_menu.add_command(label="Open Message...", command=self.on_open_file,
                                    image=self.open_doc_icon24, compound='left')
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Delete Folder", command=self.on_delete,
                                    image=self.delete_folder_icon24, compound='left')
        self.popup_menu.add_command(label="Delete Message", command=self.on_delete,
                                    image=self.delete_doc_icon24, compound='left')
        self.popup_menu.bind("<FocusOut>", self.popup_focus_out)

    def popup_display(self, event, is_directory):
        # type: (Event, bool) -> None
        """This method displays the tree popup menu with the individual menu items enabled/disabled based
        on the node type selected, folder of file/message.

        :param event: Contains the tree widget being selected; used to obtain a selected node from
                      the tree;
        :param is_directory: Boolean indicating if the selected tree node is a directory or file/message,
                             True if it's a directory, False otherwise;
        :return: None
        """
        # Set the enable/disabled state of the popup menu items depending
        # on it being opened on a file or directory
        if is_directory:
            self.popup_menu.entryconfig(0, state=NORMAL)
            self.popup_menu.entryconfig(1, state=DISABLED)
            # Index 2 is the separator
            if self.is_compulsory_directory():
                self.popup_menu.entryconfig(3, state=DISABLED)
            else:
                self.popup_menu.entryconfig(3, state=NORMAL)
            self.popup_menu.entryconfig(4, state=DISABLED)
        else:
            self.popup_menu.entryconfig(0, state=DISABLED)
            self.popup_menu.entryconfig(1, state=NORMAL)
            # Index 2 is the separator
            self.popup_menu.entryconfig(3, state=DISABLED)
            self.popup_menu.entryconfig(4, state=NORMAL)

        # Display the popup menu
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # Release the focus and hide the menu
            self.popup_menu.grab_release()

    def prompt_for_folder_name(self):
        # type: () -> str | None
        """This method displays a message box prompting input of a folder name when the tree popup menu
        item 'new folder' is selected. The input is syntactically checked for valid characters,
        (lower and upper case 'A' to 'Z', digits '0' to '9', period, underscore and hyphen) and that the
        folder name does not start with a digit.

        :return: A string containing the new folder name or None if the input dialogue is cancelled;
        """

        # Display a message box to input a folder name into
        dir_name = self.show_ask_string_box(self, 'New Folder', 'Enter a Folder Name')
        if dir_name is None:
            return None
        if re.fullmatch("[A-Za-z0-9-_.]+", dir_name):
            return dir_name
        # Show information about what the problem is
        self.show_info_box(self, "Input Error", "Only Aa to Zz, 0 to 9, '.', '-' and '_' allowed as a Folder name;")
        # Recurse until the input is correct or the user cancels the operation
        return self.prompt_for_folder_name()

    def set_message_list_frame(self, message_list_frame):
        # type: (MessageListFrame) -> None
        """This method sets an instance of the message list area so that this class can update the message
        list. This method is invoked from the constructor building the complete application GUI.

        :param message_list_frame: An instance of the MessageListFrame containing the message
        display area/list.
        :return: None
        """
        # Store a handle to the list frame so this class can send it messages
        self.message_list_frame = message_list_frame

    @staticmethod
    def show_error_box(title, message, path):
        # type: (str, str, str) -> None
        """This method is a helper method to display a 'error' message box;

        :param title: The title displayed in the message box;
        :param message: The error message to display in the message box;
        :param path: The path of the erroneous file system item to which this error pertains;
        :return: None
        """
        messagebox.showerror(title=title, message=message + os.linesep + path)

    @staticmethod
    def show_info_box(parent, title, message):
        # type: (Treeview, str, str) -> None
        """This method is a helper method to display a 'info' message box;

        :param parent: Handle to the parent window of the info box;
        :param title: The title displayed in the info box;
        :param message: The error message to display in the info box;
        :return: None
        """
        showinfo(title, message, parent=parent)

    @staticmethod
    def show_ask_string_box(parent, title, message):
        # type: (Treeview, str, str) -> str
        """This method is a helper method to display a 'ask string' message box;

        :param parent: Handle to the parent window of the 'ask string' box;
        :param title: The title displayed in the 'ask string' box;
        :param message: The error message to display in the 'ask string' box;
        :return: None
        """
        return askstring(title, message, parent=parent)

    @staticmethod
    def show_ask_yes_no_box(parent, title, message, path):
        # type: (Treeview, str, str, str) -> bool
        """This method is a helper method to display a 'ask yes/no' message box;

        :param parent: Handle to the parent window of the 'ask yes/no' message box;
        :param title: The title displayed in the 'ask yes/no' message box;
        :param message: The error message to display in the 'ask yes/no' message box;
        :param path: The path of the erroneous file system item to which this error pertains;
        :return: None
        """
        return askyesno(title, message + os.linesep + path, parent=parent)

    def update_message_list(self):
        # type: () -> None
        """This method updates the message list displayed in the MessageTreeFrame with the messages
        contained in a tree node directory manually selected in the application GUI. If a message
        (file) is selected, the parent folder is used as the root from which all messages are displayed.

        :return: None
        """
        # Update the list of messages to reflect the content of the selected folder
        # or the parent folder if a file is selected
        if os.path.isdir(self.selected_path):
            folder_item_to_display = self.selected_item
        else:
            folder_item_to_display = self.parent(self.selected_item)

        # Get the child nodes of the currently selected node
        children = self.get_children(folder_item_to_display)

        # Loop over the child nodes and recover the path and filename for each node
        item_paths = []
        for child in children:
            item_paths.append(self.item(child)['values'][0])

        # Pass the list of zero or more path and filenames for the selected tree node to the message list
        self.message_list_frame.update_list_entries(item_paths)

    def __del__(self):
        # type: () -> None
        """This method destroys the File Listener thread and associated resources;

        :return: None
        """
        # Destroy the file listener thread resources
        self.file_change_listener_thread.join(1.0)
        # destroy the popup menu created by this class
        self.popup_menu.destroy()


class FileChangeListenerThread(threading.Thread):
    """This class subclasses the Python 'threading.Thread' class in order to create a thread
    to run the OS File Listener class which notifies this application when a change
    is made to the underlying OS file system.
    """
    observer = None
    app_root_message_path = ""
    treeview = None

    def __init__(self, treeview):
        # type: (MessageTree) -> None
        """This constructor takes an instance of the 'MessageTreeFrame' in order that the OS File Listener
        can call methods in the treeview to update the tree nodes based on file / directory creation
        and / or deletion events.

        :param treeview: An instance of the 'MessageTreeFrame' containing the treeview to be updated
                         based on the underlying OS file system events;
        """
        super().__init__()
        self.app_root_message_path = treeview.app_root_message_path
        self.name = "File System Observer"
        self.observer = Observer()
        self.treeview = treeview

    def run(self):
        # type: () -> None
        """This method runs the thread containing the OS File Listener; the OS File Listener
        is instantiated and runs in the background listening for underlying file system changes
        (file / directory creation and deletion)..

        :return: None
        """
        print("Schedule File System Observer for '" + self.app_root_message_path + "'...")
        self.observer.schedule(TreeviewFileSystemEventHandler(self.treeview),
                               self.app_root_message_path, recursive=True)
        print("Starting File System Observer...")
        self.observer.start()
        print("File System Observer running")

    def join(self, timeout=None):
        # type: (float) -> None
        """This method stops the thread containing the OS File Listener.

        :param timeout:
        :return:
        """
        print("Stopping File System Observer...")
        self.observer.stop()
        self.observer.join()
        print("File System Observer Stopped")


class TreeviewFileSystemEventHandler(FileSystemEventHandler):
    """This class subclasses the 'FileSystemEventHandler' which listens for changes made to the
    OS file system, this includes file deletion, creation, modification and closure.
    The events of interest are created and deletion. This class is instantiated on a dedicated
    thread to ensure parallel processing while the GUI is running.

    If an event is detected the treeview nodes are updated, (new nodes added on file or directory
    creation and node removal on file or directory deletion).
    """
    treeview = None

    def __init__(self, treeview):
        # type: (MessageTree) -> None
        """This constructor takes an instance of the 'MessageTreeFrame' class in order to call
        the tree node add and delete node methods, called when a new file / directory is
        created or deleted.

        :param treeview: An instance handle of the 'MessageTreeFrame' containing the treeview
                         that has to be updated due to underlying OS file system activity;
        """
        self.treeview = treeview

    def on_created(self, event):
        """This method is invoked when the underlying OS file system creates a new file
        or directory. This method calls a method in the 'MessageTreeFrame' instance
        to update the tree by adding a new tree node.

        :param event: The data for the file or directory creation event that contains the path
                      and file name of the created file or directory;
        :return: None
        """
        print("OS Creation: " + event.src_path)
        # Add a tree node to the treeview for the file / directory being created
        self.treeview.add_tree_node(event.src_path)

    def on_closed(self, event):
        """This method does nothing, the application has no interest when a file is closed.

        :param event: The data for the file closing event that contains the path
                      and file name of the file being closed;
        :return: None
        """
        print("OS Closed: " + event.src_path)
        pass

    def on_deleted(self, event):
        """This method is invoked when the underlying OS file system deletes a file
        or directory. This method calls a method in the 'MessageTreeFrame' instance
        to update the tree by deleting a tree node.

        :param event: The data for the file or directory deletion event that contains the path
                      and file name of the deleted file or directory;
        :return: None
        """
        print("OS Deleted: " + event.src_path)
        # Delete the tree node associated with the file / directory being deleted
        self.treeview.delete_tree_node(event.src_path)

    def on_modified(self, event):
        """This method handles the case when a file is moved using the underlying OS instead of
        the application GUI. In Linux, when the 'mv' command is used, this 'modified' method is
        called twice, once for the source and once for the target. The filename is not included
        in event.src_path. Hence, the only way to deal with this is to rebuild the complete tree node
        from the path provided by this method.

        :param event: The data for the directory modification event that contains the path of the
                      directory being modified;
        :return: None
        """
        self.treeview.move_file_os(event.src_path)
