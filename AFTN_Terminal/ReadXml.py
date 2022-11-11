import os.path
import re
from datetime import datetime
from tkinter import messagebox
import xml.etree.ElementTree as Et

from Configuration.EnumerationConstants import FieldIdentifiers, SubFieldIdentifiers


class ReadXml:
    message_file_path: str = ""
    creation_time: str = ""
    modification_time: str = ""
    creation_time_seconds: float = 0.0
    modification_time_seconds: float = 0.0
    root_element = None
    message_ok = False

    def __init__(self, message_file_path):
        # type: (str) -> None

        # Check if the file exists
        if not os.path.exists(message_file_path):
            messagebox.showerror(
                title="Read Message Error - 1",
                message="The Message File located in..." + os.linesep +
                        message_file_path + os.linesep + " does not exist")
            return

        # Save the message path and file name
        self.message_file_path = message_file_path

        # Get and save the number of seconds since the epoch (00:00:00 UTC on 1 January 1970)
        # for both creation and modification times
        self.creation_time_seconds = os.path.getctime(message_file_path)
        self.modification_time_seconds = os.path.getmtime(message_file_path)

        # Convert and save the time in seconds to a timestamp string
        self.creation_time = \
            datetime.fromtimestamp(self.modification_time_seconds).strftime('%Y-%m-%d %H:%M:%S')
        self.modification_time = \
            datetime.fromtimestamp(self.modification_time_seconds).strftime('%Y-%m-%d %H:%M:%S')

        # Indicate that the message has been successfully read
        self.message_ok = self.read_message_file()

    def build_message(self):
        # type: () -> str
        icao_fields = self.get_base_node("icao_fields")
        if icao_fields is None:
            return ""
        message = ""
        seperator = " "
        title = ""
        new_line = os.linesep
        for icao_field in icao_fields:
            field_text = icao_field.text.rstrip(" \n\r")
            field_id = icao_field.attrib['id']
            if re.fullmatch("PRIORITY_INDICATOR", field_id):
                message = message + field_text + seperator
            elif re.fullmatch("ADDRESS", field_id):
                message = message + field_text
            elif re.fullmatch("FILING_TIME", field_id):
                message = message + new_line + field_text + seperator
            elif re.fullmatch("ORIGINATOR", field_id):
                message = message + field_text
            elif re.fullmatch("ADADDRESS", field_id):
                if len(field_text) > 0:
                    message = message + new_line + field_text
            elif re.fullmatch("F3", field_id):
                message = message + new_line + "(" + field_text
                seperator = "-"
                title = field_text
            # elif re.full match("FILING_TIME", field_id):
            #     message = message + new_line + seperator + field_text
            elif re.match("ALR", title) and re.fullmatch("F7|F9|F13|F15|F16|F18|F19|F20", field_id):
                message = message + new_line + seperator + field_text
            elif re.match("CPL|FPL", title) and re.fullmatch("F9|F13|F15|F16|F18", field_id):
                message = message + new_line + seperator + field_text
            elif re.match("SPL", title) and re.fullmatch("F16|F18|F19", field_id):
                message = message + new_line + seperator + field_text
            else:
                if len(field_text) > 0:
                    message = message + seperator + field_text

        return (message.rstrip(seperator) + ")").lstrip(new_line)

    def get_adjacent_unit_sender(self):
        # type: () -> str
        adjacent_unit_sender = self.get_base_node("adjacent_unit_sender")
        if adjacent_unit_sender is None:
            return ""
        return adjacent_unit_sender.text

    def get_adjacent_unit_receiver(self):
        # type: () -> str
        adjacent_unit_receiver = self.get_base_node("adjacent_unit_receiver")
        if adjacent_unit_receiver is None:
            return ""
        return adjacent_unit_receiver.text

    def get_all_errors(self):
        # type: () -> []
        return self.get_icao_field_errors() + self.get_ers_errors()

    def get_base_node(self, element_name):
        # type: (str) -> Et.Element | None
        for child in self.root_element:
            if re.fullmatch(element_name, child.tag):
                return child
        return None

    def get_creation_time(self):
        # type: () -> str
        return self.creation_time

    def get_creation_time_seconds(self):
        # type: () -> float
        return self.creation_time_seconds

    def get_derived_flight_rules(self):
        # type: () -> str
        derived_flight_rules = self.get_base_node("derived_flight_rules")
        if derived_flight_rules is None:
            return ""
        return derived_flight_rules.text

    def get_ers_errors(self):
        # type: () -> []
        retval = []
        ers_node = self.get_ers_node()
        if ers_node is None:
            return retval
        for ers_data in ers_node:
            if re.fullmatch("ers_errors", ers_data.tag):
                for error_record in ers_data:
                    retval.append([error_record.attrib['error_text'],
                                   int(error_record.attrib['start_index']),
                                   int(error_record.attrib['end_index'])])
        return retval

    def get_ers_node(self):
        # type: () -> Et.Element | None
        return self.get_base_node("ers")

    def get_ers_records(self):
        # type: () -> []
        retval = []
        ers_node = self.get_ers_node()
        if ers_node is None:
            return retval

        for ers_record in ers_node:
            if re.fullmatch("ers_record", ers_record.tag):
                retval.append([ers_record.text,
                               ers_record.attrib['flight_rules'],
                               ers_record.attrib['speed'],
                               ers_record.attrib['altitude'],
                               int(ers_record.attrib['start_index']),
                               int(ers_record.attrib['end_index']),
                               ers_record.attrib['break_text']])
        return retval

    def get_f3(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F3)

    def get_f3a(self):
        return self.get_subfield_fx(FieldIdentifiers.F3, SubFieldIdentifiers.F3a)

    def get_f5(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F5)

    def get_f7(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F7)

    def get_f7a(self):
        return self.get_subfield_fx(FieldIdentifiers.F7, SubFieldIdentifiers.F7a)

    def get_f8(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F8)

    def get_f9(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F9)

    def get_f9b(self):
        return self.get_subfield_fx(FieldIdentifiers.F9, SubFieldIdentifiers.F9b)

    def get_f9c(self):
        return self.get_subfield_fx(FieldIdentifiers.F9, SubFieldIdentifiers.F9c)

    def get_f10(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F10)

    def get_f13(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F13)

    def get_f13a(self):
        return self.get_subfield_fx(FieldIdentifiers.F13, SubFieldIdentifiers.F13a)

    def get_f13b(self):
        return self.get_subfield_fx(FieldIdentifiers.F13, SubFieldIdentifiers.F13b)

    def get_f14(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F14)

    def get_f15(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F15)

    def get_f16(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F16)

    def get_f16a(self):
        return self.get_subfield_fx(FieldIdentifiers.F16, SubFieldIdentifiers.F16a)

    def get_f17(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F17)

    def get_f18(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F18)

    def get_f19(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F19)

    def get_f20(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F20)

    def get_f21(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F21)

    def get_f22(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.F22)

    def get_fx(self, field_id):
        # type: (FieldIdentifiers) -> str
        icao_fields = self.get_base_node("icao_fields")
        if icao_fields is None:
            return ""
        for icao_field in icao_fields:
            if re.fullmatch(field_id.name, icao_field.attrib["id"]):
                return icao_field.text.rstrip(" \n\r")
        return ""

    def get_icao_field_errors(self):
        # type: () -> []
        retval = []
        icao_field_errors = self.get_base_node("icao_field_errors")
        if icao_field_errors is None:
            return retval
        for error_record in icao_field_errors:
            retval.append([error_record.attrib['error_message'],
                           int(error_record.attrib['start_index']),
                           int(error_record.attrib['end_index'])])
        return retval

    def get_message_body(self):
        # type: () -> str
        message_body = self.get_base_node("message_body")
        if message_body is None:
            return ""
        return message_body.text

    def get_message_header(self):
        # type: () -> str
        message_header = self.get_base_node("message_header")
        if message_header is None:
            return ""
        return message_header.text

    def get_message_type(self):
        # type: () -> str
        message_type = self.get_base_node("message_type")
        if message_type is None:
            return ""
        return message_type.text

    def get_modification_time(self):
        # type: () -> str
        return self.modification_time

    def get_modification_time_seconds(self):
        # type: () -> float
        return self.modification_time_seconds

    def get_original_message(self):
        # type: () -> str
        original_message = self.get_base_node("original_message")
        if original_message is None:
            return ""
        return original_message.text

    def get_priority_indicator(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.PRIORITY_INDICATOR)

    def get_filing_time(self):
        # type: () -> str
        return self.get_fx(FieldIdentifiers.FILING_TIME)

    def is_message_ok(self):
        return self.message_ok

    def read_message_file(self):
        # type: () -> bool
        # Get the XML tree
        try:
            tree = Et.parse(self.message_file_path)
        except Et.ParseError:
            messagebox.showerror(
                title="Read Message Error - 2",
                message="A valid ATS Message could not be found in the file..." + os.linesep +
                        self.message_file_path + os.linesep +
                        "Ensure the file contents comply with the XML ATS Message file format")
            return False

        # Get the root element in the XML tree
        self.root_element = tree.getroot()

        # Check if there is a valid root element
        if self.root_element is None:
            messagebox.showerror(
                title="Read Message Error - 3",
                message="Cannot fined a valid ATS Message root XML element in the file..." + os.linesep +
                        self.message_file_path + os.linesep +
                        "Ensure the file contents comply with the XML ATS Message file format")
            return False

        # Check if the XML file contains a root element with one expected if it's a 'message' XML file
        if self.root_element.tag != "flight_plan_record":
            messagebox.showerror(
                title="Read Message Error - 4",
                message="Cannot fined a valid ATS Message root XML element in the file..." + os.linesep +
                        self.message_file_path + os.linesep +
                        "Ensure the file contents comply with the XML ATS Message file format")
            return False
        return True

    def get_subfield_fx(self, field_id, subfield_id):
        # type: (FieldIdentifiers, SubFieldIdentifiers) -> str
        icao_fields = self.get_base_node("icao_fields")
        if icao_fields is None:
            return ""
        for icao_field in icao_fields:
            if re.fullmatch(field_id.name, icao_field.attrib["id"]):
                for icao_subfield in icao_field:
                    if re.fullmatch(subfield_id.name, icao_subfield.attrib["id"]):
                        return icao_subfield.text.rstrip(" \n\r")
        return ""

    def get_ers_list_items(self):
        # type: () -> []
        items = []
        ers_node = self.get_ers_node()
        if ers_node is None:
            return ""
        for ers_record in ers_node:
            if re.fullmatch('ers_record', ers_record.tag):
                items.append([
                    ers_record.text,
                    ers_record.attrib['speed'],
                    ers_record.attrib['altitude'],
                    ers_record.attrib['bearing'],
                    ers_record.attrib['distance'],
                    ers_record.attrib['flight_rules'],
                    ers_record.attrib['break_text']
                ])
        return items
