import os
from datetime import datetime
from tkinter import messagebox


class WriteXml:

    @staticmethod
    def update_existing_message(message_file_path, text_to_write):
        # type: (str, str) -> None

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
    def write_new_message(text_to_write, app_root_message_path):
        # type: (str, str) -> None

        # Put together a complete file path for the new file
        file_path = app_root_message_path + os.sep + "Outbox" + os.sep + \
                    "message-" + datetime.now().strftime('%Y%m%d-%H:%M:%s') + ".xml"

        # Open the file containing the message being displayed/edited
        file_handle = os.open(file_path, os.O_CREAT | os.O_RDWR | os.O_TRUNC)

        # Write the updated xml string
        os.write(file_handle, text_to_write.encode())

        # Close the file
        os.close(file_handle)
