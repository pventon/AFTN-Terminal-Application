class ErrorMessages:
    """This class contains a list of error messages in a dictionary with each error message indexed by
    an integer value. The errors listed here are all the error messages used by the field 15 parser."""
    error_messages = {
        0: "ERROR UNDEFINED",
        1: "The first Field 15 element must be a SPEED/LEVEL and not '!'",
        2: "A SPEED/LEVEL element cannot be followed by '!', (i.e. point or SID?)",
        3: "The element '!' is an unrecognised Field 15 element",
        4: "Element '!' is too long for a Field 15 Element",
        5: "Expecting '/' before '!'",
        6: "No VFR section preceding this '!' rule change indicator",
        7: "No OAT section preceding this '!' rule change indicator",
        8: "No IFPSTART preceding this '!' indicator",
        9: "Expecting 'C/POINT/' before '!'",
        10: "Expecting the keyword 'STAY' before '!'",
        11: "'/' not expected preceding '!'",
        12: "Expecting a PRP after an ATS route instead of '!'",
        13: "Rule change '!' cannot occur following an ATS route element",
        14: "Cannot go direct ('!') from an ATS route element, must be preceded by a point",
        15: "'!' must be preceded by a point",
        16: "'!' cannot follow a '/'",
        17: "Expecting SPEED/LEVEL, SPEED/VFR or cruise climb point name after '/' instead of '!'",
        18: "Expecting cruise climb point name before '!'",
        19: "Expecting end of field 15 after truncation indicator 'T' instead od '!'",
        20: "Field 15 is incomplete, expecting additional data after the final '!'",
        21: "A 'DCT' must be followed by a point instead of '!'",
        22: "Expecting '/SPEED/LEVEL' following '!' to complete rule change to IFR",
        23: "The first SPEED/LEVEL cannot be followed by the element '!'",
        24: "Expecting SID or DPF after first SPEED/LEVEL element instead of '!'",
        25: "Field 15 cannot end with the '!' element",
        26: "Expecting '/' after cruise / climb 'C/POINT' instead of '!'",
        27: "Expecting point / speed / altitude / altitude after start of Cruise/Climb indicator 'C/!'",
        28: "Expecting speed / altitude / altitude after start of Cruise/Climb indicator 'C/!/'",
        29: "Expecting Cruise/Climb 'SPEED/ALTITUDE/ALTITUDE' or 'SPEED/ALTITUDE/PLUS' instead of '!'",
        30: "SID '!' must follow the first SPEED/ALTITUDE and cannot appear anywhere else in field 15",
        31: "The SID must be followed by a point or STAR, cannot be followed with '!'",
        32: "The SID cannot be followed by another SID '!'",
        33: "A SID or STAR ('!') must be the first or last tokens in a field 15",
        34: "A STAR must be the last element in field 15 and cannot be followed with '!'",
        35: "Expecting STAY time as '/HHMM' after '!'",
        36: "Expecting forward slash '/' after STAY instead of '!'",
        37: "Time value as HHMM token missing after '!'",
        38: "Expecting HHMM token following STAYx/ element",
        39: "'!' Cannot follow a STAY/HHMM' element",
        40: "The flight level '!' must end in a zero or 5",
        41: "Field 15 is empty",
        42: "Latitude degree value must be 0 to 90 instead of '!'",
        43: "Latitude degree/minute value must be 0 to 9000 with minutes < 60 instead of '!'",
        44: "Longitude degree value must be 0 to 180 instead of '!'",
        45: "Longitude degree/minute value must be 0 to 18000 with minutes < 60 instead of '!'",
        46: "Bearing degree value must be 0 to 360 instead of '!'",
        47: "ATS route '!' cannot follow a Lat/Long point",
        48: "Lat/Long '!' cannot follow an ATS route",
        49: "Field 15 contains no route description",
        50: "Expecting SPEED/LEVEL or SPEED/VFR after '/' instead of '!'",
        52: "Expecting point / speed / altitude / altitude after start of Cruise/Climb indicator 'C!'",
        53: "Add crossing point between previous ATS route and '!'",
        54: "Add APF between previous ATS route and STAR '!'",
        55: "The SPEED/LEVEL '!' cannot follow an ATS route",
        56: ""
    }
