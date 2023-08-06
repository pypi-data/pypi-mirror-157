"""PJScript Parser"""

# pylint: disable=line-too-long
# pylint: disable=wildcard-import

from typing import List, Tuple
from pjscript.syntax.token import \
    Token, Span
from pjscript.models import \
    BaseModel, \
    CallExpression, AssignmentExpression
from pjscript.models.literal import *
from pjscript.models.expression import *


class Parser:  # pylint: disable=too-few-public-methods  # it's okay to have only one: `parsed()`

    """Parser makes AST based on passed tokens"""

    _errors: List[str]
    _warnings: List[str]
    _tokens: List[Token]
    _program_ast: ProgramExpression
    _last_semicolon_token_span: Span

    def __init__(self, tokens: List[Token]) -> None:

        """Instantiate Parser"""

        self._errors = []
        self._warnings = []
        self._tokens = tokens
        self._parse()

    def parsed(self) -> ProgramExpression:

        """Returns program expression instance"""

        return self._program_ast

    def _expressions(
            self,
            tokens: List[Token] = None
    ) -> List[List[Token]]:

        """Returns tokens grouped by a semicolon token"""

        if tokens is None:
            tokens = self._tokens

        groups = []

        idx = 0
        while idx < len(tokens):
            # TODO: this algorithm is stupid and should be improved!
            if tokens[idx].is_opening_curly_bracket():
                while idx < len(tokens):
                    idx += 1
                    if tokens[idx].is_closing_curly_bracket():
                        idx += 1
                        break
            if tokens[idx].is_semicolon():
                self._last_semicolon_token_span = tokens[idx].span()
                groups.append(tokens[:idx])
                tokens = tokens[idx + 1:]
                idx = 0
            else:
                idx += 1

        return groups

    @staticmethod
    def _args_by(tokens, cond) -> List[List[Token]]:

        """Returns tokens grouped by a some token"""

        groups = []
        group = []

        idx = 0
        while idx < len(tokens):
            if cond(tokens[idx]):
                groups.append(group)
                group = []
                tokens = tokens[idx + 1:]
                idx = 0
            else:
                group.append(tokens[idx])
                idx += 1

        # we do not want to lose last argument expression from the ExpressionCall' arguments list
        if group:
            groups.append(group)

        return groups

    @staticmethod
    def _find_preferred_operator(tokens: List[Token]) -> Tuple[int, str]:

        """Returns most preferred operator (as string) and its index in tokens list"""

        # TODO: for some reason PyCharm complains about '*found' types, but code **should** and **does** work

        sub_found: Tuple[Tuple[int, Token]]
        sub_found = tuple(filter(lambda p: p[1].is_sub_operator(), enumerate(tokens)))               # stupid
        if not sub_found:
            add_found: Tuple[Tuple[int, Token]]
            add_found = tuple(filter(lambda p: p[1].is_add_operator(), enumerate(tokens)))           # stupid
            if not add_found:
                div_found: Tuple[Tuple[int, Token]]
                div_found = tuple(filter(lambda p: p[1].is_div_operator(), enumerate(tokens)))       # stupid
                if not div_found:
                    mul_found: Tuple[Tuple[int, Token]]
                    mul_found = tuple(filter(lambda p: p[1].is_mul_operator(), enumerate(tokens)))   # stupid
                    assert mul_found,     f'{tokens[0].span()}: no valid arithmetical operator found, a bug?'
                    return mul_found[0][0], BinaryExpression.Mul  # <----- return found '*' operator position
                return div_found[0][0], BinaryExpression.Div  # <--------- return found '/' operator position
            return add_found[0][0], BinaryExpression.Add  # <------------- return found '+' operator position
        return sub_found[0][0], BinaryExpression.Sub  # <----------------- return found '-' operator position

    @staticmethod
    def _contains_arithmetical_operator_token(tokens: List[Token]) -> bool:

        """Returns whether tokens list contains at least one arithmetical operator"""

        return bool(tuple(filter(lambda token: token.is_arithmetical_operator(), tokens)))

    def _parse_call_expression(self, tokens: List[Token], instantiation: bool) -> CallExpression:

        """Returns parsed CallExpression (ObjectCallExpression, MemberCallExpression) instance"""

        name, start = (IdentifierLiteral(tokens[1]), 2)if instantiation else(IdentifierLiteral(tokens[0]), 1)

        args = [self._parse_expression(tokens) for tokens in self._args_by(tokens[start + 1:len(tokens) - 1],
                                                                           # separate arguments by coma token
                                                                           lambda token:    token.is_coma())]

        # TODO: in JS, we can also express Member*Expression by 'foo . bar', so we need to improve this logic

        payload = instantiation, name, args

        return MemberCallExpression(*payload) if name.token().has_a_dot() else ScopedCallExpression(*payload)

    def _parse_assignment_expression(self, tokens: List[Token]) -> AssignmentExpression:

        """Returns parsed AssignmentExpression instance"""

        mutable, tokens = \
            (tokens[0].value() == 'var', tokens[1:]) if tokens[0].is_mutability_keyword() else (True, tokens)

        assert len(tokens) >= 3, f'{tokens[0].span().formatted()}: incorrect arity for assignment expression'

        lhs = IdentifierLiteral(tokens[0])
        rhs = self._parse_expression(tokens[2:])  # <-- skip over assignment operator, if empty -> raises err

        return MemberAssignmentExpression(mutable, lhs, rhs) \
            if tokens[0].has_a_dot() \
            else ScopedAssignmentExpression(mutable, lhs, rhs)   # <--- dispatch between two Assignment types

    def _parse_function_expression(self, tokens: List[Token]) -> FunctionExpression:

        """Returns parsed FunctionExpression"""

        closing_bracket_index = 0
        for (idx,
             token) in enumerate(tokens):
            if token.is_closing_bracket():
                closing_bracket_index = idx  # <--- find closing bracket token index or set it to 0 otherwise

        # TODO: we need also check whether each group contains only one regular identifier, and *fail* if not

        assert closing_bracket_index, f'{tokens[0].span()}: function: unable to find nearest closing bracket'

        params = [IdentifierLiteral(t[0])
                  for t in self._args_by(tokens[2:closing_bracket_index], lambda t: t.is_coma())]    # params

        expressions = self._expressions(tokens[closing_bracket_index + 2:len(tokens) - 1])   # fn expressions

        body = [self._parse_expression(raw) for raw in expressions[:-1]]   # <------- construct function body

        # return;
        #      ^
        # return ...;
        #      ^

        if expressions[-1][0].is_return_keyword():
            returns = (self._parse_expression(expressions[-1][1:]))  # <----- parse function return statement
        else:
            returns = None  # <--------------------------- if there is no return statement, set it to nullptr

        return FunctionExpression(params, body, returns)  # <-------------- return parsed function expression

    def _parse_binary_expression(self, tokens: List[Token]) -> BinaryExpression:

        """Returns parsed BinaryExpression"""

        # TODO: improve assertion, we should not allow nothing at the start/end, but literals and identifiers

        assert not tokens[0].is_arithmetical_operator() \
               and not tokens[-1].is_arithmetical_operator(),  f'{tokens[0].span()}: wrong expression syntax'

        index, operator = self._find_preferred_operator(tokens)  # <------------ find most preferred operator
        lhs = self._parse_expression(tokens[:index])  # <------------------- recursively parse left-hand-side
        rhs = self._parse_expression(tokens[index + 1:])  # <-------------- recursively parse right-hand-side
        return BinaryExpression(operator, lhs, rhs)  # <------------- return parsed BinaryExpression instance

    def _parse_expression(self, tokens: List[Token]) -> BaseModel:  # pylint: disable=R0911  # it's okay, bro

        """Returns either a parsed expression or a parsed literal instance"""

        assert tokens, f'{(self._last_semicolon_token_span - 1).formatted()}: can not parse empty expression'

        # TODO: implement matching instead of manual guessing what kind of expression we should parse->return

        # null;
        # null keyword

        if len(tokens) == 1 and tokens[0].is_null_keyword():
            return NullLiteral(tokens[0])  # <------------------------- parse 'null' keyword as a NullLiteral

        # "string";
        # string literal

        if len(tokens) == 1 and tokens[0].is_string():
            return StringLiteral(tokens[0])  # <----------------------- parse string token as a StringLiteral

        # true;
        # false;
        # boolean keyword

        if len(tokens) == 1 and tokens[0].is_boolean_keyword():
            return BooleanLiteral(tokens[0])  # <-------- parse ('true', 'false') keyword as a BooleanLiteral

        # undefined keyword

        if len(tokens) == 1 and tokens[0].is_undefined_keyword():
            return UndefinedLiteral(tokens[0])  # <-------------------------------- parse as UndefinedLiteral

        # Object;
        # foo.bar;
        # single identifier

        if len(tokens) == 1 and tokens[0].is_regular_identifier():  # it's needed for a secondary else branch

            if tokens[0].has_a_dot():  # <-- 'has_a_dot()' already checks that it's just a regular identifier
                return MemberAccessExpression(IdentifierLiteral(tokens[0]))  # <- parse as a MemberAccessExpr
            return ScopedAccessExpression(IdentifierLiteral(tokens[0]))  # <----- parse as a ScopedAccessExpr

        # new Object;
        #   ^      ^
        # new Object();
        #   ^      ^~~

        if tokens[0].is_new_keyword() and tokens[1].is_regular_identifier():
            return self._parse_call_expression(tokens,    instantiation=True)  # <-- parse instantiation call

        # Object();
        #      ^^^
        # console.log("Hello", "World", "!");
        #           ^^~~~~~~~~~~~~~~~~~~~~~^

        if tokens[0].is_regular_identifier() \
                and tokens[1].is_opening_bracket() and tokens[-1].is_closing_bracket():
            return self._parse_call_expression(tokens,    instantiation=False)  # <------- parse regular call

        # foo = "foo";
        #   ^ ^ ..... ...
        # var bar = "bar";
        #   ^   ^ ^ ..... ...
        # const xyz = bar;
        #     ^   ^ ^ ... ...

        if (len(tokens) >= 3  # pylint: disable=too-many-boolean-expressions  # might consider refactor this?
            and tokens[0].is_regular_identifier()
            and tokens[1].is_assignment_operator()) \
                or (len(tokens) >= 4
                    and tokens[0].is_mutability_keyword()
                    and tokens[1].is_regular_identifier()
                    and tokens[2].is_assignment_operator()):
            return self._parse_assignment_expression(tokens)  # <------------- parse an assignment expression

        # function() {};
        #        ^^   ^
        # function(a, b) {};
        #        ^^      ^
        # function() {...};
        #        ^^      ^
        # function(a, b) {...};
        #        ^^          ^

        if tokens[0].is_function_keyword() and len(tokens) >= 5 \
                and tokens[1].is_opening_bracket() and tokens[-1].is_closing_curly_bracket():
            return self._parse_function_expression(tokens)  # <-------------------- parse function expression

        # "foo" + "bar" * "xyz";
        #       ^       ^

        if len(tokens) >= 3 and self._contains_arithmetical_operator_token(tokens):
            return self._parse_binary_expression(tokens)   # if there is at least *one* arithmetical operator

        raise SyntaxError(f'{tokens[0].span().formatted()}: it does not match any known expression pattern!')

    def _parse(self) -> None:

        """Takes list of tokens and produces ProgramExpression (AST) instance based on 'recursive parsing'"""

        self._program_ast = ProgramExpression([self._parse_expression(expr) for expr in self._expressions()])
