"""PJScript Lexer"""

import re
from typing import List
from pjscript.syntax.token import Token, Span

ALPHABET = re.compile(r'[a-zA-Z]')   # matches all the English letters


class Lexer:  # pylint: disable=too-few-public-methods  # it's okay :)

    """Lexer takes source code string, and returns a list of tokens"""

    _source: str
    _pointer: int = 0
    _line_no: int = 1
    _char_no: int = 1
    _tokens: List[Token]

    def __init__(self, source: str) -> None:

        """Instantiate Lexer"""

        self._source = source
        self._tokens = []
        self._lex()

    def lexed(self) -> List[Token]:

        """Returns the list of tokens"""

        return self._tokens

    def _advance_and_increment_char_no(self) -> None:

        """Advances the pointer and increments the character number"""

        self._pointer += 1
        self._char_no += 1

    def _advance_and_increment_line_no_then_also_reset_line_no(self) -> None:

        """Advances the pointer, resets 'char_no' and increments 'line_no'"""

        self._pointer += 1
        self._char_no = 1
        self._line_no += 1

    def _span(self) -> Span:

        """Returns current span state"""

        return Span(self._line_no, self._char_no)

    def _has_next_symbol(self) -> bool:

        """Returns whether source code has next symbol"""

        return self._pointer < len(self._source)

    def _next_symbol(self) -> str:

        """Returns next symbol"""

        return self._source[self._pointer + 1]

    def _current_symbol(self) -> str:

        """Returns current symbol"""

        return self._source[self._pointer]

    def _current_symbol_is_newline(self) -> bool:

        """Returns whether current symbol is newline"""

        return self._current_symbol() == '\n'

    def _current_symbol_is_coma(self) -> bool:

        """Returns whether current symbol is coma"""

        return self._current_symbol() == ','

    def _current_symbol_is_operator(self) -> bool:

        """Returns whether current symbol is operator"""

        return self._current_symbol() in ['+', '-', '*', '/',
                                          '=']

    def _current_symbol_is_semicolon(self) -> bool:

        """Returns whether current symbol is semicolon"""

        return self._current_symbol() == ';'

    def _current_symbol_is_opening_bracket(self) -> bool:

        """Returns whether current symbol is opening bracket"""

        return self._current_symbol() == '('

    def _current_symbol_is_closing_bracket(self) -> bool:

        """Returns whether current symbol is closing bracket"""

        return self._current_symbol() == ')'

    def _current_symbol_is_opening_curly_bracket(self) -> bool:

        """Returns whether current symbol is opening curly bracket"""

        return self._current_symbol() == '{'

    def _current_symbol_is_closing_curly_bracket(self) -> bool:

        """Returns whether current symbol is closing curly bracket"""

        return self._current_symbol() == '}'

    def _current_symbol_is_double_quote(self) -> bool:

        """Returns whether current symbol is double quote"""

        return self._current_symbol() == '"'

    def _current_symbol_is_single_quote(self) -> bool:

        """Returns whether current symbol is single quote"""

        return self._current_symbol() == "'"

    def _current_symbol_is_character(self) -> bool:

        """Returns whether current symbol is character"""

        return re.match(ALPHABET, self._current_symbol()) is not None \
            or self._current_symbol() in ['.', '_']

    def _lex(self) -> None:  # pylint: disable=too-many-branches

        """Lex a source code"""

        while self._has_next_symbol():

            if (self._current_symbol() == '/'
                    and self._has_next_symbol()
                    and self._next_symbol() == '/'):
                self._advance_and_increment_char_no()
                while self._has_next_symbol():
                    if self._current_symbol_is_newline():
                        break
                    self._advance_and_increment_char_no()  # // ......

            if (self._current_symbol() == '/'
                    and self._has_next_symbol()
                    and self._next_symbol() == '*'):
                self._advance_and_increment_char_no()
                while self._has_next_symbol():
                    if (self._current_symbol() == '*'
                            and self._has_next_symbol()
                            and self._next_symbol() == '/'):
                        # TODO: also match newline inside of a comment
                        self._advance_and_increment_char_no()   # skip
                        self._advance_and_increment_char_no()   # skip
                        break
                    self._advance_and_increment_char_no()  # /* ... */

            elif self._current_symbol_is_coma():
                self._tokens.append(Token(
                    Token.Coma, self._current_symbol(), self._span()))
                self._advance_and_increment_char_no()

            elif self._current_symbol_is_operator():
                self._tokens.append(Token(
                    Token.Operator, self._current_symbol(), self._span()))
                self._advance_and_increment_char_no()

            elif self._current_symbol_is_semicolon():
                self._tokens.append(Token(
                    Token.Semicolon, self._current_symbol(), self._span()))
                self._advance_and_increment_char_no()

            elif self._current_symbol_is_opening_bracket():
                self._tokens.append(Token(
                    Token.OpeningBracket, self._current_symbol(), self._span()))
                self._advance_and_increment_char_no()

            elif self._current_symbol_is_closing_bracket():
                self._tokens.append(Token(
                    Token.ClosingBracket, self._current_symbol(), self._span()))
                self._advance_and_increment_char_no()

            elif self._current_symbol_is_opening_curly_bracket():
                self._tokens.append(Token(
                    Token.OpeningCurlyBracket,
                    self._current_symbol(),
                    self._span()
                ))
                self._advance_and_increment_char_no()

            elif self._current_symbol_is_closing_curly_bracket():
                self._tokens.append(Token(
                    Token.ClosingCurlyBracket,
                    self._current_symbol(),
                    self._span()
                ))
                self._advance_and_increment_char_no()

            elif self._current_symbol_is_double_quote():
                value = ""
                while self._has_next_symbol():
                    self._advance_and_increment_char_no()
                    if not self._current_symbol_is_double_quote():
                        value += self._current_symbol()
                    else:
                        break
                self._tokens.append(Token(Token.String, value, self._span()))
                self._advance_and_increment_char_no()

            elif self._current_symbol_is_single_quote():
                value = ""
                while self._has_next_symbol():
                    self._advance_and_increment_char_no()
                    if not self._current_symbol_is_single_quote():
                        value += self._current_symbol()
                    else:
                        break
                self._tokens.append(Token(Token.String, value, self._span()))
                self._advance_and_increment_char_no()

            elif self._current_symbol_is_character():
                value = self._current_symbol()
                while self._has_next_symbol():
                    self._advance_and_increment_char_no()
                    if self._current_symbol_is_character():
                        value += self._current_symbol()
                    else:
                        break
                self._tokens.append(Token(Token.Identifier, value, self._span()))
                # don't advance pointer when reached end of identifier definition

            else:
                if self._current_symbol_is_newline():
                    self._advance_and_increment_line_no_then_also_reset_line_no()
                else:
                    self._advance_and_increment_char_no()  # skip over separators
