"""PJScript Span and Token"""


class Span:

    """Span represents a Token position in a source code"""

    _line_no: int
    _char_no: int

    def __init__(self, line_no: int, char_no: int) -> None:

        """Instantiate Span"""

        self._line_no = line_no
        self._char_no = char_no

    def line(self) -> int:

        """Returns line number"""

        return self._line_no

    def char(self) -> int:

        """Returns character number"""

        return self._char_no

    def tuple(self) -> tuple:

        """Returns span as a tuple"""

        return self._line_no, self._char_no

    def formatted(self) -> str:

        """Returns span as a string"""

        return ':'.join(map(str, self.tuple()))

    def __sub__(self, char_no: int) -> "Span":

        """Returns new Span with a char_no decremented"""

        return Span(self.line(), self._char_no - char_no)


class Token:      # pylint: disable=too-many-public-methods

    """Token represents some part of the language syntax"""

    Coma = 'Coma'
    Operator = 'Operator'
    Semicolon = 'Semicolon'
    OpeningBracket = 'OpeningBracket'
    ClosingBracket = 'ClosingBracket'
    OpeningCurlyBracket = 'OpeningCurlyBracket'
    ClosingCurlyBracket = 'ClosingCurlyBracket'
    String = 'String'
    Identifier = 'Identifier'

    _kind: str
    _value: str
    _span: Span

    def __init__(self, kind: str, value: str, span: Span) -> None:

        """Instantiate Token"""

        self._kind = kind
        self._value = value
        self._span = span

    def kind(self) -> str:

        """Returns token kind"""

        return self._kind

    def value(self) -> str:

        """Returns token value"""

        return self._value

    def span(self) -> Span:

        """Returns token span"""

        return self._span

    def is_coma(self) -> bool:

        """Returns whether token is coma"""

        return self._kind == self.Coma

    def is_operator(self) -> bool:

        """Returns whether token is operator"""

        return self._kind == self.Operator

    def is_add_operator(self) -> bool:

        """Returns whether token is add operator"""

        return self.is_operator() and self._value == '+'

    def is_sub_operator(self) -> bool:
        """Returns whether token is sub operator"""

        return self.is_operator() and self._value == '-'

    def is_mul_operator(self) -> bool:

        """Returns whether token is mul operator"""

        return self.is_operator() and self._value == '*'

    def is_div_operator(self) -> bool:

        """Returns whether token is div operator"""

        return self.is_operator() and self._value == '/'

    def is_arithmetical_operator(self) -> bool:

        """Returns whether token is arithmetic operator"""

        return (self.is_add_operator()
                or self.is_sub_operator()
                or self.is_mul_operator()
                or self.is_div_operator())

    def is_assignment_operator(self) -> bool:

        """Returns whether token is assignment operator"""

        return self.is_operator() and self._value == '='

    def is_semicolon(self) -> bool:

        """Returns whether token is semicolon"""

        return self._kind == self.Semicolon

    def is_opening_bracket(self) -> bool:

        """Returns whether token is opening bracket"""

        return self._kind == self.OpeningBracket

    def is_closing_bracket(self) -> bool:

        """Returns whether token is closing bracket"""

        return self._kind == self.ClosingBracket

    def is_opening_curly_bracket(self) -> bool:

        """Returns whether token is opening curly bracket"""

        return self._kind == self.OpeningCurlyBracket

    def is_closing_curly_bracket(self) -> bool:

        """Returns whether token is closing curly bracket"""

        return self._kind == self.ClosingCurlyBracket

    def is_string(self) -> bool:

        """Returns whether token is string"""

        return self._kind == self.String

    def is_identifier(self) -> bool:

        """Returns whether token is identifier"""

        return self._kind == self.Identifier

    def is_keyword(self) -> bool:

        """Returns whether token is keyword"""

        return (self.is_new_keyword()
                or self.is_null_keyword()
                or self.is_boolean_keyword()
                or self.is_mutability_keyword()
                or self.is_function_keyword()
                or self.is_return_keyword()
                or self.is_undefined_keyword())

    def is_new_keyword(self) -> bool:

        """Returns whether token is new keyword"""

        return self.is_identifier() and self._value == 'new'

    def is_null_keyword(self) -> bool:

        """Returns whether token is null keyword"""

        return self.is_identifier() and self._value == 'null'

    def is_boolean_keyword(self) -> bool:

        """Returns whether token is boolean keyword"""

        return self.is_identifier() and self._value in ['true',
                                                        'false']

    def is_mutability_keyword(self) -> bool:

        """Returns whether token is mutability keyword"""

        return self.is_identifier() and self._value in ['var',
                                                        'const']

    def is_function_keyword(self) -> bool:

        """Returns whether token is function keyword"""

        return self.is_identifier() and self._value == 'function'

    def is_return_keyword(self) -> bool:

        """Returns whether token is return keyword"""

        return self.is_identifier() and self._value == 'return'

    def is_undefined_keyword(self) -> bool:

        """Returns whether token is undefined keyword"""

        return self.is_identifier() and self._value == 'undefined'

    def is_regular_identifier(self) -> bool:

        """Returns whether token is regular identifier"""

        return self.is_identifier() \
            and not self.is_keyword() and not self.is_operator()

    def has_a_dot(self) -> bool:

        """Returns whether token value has a dot character"""

        return self.is_regular_identifier() and '.' in self._value

    def __repr__(self) -> str:

        """Debugging simplified"""

        return self.__str__()

    def __str__(self) -> str:

        """Custom serializer helps to simplify debugging process"""

        value = self.value() \
            if not self.is_string() else f'"{self.value()}"'

        return f'[{self.span().formatted()} {self.kind()}] {value}'
