"""PJScript FunctionExpression"""

# pylint: disable=line-too-long  # it complains about last lines

from typing import List
from pjscript.models.expression.base import BaseExpression
from pjscript.models.literal.identifier import IdentifierLiteral
from pjscript.models.base import BaseModel


class FunctionExpression(BaseExpression):

    """FunctionExpression class"""

    _parameters: List[IdentifierLiteral]
    _body: List[BaseModel]
    _returns: BaseModel

    def __init__(self,
                 parameters: List[IdentifierLiteral],
                 body: List[BaseModel],
                 returns: BaseModel) -> None:

        """Instantiate FunctionExpression"""

        self._parameters = parameters
        self._body = body
        self._returns = returns

    def parameters(self) -> List[IdentifierLiteral]:

        """Returns FunctionExpression parameters"""

        return self._parameters

    def body(self) -> list:

        """Returns FunctionExpression body"""

        return self._body

    def returns(self) -> BaseModel:

        """Return FunctionExpression return expression"""

        return self._returns

    def to_dict(self) -> dict:

        """Returns dict representation"""

        return {
            "class": 'FunctionExpression',
            "parameters": [param.to_dict() for param in self.parameters()],
            "body": [expr.to_dict() for expr in self.body()],
            "returns": self.returns().to_dict()
        }

    def generate(self, top: bool = False, **opts) -> str:

        """Generate FunctionExpression"""

        body = 'Object* _new = new Object();\n' \
               '_new->set((char*)"this", _new, false);\n'

        if self._returns:
            ret = f'return ({  self._returns.generate(emv = "_new")  })->some();'
        else:
            ret = 'return (new UndefinedPrimitive())-some();'    # default retval

        for each in self.body():
            body += f'{each.generate(env="_new")};\n'  # <------ make expressions

        body += '_new->del((char*)"this");\n'  # <----------------- delete "this"

        body += f'if ($is_instantiation)\n' \
                f'    return _new->some();\n' \
                f'{ret}'  # <--------------------- detect return value in runtime

        return f'[_](ArgsType args, bool $is_instantiation) {{\n' \
               f'{body}' \
               f'}}' + self._semicolon(top)  # <--0- generated FunctionExpression

    def __repr__(self) -> str:

        """Debugging simplified"""

        return self.__str__()

    def __str__(self) -> str:

        """Custom serializer for FunctionExpression made to simplify debugging"""

        parameters_formatted = ', '.join(map(str, self.parameters()))    # params
        body_formatted = ', '.join(map(str, self.body()))  # formatted body and ^

        return f'FunctionExpression [{parameters_formatted}] [{body_formatted}])'
