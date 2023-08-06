"""PJScript ProgramExpression"""

from typing import List, Tuple
from pjscript.models.expression.base \
    import BaseExpression
from pjscript.models.base import BaseModel


class ProgramExpression(BaseExpression):

    """ProgramExpression class"""

    _body: List[BaseModel]

    def __init__(self, body: List[BaseModel]) -> None:

        """Instantiate ProgramExpression"""

        self._body = body

    def body(self) -> List[BaseModel]:

        """Returns ProgramExpression body"""

        return self._body

    def to_dict(self) -> dict:

        """Returns dict representation"""

        return {
            "class": 'ProgramExpression',
            "body": [expression.to_dict() for expression in self.body()]
        }

    def ctxs(self, name: str) -> Tuple[str, str]:

        """Generate .{h,c}pp contexts"""

        include = '#include "runtime/cxx/pjscript.hpp"'
        signature = f'void {name}( Environment* _env )'

        return f'{include}\n{signature};\n', \
               f'{include}\n{signature}{{\n{self.generate()}}}'

    def generate(self, top: bool = False, **opts) -> str:

        """Generate ProgramExpression"""

        return '\n'.join(map(lambda ex: ex.generate(True), self.body()))

    def __repr__(self) -> str:

        """Debugging simplified"""

        return self.__str__()

    def __str__(self) -> str:

        """Custom ProgramExpression serializer was written with the aim to simplify debugging"""

        return f'ProgramExpression([{", ".join(map(str, self.body())) if self.body() else ""}])'
