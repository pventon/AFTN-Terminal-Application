import os.path
import re
from datetime import datetime
from tkinter import messagebox
import xml.etree.ElementTree as Et

from Configuration.EnumerationConstants import FieldIdentifiers, SubFieldIdentifiers


class ReadXml:
    """This class reads a message XML file and provides methods to access individual ICAO fields,
    error message and an extracted route sequence in a flight plan message. There is also a
    method to build an ICAO format message from the XML file.
    """

    message_file_path: str = ""
    """Contains a full absolute path and file name for an XML file being read by this class."""

    creation_time: str = ""
    """Contains the XML file creation date/timestamp read from the XML file as a formatted string;"""

    modification_time: str = ""
    """Contains the XML file modification date/timestamp read from the XML file as a formatted string;"""

    creation_time_seconds: float = 0.0
    """Contains the XML file creation date/timestamp read from the XML file in seconds since the epoch,
    (00:00:00 UTC on 1 January 1970);"""

    modification_time_seconds: float = 0.0
    """Contains the XML file modification date/timestamp read from the XML in seconds since the epoch,
    (00:00:00 UTC on 1 January 1970);"""

    root_element = None
    """The root XML element of the XML file being read by this class;"""

    message_ok = False
    """A flag indicating that file opening, XML parsing and presence of a known message XML structure was
    successful;"""

    def __init__(self, message_file_path):
        # type: (str) -> None
        """This constructor opens and reads the XML file given in the 'message_file_path'
        parameter. The file creation and modification time is extracted form the file
        and stored in this class instance. The class method 'read_message_file()' is a helper
        method doing the heavy lifting for reading and checking the file content represents
        a valid ATS message XML file.

        :param message_file_path: The full absolute path and file name for an XML file being
               read by this class.
        """
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
        """This method builds an ICAO format message with the message header (if present) and message body
        by extracting all necessary ICAO fields for a given title from the XML file. This method can be used
        to display a message in the editor dialogue or transmission on the AFTN network.

        :return: A string representing a complete ICAO ATS message.
        """
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
        """This method retrieves the adjacent unit sender identifier/name from the XML file read by
        this class. The field is only present for OLDI messages, very unlikely this field is present
        for ATS messages.

        :return: An adjacent unit identifier/name or an empty string if the XML file does not
        contain a sender adjacent unit identifier/name.
        """
        adjacent_unit_sender = self.get_base_node("adjacent_unit_sender")
        if adjacent_unit_sender is None:
            return ""
        return adjacent_unit_sender.text

    def get_adjacent_unit_receiver(self):
        # type: () -> str
        """This method retrieves the adjacent unit receiver identifier/name from the XML file read by
        this class. The field is only present for OLDI messages, very unlikely this field is present
        for ATS messages.

        :return: An adjacent unit identifier/name or an empty string if the XML file does not
        contain a receiver adjacent unit identifier/name.
        """
        adjacent_unit_receiver = self.get_base_node("adjacent_unit_receiver")
        if adjacent_unit_receiver is None:
            return ""
        return adjacent_unit_receiver.text

    def get_all_errors(self):
        # type: () -> []
        """This method returns a list of all errors in a message XML file, this includes
        both ICAO and field 15 extracted route errors. Each list entry is in itself a list
        containing the following items at the indices shown:
            - Index 0: The error message text;
            - Index 1: The zero based index of the first character of the erroneous field;
            - Index 2: The zero based index of the last character + 1 of the erroneous field;

        :return: A list containing all errors present in the message XML file;
        """
        return self.get_icao_field_errors() + self.get_ers_errors()

    def get_base_node(self, element_name):
        # type: (str) -> Et.Element | None
        """This method returns the XML element that is a child of the XML document root element
        with the name given by the parameter 'element_name'.

        :param element_name: The name of the XML element being retrieved;
        :return: The XML element with a name matching that given in the parameter 'element_name'
                 or 'None' if the element does not exist.
        """
        for child in self.root_element:
            if re.fullmatch(element_name, child.tag):
                return child
        return None

    def get_creation_time(self):
        # type: () -> str
        """This method retrieves the XML file creation date/timestamp as a formatted string;

        :return: A formatted string containing the XML file creation timestamp;
        """
        return self.creation_time

    def get_creation_time_seconds(self):
        # type: () -> float
        """This method retrieves the XML file creation date/timestamp in seconds since the epoch,
        (00:00:00 UTC on 1 January 1970);

        :return: The message creation timestamp as a floating point number representing the number
        of seconds since the epoch;
        """
        return self.creation_time_seconds

    def get_derived_flight_rules(self):
        # type: () -> str
        """This method returns the derived flight rules; this field is populated by the field 15 parser
        that determines the flight rules from the field 15 route semantics.

        :return: A string representing the derived flight rules or an empty string if the derived flight
                 rules are missing;
        """
        derived_flight_rules = self.get_base_node("derived_flight_rules")
        if derived_flight_rules is None:
            return ""
        return derived_flight_rules.text

    def get_ers_errors(self):
        # type: () -> []
        """This method returns a list of the field 15 extracted route errors in a message XML file.
        Each list entry is in itself a list containing the following items at the indices shown:
            - Index 0: The error message text;
            - Index 1: The zero based index of the first character of the erroneous field;
            - Index 2: The zero based index of the last character + 1 of the erroneous field;

        :return: A list containing the field 15 route extraction errors present in the message XML file;
        """
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
        """This method is a helper method to retrieve the XML element whose child nodes are the
        extracted route information.

        :return: The XML element representing the root node of the extracted route information/elements;
        """
        return self.get_base_node("ers")

    def get_ers_records(self):
        # type: () -> []
        """This method is a helper method to retrieve all the ERS child XML elements where each child
        element is an Extracted Route Sequence record.

        :return: A list of ERS XML elements where each list item is an Extracted Route Sequence record
        """
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
        """This method is a helper method to retrieve ICAO field F3;

        :return: ICAO F3 or an empty string if F3 is missing;
        """
        return self.get_fx(FieldIdentifiers.F3)

    def get_f3a(self):
        """This method is a helper method to retrieve ICAO subfield F3a;

        :return: ICAO F3a or an empty string if F3a is missing;
        """
        return self.get_subfield_fx(FieldIdentifiers.F3, SubFieldIdentifiers.F3a)

    def get_f5(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F5;

        :return: ICAO F5 or an empty string if F5 is missing;
        """
        return self.get_fx(FieldIdentifiers.F5)

    def get_f7(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F7;

        :return: ICAO F7 or an empty string if F7 is missing;
        """
        return self.get_fx(FieldIdentifiers.F7)

    def get_f7a(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO subfield F7a;

        :return: ICAO F7a or an empty string if F7a is missing;
        """
        return self.get_subfield_fx(FieldIdentifiers.F7, SubFieldIdentifiers.F7a)

    def get_f8(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F8;

        :return: ICAO F8 or an empty string if F8 is missing;
        """
        return self.get_fx(FieldIdentifiers.F8)

    def get_f9(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F9;

        :return: ICAO F9 or an empty string if F9 is missing;
        """
        return self.get_fx(FieldIdentifiers.F9)

    def get_f9b(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO subfield F9b;

        :return: ICAO F9b or an empty string if F9b is missing;
        """
        return self.get_subfield_fx(FieldIdentifiers.F9, SubFieldIdentifiers.F9b)

    def get_f9c(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO subfield F9c;

        :return: ICAO F9c or an empty string if F9c is missing;
        """
        return self.get_subfield_fx(FieldIdentifiers.F9, SubFieldIdentifiers.F9c)

    def get_f10(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F10;

        :return: ICAO F10 or an empty string if F10 is missing;
        """
        return self.get_fx(FieldIdentifiers.F10)

    def get_f13(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F13;

        :return: ICAO F13 or an empty string if F13 is missing;
        """
        return self.get_fx(FieldIdentifiers.F13)

    def get_f13a(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO subfield F13a;

        :return: ICAO F13a or an empty string if F13a is missing;
        """
        return self.get_subfield_fx(FieldIdentifiers.F13, SubFieldIdentifiers.F13a)

    def get_f13b(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO subfield F13b;

        :return: ICAO F13b or an empty string if F13b is missing;
        """
        return self.get_subfield_fx(FieldIdentifiers.F13, SubFieldIdentifiers.F13b)

    def get_f14(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F14;

        :return: ICAO F14 or an empty string if F14 is missing;
        """
        return self.get_fx(FieldIdentifiers.F14)

    def get_f15(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F15;

        :return: ICAO F15 or an empty string if F15 is missing;
        """
        return self.get_fx(FieldIdentifiers.F15)

    def get_f16(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F16;

        :return: ICAO F16 or an empty string if F16 is missing;
        """
        return self.get_fx(FieldIdentifiers.F16)

    def get_f16a(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO subfield F16a;

        :return: ICAO F16a or an empty string if F16a is missing;
        """
        return self.get_subfield_fx(FieldIdentifiers.F16, SubFieldIdentifiers.F16a)

    def get_f17(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F17;

        :return: ICAO F17 or an empty string if F17 is missing;
        """
        return self.get_fx(FieldIdentifiers.F17)

    def get_f18(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F18;

        :return: ICAO F18 or an empty string if F18 is missing;
        """
        return self.get_fx(FieldIdentifiers.F18)

    def get_f19(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F19;

        :return: ICAO F19 or an empty string if F19 is missing;
        """
        return self.get_fx(FieldIdentifiers.F19)

    def get_f20(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F20;

        :return: ICAO F20 or an empty string if F20 is missing;
        """
        return self.get_fx(FieldIdentifiers.F20)

    def get_f21(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F21;

        :return: ICAO F21 or an empty string if F21 is missing;
        """
        return self.get_fx(FieldIdentifiers.F21)

    def get_f22(self):
        # type: () -> str
        """This method is a helper method to retrieve ICAO field F22;

        :return: ICAO F22 or an empty string if F22 is missing;
        """
        return self.get_fx(FieldIdentifiers.F22)

    def get_fx(self, field_id):
        # type: (FieldIdentifiers) -> str
        """This is a helper method to retrieve any ICAO field specified by an enumeration value
        given in the parameter 'field_id'.

        :param field_id: An enumeration value from the FieldIdentifiers class specifying the
               field identifying the ICAO field to retrieve;
        :return: A string containing the field being retrieved or an empty string if the
                 field does not exist;
        """
        icao_fields = self.get_base_node("icao_fields")
        if icao_fields is None:
            return ""
        for icao_field in icao_fields:
            if re.fullmatch(field_id.name, icao_field.attrib["id"]):
                return icao_field.text.rstrip(" \n\r")
        return ""

    def get_icao_field_errors(self):
        # type: () -> []
        """This method returns a list of the ICAO field errors (excludes the field 15 extracted route
        errors, refer to 'get_ers_errors()' for the extracted route errors.
        Each list entry is in itself a list containing the following items at the indices shown:
            - Index 0: The error message text;
            - Index 1: The zero based index of the first character of the erroneous field;
            - Index 2: The zero based index of the last character + 1 of the erroneous field;

        :return: A list containing the ICAO errors present in the message XML file;
        """
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
        """This method is a helper method to retrieve the message body from the XML file read by this class.

        :return: The message body or an empty string if message body is missing;
        """
        message_body = self.get_base_node("message_body")
        if message_body is None:
            return ""
        return message_body.text

    def get_message_header(self):
        # type: () -> str
        """This method is a helper method to retrieve the message header from the XML file read by this class.

        :return: The message header or an empty string if message header is missing;
        """
        message_header = self.get_base_node("message_header")
        if message_header is None:
            return ""
        return message_header.text

    def get_message_type(self):
        # type: () -> str
        """This method is a helper method to retrieve the message type from the XML file read by this class.

        :return: The message type or an empty string if message type is missing;
        """
        message_type = self.get_base_node("message_type")
        if message_type is None:
            return ""
        return message_type.text

    def get_modification_time(self):
        # type: () -> str
        """This method retrieves the XML file modification date/timestamp as a formatted string;

        :return: A formatted string containing the XML file modification timestamp;
        """
        return self.modification_time

    def get_modification_time_seconds(self):
        # type: () -> float
        """This method retrieves the XML file modification date/timestamp in seconds since the epoch,
        (00:00:00 UTC on 1 January 1970);

        :return: The message modification timestamp as a floating point number representing the number
        of seconds since the epoch;
        """
        return self.modification_time_seconds

    def get_original_message(self):
        # type: () -> str
        """This method is a helper method to retrieve the message originator from the XML file read by this class.

        :return: The message originator or an empty string if message originator is missing;
        """
        original_message = self.get_base_node("original_message")
        if original_message is None:
            return ""
        return original_message.text

    def get_priority_indicator(self):
        # type: () -> str
        """This method is a helper method to retrieve the message priority indicator from the XML
        file read by this class.

        :return: The message priority indicator or an empty string if message priority indicator is missing;
        """
        return self.get_fx(FieldIdentifiers.PRIORITY_INDICATOR)

    def get_filing_time(self):
        # type: () -> str
        """This method is a helper method to retrieve the message filing time from the XML
        file read by this class.

        :return: The message filing time or an empty string if message filing time is missing;
        """
        return self.get_fx(FieldIdentifiers.FILING_TIME)

    def is_message_ok(self):
        # type: () -> bool
        """This method returns a flag indicating if the XML file was successfully read by this class.

        :return: True if the XML file could be read and contained a valid application ATS XML message format,
                 False otherwise;
        """
        return self.message_ok

    def read_message_file(self):
        # type: () -> bool
        """This method reads a message XML file and checks for the following:

            - Can the message be opened and read by the 'Et' XML parser;
            - Does the message contain a valid and recognised XML root element (flight_plan_record)

        Message boxes are displayed to the user should any of the checks fail.

        :return: True if the XML file is a valid and recognised application message XML file, False
        otherwise.
        """
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
        """This is a helper method to retrieve any ICAO subfield specified by the enumeration values
        given in the parameters 'field_id' and 'subfield_id'.

        :param field_id: An enumeration value from the FieldIdentifiers class specifying the
               field identifying the ICAO field to retrieve;
        :param subfield_id: An enumeration value from the SubFieldIdentifiers class specifying the
               subfield identifying the ICAO subfield to retrieve;
        :return: A string containing the subfield being retrieved or an empty string if the
                 subfield does not exist;
        """
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
        """This method retrieves a list of Extracted Route Sequence records from the extracted route
        derived by the field 15 parser. Not all the extracted route record fields are retrieved, a
        small subset is retrieved and used to display the ERS in the ERS dialogue window.
        Each list item returned by this method is a list containing the following fields:

            - Speed: This is the speed as given in field 15 at a point, e.g. N0450;
            - Altitude: This is the altitude as given in field 15 at a point, e.g. F250;
            - Bearing: The azimuth between two points, (only present if two consecutive points
                       are given as latitude/longitude values) given as a decimal angle;
            - Distance: The distance between two points in meters as a decimal value, (only
                        present if two consecutive points are given as latitude/longitude values);
            - Flight Rules: Flight rules assigned to an extracted route item;
            - Break Text: This is text following a point where IFR rules have been cancelled;

        :return: A list of extracted route records;
        """
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
