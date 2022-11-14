import os
from datetime import datetime
from tkinter import messagebox


class WriteXml:
    """This class writes XML content to an existing ATS XML message file or creates a new
    XML file if a new message is being created. New messages are written to a file in the
    'outbox' directory."""

    @staticmethod
    def update_existing_message(message_file_path, text_to_write):
        # type: (str, str) -> None
        """This method writes an ATS message to an existing XML message file, i.e. an update
        is being performed. The text being written must be in the application XML file
        format as obtained from parsing a message. The message parser creates a FlightPLanRecord
        instance; this class contains a method 'as_xml()' that outputs a parsed message in the
        required XML format.

        :param message_file_path: An absolute path to the existing message XML file being updated;
        :param text_to_write: The text to write to the XML file;
        :return: None
        """
        # Check if the file exists
        if not os.path.exists(message_file_path):
            messagebox.showerror(
                title="Write Message Error - 1",
                message="The Message File located in does not exist..." + os.linesep +
                        message_file_path + os.linesep +
                        "Cannot write and save the message update")
            return

        # Open the file containing the message being displayed/edited
        file_handle = os.open(message_file_path, os.O_RDWR | os.O_TRUNC)

        # Write the updated xml string
        os.write(file_handle, text_to_write.encode())

        # Close the file
        os.close(file_handle)

    @staticmethod
    def write_new_message(text_to_write, working_directory_path):
        # type: (str, str) -> None
        """This method writes an ATS message to a new XML message file, i.e. a new file is being
        created. The text being written must be in the application XML file format as obtained from
        parsing a message. The message parser creates a FlightPLanRecord instance; this class contains a
        method 'as_xml()' that outputs a parsed message in the required XML format.

        :param working_directory_path: An absolute path to the message XML file being created;
        :param text_to_write: The text to write to the XML file;
        :return: None
        """
        # Put together a complete file path for the new file
        file_path = \
            working_directory_path + os.sep + "Outbox" + os.sep + "message-" + \
            datetime.now().strftime('%Y%m%d-%H:%M:%s') + ".xml"

        # Open the file containing the message being displayed/edited
        file_handle = os.open(file_path, os.O_CREAT | os.O_RDWR | os.O_TRUNC)

        # Write the updated xml string
        os.write(file_handle, text_to_write.encode())

        # Close the file
        os.close(file_handle)
