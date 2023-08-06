"""PJScript AccessExpression"""

from pjscript.models.expression.base \
    import BaseExpression
from pjscript.models.literal.identifier \
    import IdentifierLiteral


class AccessExpression(BaseExpression):

    """AccessExpression class"""

    _name: IdentifierLiteral

    def __init__(self, name: IdentifierLiteral) -> None:

        """Instantiate AccessExpression"""

        self._name = name

    def name(self) -> IdentifierLiteral:

        """Returns AccessExpression name"""

        return self._name

    def to_dict(self) -> dict:

        """Returns dict representation"""

        return {
            "class": self.__class__.__name__,
            "name": self.name().to_dict()
        }

    def __repr__(self) -> str:

        """Debugging simplified"""

        return self.__str__()

    def __str__(self) -> str:

        """Custom serializer made to simplify debugging"""

        return f'{self.__class__.__name__}({self.name()})'
