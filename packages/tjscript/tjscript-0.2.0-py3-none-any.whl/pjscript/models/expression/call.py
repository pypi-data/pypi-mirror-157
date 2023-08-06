"""PJScript CallExpression"""

# pylint: disable=line-too-long  # it complains about last lines

from typing import List
from pjscript.models.expression.base import BaseExpression
from pjscript.models.literal.identifier import IdentifierLiteral
from pjscript.models.base import BaseModel


class CallExpression(BaseExpression):

    """CallExpression class"""

    _instantiation: bool  # whether call expression should return object instance, or just a result?
    _name: IdentifierLiteral
    _args: List[BaseModel]

    def __init__(self, instantiation: bool, name: IdentifierLiteral, args: List[BaseModel]) -> None:

        """Instantiate CallExpression"""

        self._instantiation = instantiation
        self._name = name
        self._args = args

    def instantiation(self) -> bool:

        """Returns CallExpression instantiation flag"""

        return self._instantiation

    def name(self) -> IdentifierLiteral:

        """Returns CallExpression name"""

        return self._name

    def args(self) -> list:

        """Returns CallExpression args"""

        return self._args

    def to_dict(self) -> dict:

        """Returns dict representation"""

        return {
            "class": self.__class__.__name__,
            "instantiation": self.instantiation(),
            "name": self.name().to_dict(),
            "args": [arg.to_dict() for arg in self.args()]
        }

    def __repr__(self) -> str:

        """Debugging simplified"""

        return self.__str__()

    def __str__(self) -> str:

        """Custom serializer for CallExpression child classes written in order to simplify debugging"""

        inst = 'instantiation' if self.instantiation() else 'no-instantiation'  # <- instantiation flag
        class_name = self.__class__.__name__  # <--------------- get the actual name of a derived class

        return f'{class_name}' \
               f'(<{inst}>, {self.name()}, [{", ".join(map(str, self.args()))if self.args() else ""}])'
