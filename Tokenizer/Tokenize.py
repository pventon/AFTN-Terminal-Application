from Tokenizer.Tokens import Tokens


class Tokenize:
    """This class tokenizes a string looking for tokens separated by caller specified
    whitespace characters, storing each token along with its location where it was
    found in the input string (a tokens start and end index in the source string). The
    individual tokens along with their associated attributes are stored in a 'Tokens'
    class instance. """

    string_to_tokenize: str = ""
    """The input string containing the tokens to be extracted"""

    whitespace: str = ""
    """Whitespace token delimiter characters"""

    tokens: Tokens = Tokens()
    """List of extracted tokens"""

    def __init__(self):
        """Constructor without a string to tokenize and assigning a default whitespace string
        regular expressions \" \\\\n\\\\t\\\\r\".

            :return: None"""
        self.string_to_tokenize = ""
        self.tokens = Tokens()
        self.whitespace = " \n\t\r"

    def tokenize(self):
        # type: () -> None
        """Tokenize the string using the assigned whitespace character set. Any character contained
        in the parameter 'whitespace' will be discarded and treated as whitespace token separators
        apart from a forward slash '/' which will result in a forward slash token.
        A string given as "E1 E2 E3" will yield 3 tokens using the default whitespace character set.

            :return: None"""
        self.tokens = Tokens()
        idx = 0
        token_text = ""
        for item in self.string_to_tokenize:
            if item in self.whitespace:
                if len(token_text) > 0:
                    self.__save_token(token_text, idx)
                if item in "/":
                    # We have to save the forward slash token
                    self.__save_token(item, idx+1)
                token_text = ""
            else:
                token_text = token_text + item
            idx = idx + 1

        self.__save_token(token_text, idx)

    def set_string_to_tokenize(self, string_to_tokenize=""):
        # type: (str) -> None
        """Sets a string to tokenize

            :param string_to_tokenize: A string that will be tokenized by this class;
            :return: None"""
        self.string_to_tokenize = string_to_tokenize

    def get_string_to_tokenize(self):
        # type: () -> str
        """Retrieves the string that has been tokenized.

            :return: The string that was tokenized;"""
        return self.string_to_tokenize

    def set_whitespace(self, whitespace=""):
        # type: (str) -> None
        """Set a string representing the token whitespace delimiter characters.

        Note that a forward slash '/' character will be treated as whitespace
        but will be saved as a token. All other whitespace characters are
        consumed by the tokenizer.

            :param whitespace:  The string containing characters considered as
                                whitespace when tokenizing;
            :return: None"""
        self.whitespace = whitespace

    def get_whitespace(self):
        # type: () -> str
        """Retrieve the string representing the token whitespace delimiter characters.

            :return: A string containing characters treated as whitespace characters;"""
        return self.whitespace

    def get_tokens(self):
        # type: () -> Tokens
        """Retrieve the list of tokens stored in this class.

            :return: A list containing zero or more Token classes"""
        return self.tokens

    def __save_token(self, token_text, idx):
        # type: (str, int) -> None
        """Save a token to a local token attribute.

            :param token_text: Saves the token_text to a token at index idx;
            :param idx: The index identifying a token in the list of tokens;
            :return: None"""
        if len(token_text) > 0:
            self.tokens.create_append_token(
                token_text, idx - len(token_text), idx)
