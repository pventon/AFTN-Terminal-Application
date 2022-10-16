import re

from Configuration.EnumerationConstants import MessageTypes, MessageTitles, AdjacentUnits, ErrorId, FieldIdentifiers
from Configuration.ErrorMessages import ErrorMessages
from Configuration.FieldsInMessage import FieldsInMessage
from Configuration.SubFieldsInFields import SubFieldsInFields
from Configuration.SubFieldDescriptions import SubFieldDescriptions
from Configuration.MessageDescription import MessageDescription
from IcaoMessageParser.FlightPlanRecord import FlightPlanRecord
from IcaoMessageParser.ParseAdditionalAddressee import ParseAdditionalAddressee
from IcaoMessageParser.ParseAddressee import ParseAddressee
from IcaoMessageParser.ParseF3 import ParseF3
from IcaoMessageParser.ParseFieldsCommon import ParseFieldsCommon
from IcaoMessageParser.ParseFilingTime import ParseFilingTime
from IcaoMessageParser.ParseOriginator import ParseOriginator
from IcaoMessageParser.ParsePriorityIndicator import ParsePriorityIndicator
from IcaoMessageParser.Utils import Utils
from Tokenizer.Tokenize import Tokenize, Tokens


# This class is the entry point for parsing complete ICAO messages for both ATS
# and OLDI messages. The parser is able to automatically evaluate if a message
# contains a header or not. For ICAO ATS message the data definitions are set up
# as a single data set; for OLDI messages the definitions vary depending on an
# adjacent unit sending identifier.
# The entry point method is 'parse_message()' that takes an instance of FlightPlanRecord
# and a string containing the message to parse.
# The FlightPlanRecord is populated by the parser and includes all extracted fields,
# an extracted route if field 15 was present and any errors. It is a callers
# responsibility to retrieve the errors.
# If this software is used in conjunction with a GUI, all the fields are stored with
# their zero based index into the message so that erroneous fields can be
# highlighted in the GUI. This makes message correction quite simple for end users.
# Note: Eventually this parser will also support ADEXP message parsing; currently
# an error is reported when an ADEXP message is encountered.
# This class is thread safe and can be used simultaneously on multiple threads.
# This class includes the message field list definitions (the configuration data
# for the parser) by instantiating the MessageDescriptions class and assigning
# this the MCD member of this class.
class ParseMessage:
    # Minimum length of header text, anything less than this is considered
    # junk and added to the message body.
    MINIMUM_HEADER_LENGTH: int = 20

    # Minimum message length under which a message is considered junk
    # and no attempt made to parse it further. The shortest message
    # is a LAM, LAML/E012E/L001 -> 15 characters minimum.
    MINIMUM_BODY_LENGTH: int = 12

    # Configuration data defining the fields in a message for all message titles
    FIM: FieldsInMessage = FieldsInMessage()

    # Configuration data mapping ICAO fields to their respective subfields
    SFIF: SubFieldsInFields = SubFieldsInFields()

    # Configuration data providing subfield syntax definitions & other data
    SFD: SubFieldDescriptions = SubFieldDescriptions()

    # Configuration data containing all the error messages
    EM: ErrorMessages = ErrorMessages()

    # This method determines the message type (ICAO ATS, OLDI or ADEXP) based on
    # a message title.
    # Arguments
    # ---------
    # f3:       A string containing a message title;
    # return:   An enumeration from MessageDescriptions.MessageTypes;
    #           if the title is undefined / not supported then
    #           MessageDescriptions.MessageTypes.UNKNOWN is returned.
    @staticmethod
    def determine_message_type(f3):
        # type: (str) -> MessageTypes
        if len(f3) < 3:
            # Cannot be a message title, too short, error
            return MessageTypes.UNKNOWN

        message_title = Utils.title_defined(f3[0:3])
        if message_title is None:
            # Title is not supported, error
            return MessageTypes.UNKNOWN

        if message_title.value > MessageTitles.SPL.value:
            return MessageTypes.OLDI

        return MessageTypes.ATS

    # This method gets the field list for a message based on its title, adjacent unit
    # name and message type. The field list contains a list of ICAO fields that must
    # be included in a message and is used by the field parsers to parse individual subfields.
    # The field list is an instance of the MessageDescription class.
    # Arguments
    # ---------
    # flight_plan_record:   The Flight Plan Record containing the message to parse
    #                       and into which all the parsed data is written;
    #                       The name of an adjacent unit or DEFAULT if no name is defined
    #                       for the message title being processed.
    # message_title:        The message title of the message being processed
    # return:               An instance the MessageDescription class containing a list
    #                       of all fields expected in a given message or None if a suitable
    #                       field list could not be found. The latter case should never
    #                       happen and most likely indicates an error in the configuration
    #                       data.
    def get_message_description(self, flight_plan_record, message_title):
        # type: (FlightPlanRecord, MessageTitles) -> MessageDescription | None

        md = self.FIM.get_message_content(flight_plan_record.get_message_type(),
                                          flight_plan_record.get_sender_adjacent_unit_name(), message_title)
        if md is None:
            # If we land here then data configuration is missing
            # for the combination Message Type -> Adjacent Unit -> Message Title
            # It is a data configuration error, we can add an error
            Utils.add_error(
                flight_plan_record,
                "Message Type: " + flight_plan_record.get_message_type().name +
                ", Adjacent Unit Name: " + flight_plan_record.get_sender_adjacent_unit_name().name +
                ", Message Title: " + message_title.name +
                ". Default configuration will be used.",
                0, 0, self.EM, ErrorId.SYSTEM_CONFIG_UNDEFINED)
            # Let's check if we can proceed with the default adjacent unit before we give up
            md = self.FIM.get_message_content(flight_plan_record.get_message_type(),
                                              AdjacentUnits.DEFAULT, message_title)
            if md is None:
                # Shit out of luck, cannot proceed
                Utils.add_error(
                    flight_plan_record,
                    "Message Type: " + flight_plan_record.get_message_type().name +
                    ", Adjacent Unit Name: " + AdjacentUnits.DEFAULT.name +
                    ", Message Title: " + message_title.name +
                    ". No default configuration available, message cannot be processed.",
                    0, 0, self.EM, ErrorId.SYSTEM_CONFIG_UNDEFINED)
            else:
                # We have a default definition, proceed with this
                flight_plan_record.set_sender_adjacent_unit_name(AdjacentUnits.DEFAULT)
                return md
            return None
        return md

    # This method carries out some rudimentary checks for:
    # - A 'null' message
    # - An empty message
    # - A short message (less than MINIMUM_HEADER_LENGTH characters is treated
    #   as an erroneous case)
    # Any of the erroneous cases result in an error being written to the
    # Flight Plan Record.
    # Arguments
    # ---------
    # flight_plan_record:   A flight plan record into which errors are written
    # message:              The message being parsed
    # return:               False if errors are detected, True otherwise
    def is_message_valid(self, flight_plan_record, message):
        # type: (FlightPlanRecord, str) -> bool
        # Do some very basic checks to make sure we have a valid message
        if message is None:
            # Null message value
            flight_plan_record.add_erroneous_field(
                "Null Field", self.EM.get_error_message(ErrorId.MSG_EMPTY), 0, 0)
            flight_plan_record.set_message_type(MessageTypes.UNKNOWN)
            return False
        if len(message) < 1:
            # Is an empty string
            Utils.add_error(flight_plan_record, message, 0, 0, self.EM, ErrorId.MSG_EMPTY)
            flight_plan_record.set_message_type(MessageTypes.UNKNOWN)
            return False
        if len(message) < self.MINIMUM_BODY_LENGTH:
            # Is way too short
            Utils.add_error(flight_plan_record, message, 0, len(message), self.EM, ErrorId.MSG_TOO_SHORT)
            flight_plan_record.set_message_type(MessageTypes.UNKNOWN)
            return False
        return True

    # TODO Eventually a separate ADEXP parser will be added, for now this format is not supported
    def parse_adexp(self, flight_plan_record):
        # type: (FlightPlanRecord) -> bool
        # Currently ADEXP messages are not supported, we report an error
        Utils.add_error(flight_plan_record, "ADEXP Not Supported", 0, 0, self.EM, ErrorId.MSG_ADEXP_NOT_SUPPORTED)
        return False

    # Parses an ICAO ATS message; when this method is called the following is known:
    # - The message type is ICAO ATS (MessageTypes.ATS)
    # - The message title is valid but the MessageTitle enumeration must be obtained
    # - As it's an ATS message, there is no adjacent unit identifier needed
    # To obtain the appropriate field list for the message title the following are needed:
    # - MessageTypes.ATS enumeration - Recover from the flight plan record
    # - MessageTitles.<Title enumeration> - This method will get this from the message title
    # - AdjacentUnit.DEFAULT - The default adjacent unit definition is used as there is
    #   no adjacent unit for ATS messages
    # Arguments
    # ---------
    # flight_plan_record:   The Flight Plan Record containing the message to parse;
    # return:               True if a supported message title could be identified.
    #                       False if any errors were detected.
    def parse_ats(self, flight_plan_record):
        # type: (FlightPlanRecord) -> bool

        # Tokenize the message, open & closed brackets will be removed
        tokens = self.tokenize_message(flight_plan_record, "()-\r\n\t")

        # Get the message title enumeration
        message_title = Utils.title_defined(
            tokens.get_first_token().get_token_string().replace(" ", "")[0:3])

        return self.parse_ats_or_oldi(
            flight_plan_record, tokens, message_title)

    # This class parses an OLDI message. The difference between an ATS and OLDI
    # message is that the field list, i.e. the content of a given message based
    # on its title, varies depending on the adjacent unit that a message is being
    # exchanged on.
    # This method calls the F3 parser which establishes the adjacent unit from
    # F3b and sets this in the FPR. The 'standard' ATS parser is then called which
    # uses the adjacent unit to obtain the correct field content definition.
    def parse_oldi(self, flight_plan_record):
        # type: (FlightPlanRecord) -> bool

        # Tokenize the message, open & closed brackets will be removed
        tokens = self.tokenize_message(flight_plan_record, "()-\r\n\t")

        # Get the message title enumeration
        message_title = Utils.title_defined(
            tokens.get_first_token().get_token_string().replace(" ", "")[0:3])

        # For OLDI messages we need to establish the adjacent unit sender name
        # To do this we must assume that the first token is F3a and at least F3b.
        # F3b contains the sender unit name. If we parse F3 it will set the
        # adjacent unit name into the FPR so that the appropriate field list can be
        # obtained for the OLDI title/unit.
        # Set F3 to the FPR
        flight_plan_record.add_icao_field(FieldIdentifiers.F3,
                                          tokens.get_first_token().get_token_string(),
                                          tokens.get_first_token().get_token_start_index(),
                                          tokens.get_first_token().get_token_end_index())
        # Parse F3, this will assign the adjacent unit name to the FPR
        ParseF3(flight_plan_record, self.SFIF, self.SFD).parse_field()

        return self.parse_ats_or_oldi(flight_plan_record, tokens, message_title)

    # This method parses an ATS header and saves the fields to the FPR.
    # The header parsing assumes correct message syntax, that is the fields are expected
    # in the following order:
    # <Priority Indicator> <One or more Addressees> <Filing Time> <Originator> <One or more Additional Addressees>
    # The header is tokenized and the appropriate parser called on the fields in the expected
    # order. If fields are missing and/or extra, an error is reported as are any syntax errors.
    # Arguments
    # ---------
    # flight_plan_record:   Flight plan record containing the header field and where
    #                       successfully parsed fields will be written to.
    # return:               True if parsing was successful, false if errors are detected.
    def parse_ats_header(self, flight_plan_record):
        # type: (FlightPlanRecord) -> bool

        # Tokenize the header
        tokenize = Tokenize()
        tokenize.set_string_to_tokenize(flight_plan_record.get_message_header())
        tokenize.set_whitespace(" \n\t\r")
        tokenize.tokenize()
        tokens: Tokens = tokenize.get_tokens()

        # Return if there is nothing in the header
        if tokens.get_number_of_tokens() < 1:
            return True

        # Some kind of header is present and ready for parsing, create empty fields in the FPR
        flight_plan_record.add_icao_field(FieldIdentifiers.PRIORITY_INDICATOR, "", 0, 0)
        flight_plan_record.add_icao_field(FieldIdentifiers.ADDRESS, "", 0, 0)
        flight_plan_record.add_icao_field(FieldIdentifiers.FILING_TIME, "", 0, 0)
        flight_plan_record.add_icao_field(FieldIdentifiers.ORIGINATOR, "", 0, 0)
        flight_plan_record.add_icao_field(FieldIdentifiers.ADADDRESS, "", 0, 0)

        # The following is used to indicate the 'state' of processing:
        # 0 -> Next expected header field is the Priority Indicator
        # 1 -> Next expected header field is an addressee field
        # 2 -> Next expected header field is the Originator
        # 3 -> Next expected header field is an additional addressee
        next_field: int = 0
        additional_addressee_available = False
        # Loop over the header fields
        for token in tokens.get_tokens():
            if next_field == 0:  # Process priority indicator

                # Save the Priority Indicator
                flight_plan_record.add_icao_field(FieldIdentifiers.PRIORITY_INDICATOR,
                                                  token.get_token_string(),
                                                  token.get_token_start_index(),
                                                  token.get_token_end_index())

                # Set up a new token for the addressee field(s)
                flight_plan_record.add_icao_field(
                    FieldIdentifiers.ADDRESS,
                    flight_plan_record.get_icao_field(FieldIdentifiers.ADDRESS).get_field_text(),
                    token.get_token_end_index() + 1,
                    token.get_token_end_index() + 1)

                # Indicates the next field is an addressee
                next_field = 1

            elif next_field == 1:  # Process addressee
                if Utils.get_first_digit_index(token.get_token_string()) == 0:
                    # Have to assume a field starting with a digit is the filing time
                    # Save the Filing Time
                    flight_plan_record.add_icao_field(FieldIdentifiers.FILING_TIME,
                                                      token.get_token_string(),
                                                      token.get_token_start_index(),
                                                      token.get_token_end_index())

                    # Indicate next field to process is the originator
                    next_field = 2

                else:
                    # Concatenate the addressees
                    flight_plan_record.add_icao_field(
                        FieldIdentifiers.ADDRESS,
                        flight_plan_record.get_icao_field(
                            FieldIdentifiers.ADDRESS).get_field_text() + token.get_token_string() + " ",
                        flight_plan_record.get_icao_field(FieldIdentifiers.ADDRESS).get_start_index(),
                        token.get_token_end_index())

            elif next_field == 2:  # Process the originator

                # Save the Originator
                flight_plan_record.add_icao_field(FieldIdentifiers.ORIGINATOR,
                                                  token.get_token_string(),
                                                  token.get_token_start_index(),
                                                  token.get_token_end_index())

                # Set up a new token for the additional addressee field(s)
                flight_plan_record.add_icao_field(
                    FieldIdentifiers.ADADDRESS,
                    flight_plan_record.get_icao_field(FieldIdentifiers.ADADDRESS).get_field_text(),
                    token.get_token_end_index() + 1,
                    token.get_token_end_index() + 1)

                next_field = 3

            elif next_field == 3:  # Process additional addressees

                # Concatenate the additional addressees
                flight_plan_record.add_icao_field(
                    FieldIdentifiers.ADADDRESS,
                    flight_plan_record.get_icao_field(
                        FieldIdentifiers.ADADDRESS).get_field_text() + token.get_token_string() + " ",
                    flight_plan_record.get_icao_field(FieldIdentifiers.ADADDRESS).get_start_index(),
                    token.get_token_end_index())
                additional_addressee_available = True

        ParsePriorityIndicator(flight_plan_record, self.SFIF, self.SFD).parse_field()
        ParseAddressee(flight_plan_record, self.SFIF, self.SFD).parse_field()
        ParseFilingTime(flight_plan_record, self.SFIF, self.SFD).parse_field()
        ParseOriginator(flight_plan_record, self.SFIF, self.SFD).parse_field()
        if additional_addressee_available:
            ParseAdditionalAddressee(flight_plan_record, self.SFIF, self.SFD).parse_field()

        return flight_plan_record.errors_detected()

    # This method determines parses the message fields. The field definition list
    # is obtained based on the message type, adjacent unit name and message title.
    # the field definition list contains information about all the subfields in each
    # field and is used to parse individual subfields.
    # the individual parser methods are implemented as callbacks and stored with the
    # field definition list. Each parser callback adds the fields and subfields to the FPR.
    # Once this method completes, The FPR is fully populated with the message field and
    # subfield content.
    # Arguments
    # ---------
    # flight_plan_record:   The Flight Plan Record containing the message to parse
    #                       and into which all the parsed data is written;
    # return:               True if the message was parsed without error, false
    #                       if any errors were detected.
    def parse_ats_or_oldi(self, flight_plan_record, tokens, message_title):
        # type: (FlightPlanRecord, Tokens, MessageTitles) -> bool

        # Obtain the field list definition for this message title
        md: MessageDescription = self.get_message_description(flight_plan_record, message_title)

        # Check that a valid field list is defined
        if md is None:
            return False

        # Get the list of field parsers defined for this message
        field_parsers: [ParseFieldsCommon] = md.get_field_parsers()

        # Get the list of field identifiers defining fields included in this message
        field_identifiers: [FieldIdentifiers] = md.get_message_fields()

        # Loop over the fields in the list of tokens, (these are the fields to
        # be parsed), by calling a parse method defined for each field.
        # The list of fields to parse and the list of fields defined
        # for this messages should be the same size, but if a field is missing or
        # there are additional fields, then the lists will not match. The 'smallest'
        # list is used to control the loop and avoid accessing invalid list entries;
        # if the lists differ in size an error is reported.
        idx = 0
        if tokens.get_number_of_tokens() < md.get_number_of_fields_in_message():
            # There are fewer fields to parse than fields defined for this message
            for token in tokens.get_tokens():
                # Save the field to be parsed to the flight plan
                flight_plan_record.add_icao_field(field_identifiers[idx],
                                                  token.get_token_string(),
                                                  token.get_token_start_index(),
                                                  token.get_token_end_index())
                fp = field_parsers[idx](flight_plan_record, self.SFIF, self.SFD)
                # Parse the field
                fp.parse_field()
                idx += 1

            # Check if fewer fields to parse is allowed, some messages have optional fields
            difference = md.get_number_of_fields_in_message() - tokens.get_number_of_tokens()
            if message_title == MessageTitles.FPL and difference == 1:
                # This title has an optional field 19, we only report an error if more
                # than one field is missing
                return flight_plan_record.errors_detected()
            Utils.add_error(flight_plan_record, str(md.get_number_of_fields_in_message()),
                            tokens.get_first_token().get_token_start_index(),
                            tokens.get_last_token().get_token_end_index(), self.EM,
                            ErrorId.MSG_TOO_FEW_FIELDS)
        else:
            # Either the fields to parse are equal to those defined, or we have more
            # fields in the message than defined for the messages
            for field_parser in field_parsers:
                # Save the field to be parsed to the flight plan
                flight_plan_record.add_icao_field(field_identifiers[idx],
                                                  tokens.get_token_at(idx).get_token_string(),
                                                  tokens.get_token_at(idx).get_token_start_index(),
                                                  tokens.get_token_at(idx).get_token_end_index())
                fp = field_parser(flight_plan_record, self.SFIF, self.SFD)
                # Parse the field
                fp.parse_field()
                idx += 1

            # Check if we have more fields to parse than defined for this message
            if tokens.get_number_of_tokens() > md.get_number_of_fields_in_message():
                Utils.add_error(flight_plan_record, tokens.get_token_at(idx).get_token_string(),
                                tokens.get_token_at(idx).get_token_start_index(),
                                tokens.get_token_at(idx).get_token_end_index(), self.EM,
                                ErrorId.MSG_TOO_MANY_FIELDS)

        return flight_plan_record.errors_detected()

    # This method is the entry point for message parsing; the method takes an
    # instance of FlightPlanRecord (for output) and a string containing
    # the message to parse.
    # The FlightPlanRecord is populated by the parser and includes all
    # extracted fields, if field 15 was present along with any route
    # extraction any errors. It is a callers responsibility to retrieve the
    # errors.
    # Arguments
    # ---------
    # flight_plan_record:   A flight plan record into which all data extracted
    #                       by the parser (including errors) are written
    # message:              The message with or without header
    # return:               False if errors are detected, True otherwise
    def parse_message(self, flight_plan_record, message):
        # type: (FlightPlanRecord, str | None) -> bool

        # Check if the message is worthy of further processing
        if not self.is_message_valid(flight_plan_record, message):
            return False

        # Save the complete message to the FPR
        flight_plan_record.set_message_complete(message)

        # Split and save the message header and body
        self.set_message_body_and_header(flight_plan_record)

        # Go into more detail and establish the message type;
        # (ICAO ATS, OLDI or ADEXP). The message type is stored in the FPR.
        if not self.set_message_type(flight_plan_record):
            return False

        # Call the appropriate parser
        match flight_plan_record.get_message_type():
            case MessageTypes.ADEXP:
                self.parse_ats_header(flight_plan_record)
                return self.parse_adexp(flight_plan_record)
            case MessageTypes.ATS:
                self.parse_ats_header(flight_plan_record)
                return self.parse_ats(flight_plan_record)
            case MessageTypes.OLDI:
                self.parse_oldi_header(flight_plan_record)
                return self.parse_oldi(flight_plan_record)
            case MessageTypes.UNKNOWN:
                return False

    @staticmethod
    def parse_oldi_header(flight_plan_record):
        # type: (FlightPlanRecord) -> bool
        if flight_plan_record.get_message_body() == "":
            return True
        return True

    # This method determines if a message contains a header and message body or
    # if it's a message without a header.
    # The message header and body are copied to the FPR if they are present.
    # Differentiating between the message header and body is achieved by
    # detecting the presence or not of the first hyphen or open bracket in a message.
    # The action taken is as per the following truth table:
    #            Open      Hyphen
    #  Hyphen | Bracket |  Before |
    # Present | Present | Bracket | Action
    # --------+---------+---------+--------------------------------------------
    #    No   |    No   |    x    | Save to message body + Process, no header
    # --------+---------+---------+--------------------------------------------
    #    No   |   Yes   |    x    | Split on Bracket, save to body and header + Process
    # --------+---------+---------+--------------------------------------------
    #   Yes   |    No   |    x    | Split on Hyphen, save to body and header + Process
    # --------+---------+---------+--------------------------------------------
    #   Yes   |   Yes   |   No    | Split on Bracket, save to body and header + Process
    # --------+---------+---------+--------------------------------------------
    #   Yes   |   Yes   |  Yes    | Split on Hyphen, save to body and header + Process
    # --------+---------+---------+--------------------------------------------
    # Arguments
    # ----------
    # flight_plan_record:   The Flight Plan Record containing the message to parse;
    # return:               True if the message header and body have been identified
    #                       and stored, False if any errors were detected.
    def set_message_body_and_header(self, flight_plan_record):
        # type: (FlightPlanRecord) -> None
        msg = flight_plan_record.get_message_complete()

        # Get the indices of the two characters that could indicate the start
        # of the message body.
        hyphen_index = msg.find("-", 0, len(msg))
        open_b_index = msg.find("(", 0, len(msg))

        # Take action as described in the table for this methods' documentation.
        if hyphen_index < 0 and open_b_index < 0:
            # Hyphen and Bracket Missing
            # A LAM has no hyphen, and if a message was submitted without a bracket, then...
            # Row 1 of the table in the comments
            flight_plan_record.set_message_header("")
            flight_plan_record.set_message_body(msg)
        elif (hyphen_index < 0 and open_b_index > -1) or \
                ((hyphen_index > -1 and open_b_index > -1) and open_b_index < hyphen_index):
            # (Hyphen missing, open bracket present) or
            # ((Hyphen and bracket present) and Bracket before Hyphen)
            # Rows 2 & 4 of the table in the comments
            # Split on bracket
            if open_b_index < self.MINIMUM_HEADER_LENGTH:
                flight_plan_record.set_message_header("")
                flight_plan_record.set_message_body(msg)
            else:
                flight_plan_record.set_message_header(msg[0:open_b_index])
                flight_plan_record.set_message_body(msg[open_b_index:])
        else:
            # (Hyphen present, open bracket missing) or
            # ((Hyphen and bracket present) and Hyphen before Bracket)
            # Rows 3 & 5 of the table in the comments
            # Split on hyphen
            if hyphen_index < self.MINIMUM_HEADER_LENGTH:
                # Safe to assume there is no header
                flight_plan_record.set_message_header("")
                flight_plan_record.set_message_body(msg)
            else:
                flight_plan_record.set_message_header(msg[0:hyphen_index])
                flight_plan_record.set_message_body(msg[hyphen_index:])

    # This method sets the message type (ICAO ATS, OLDI or ADEXP) to the FPR.
    # When this method is called, the FPR contains a message body and maybe
    # a header (if the message included a header).
    # This method recovers the message title from the start of the message body,
    # and checks if it is a supported message title. Using the title, the message
    # type can be ascertained and set with one of the enumeration values from
    # the MessageDescriptions.MessageTypes class.
    # Arguments
    # ---------
    # flight_plan_record:   The Flight Plan Record containing the message to parse;
    # return:               True if a supported message title could be identified.
    #                       False if any errors were detected.
    def set_message_type(self, flight_plan_record):
        # type: (FlightPlanRecord) -> bool
        msg_body = flight_plan_record.get_message_body()
        msg_header = flight_plan_record.get_message_header()

        # If we can find the '-TITLE' in some shape or form at the start
        # of the field, we must have an ADEXP message.
        # Regexp is for e.g '   -   TITLE' -> whitespace irrelevant
        if re.match("[ \n\r\t]*-[ \n\r\t]*TITLE", msg_body) is not None:
            # We have an ADEXP message
            Utils.add_error(flight_plan_record, "", 0, 0, self.EM, ErrorId.MSG_ADEXP_NOT_SUPPORTED)
            flight_plan_record.set_message_type(MessageTypes.ADEXP)
            return False

        # Try and locate an ATS message title, first attempt with a bracket
        # Regexp is for e.g '   (   FPL' Bracket is optional, whitespace irrelevant
        f3 = re.match("[ \n\r\t]*[(]?[ \n\r\t]*[A-Z]{3}", msg_body)
        if f3 is None:
            # Message title not recognised, error, grab the first three characters
            m = re.match(".{3}", msg_body)
            Utils.add_error(flight_plan_record, m.group(0),
                            len(msg_header) + m.span()[1] - 3,
                            len(msg_header) + m.span()[1], self.EM, ErrorId.F3_TITLE_SYNTAX)
            flight_plan_record.set_message_type(MessageTypes.UNKNOWN)
            return False

        # Store the indices for future error reporting.
        end_index = len(msg_header) + f3.span()[1]
        start_index = end_index - 3

        # We have a possible ATS message, extract the message title
        f3 = re.findall("[A-Z]{3}", f3.group(0))
        if f3 is not None:
            # Try and figure out the message type
            message_type = self.determine_message_type(f3[0])
            if message_type is MessageTypes.UNKNOWN:
                # Unrecognised message title
                Utils.add_error(flight_plan_record, f3[0], start_index, end_index + 3,
                                self.EM, ErrorId.F3_TITLE_SYNTAX)
                flight_plan_record.set_message_type(MessageTypes.UNKNOWN)
                return False
            else:
                # Title recognized
                # One more check to do, some message titles are the same for
                # OLDI and ATS messages. OLDI messages always include F3b & F3c.
                # Regexp is for e.g '   (   ACPAA/BB001' Bracket is optional, whitespace irrelevant
                mm = re.match("[ \n\r\t]*[(]?[ \n\r\t]*[A-Z]{3,7}/[A-Z]{1,4}[0-9]{1,3}", msg_body)
                message_title = Utils.title_defined(f3[0])
                if (message_title is MessageTitles.ACP or message_title is MessageTitles.CDN or
                        message_title is MessageTitles.CPL) and mm is not None:
                    flight_plan_record.set_message_type(MessageTypes.OLDI)
                else:
                    flight_plan_record.set_message_type(message_type)
                return True
        else:
            # This should never ever happen
            Utils.add_error(flight_plan_record, "Regexp went wrong", 0, 0, self.EM, ErrorId.F3_TITLE_SYNTAX)
            flight_plan_record.set_message_type(MessageTypes.UNKNOWN)
            return False

    # This method tokenizes a field or message, any string passed to it.
    @staticmethod
    def tokenize_message(flight_plan_record, whitespace):
        # type: (FlightPlanRecord, str) -> Tokens
        tokenizer = Tokenize()
        tokenizer.set_string_to_tokenize(flight_plan_record.get_message_body())
        tokenizer.set_whitespace(whitespace)
        tokenizer.tokenize()
        return tokenizer.get_tokens()
