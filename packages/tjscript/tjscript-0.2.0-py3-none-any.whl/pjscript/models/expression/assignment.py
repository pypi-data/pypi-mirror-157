"""PJScript AssignmentExpression"""

# pylint: disable=duplicate-code  # for Assignment, Binary

from pjscript.models.expression.base import BaseExpression
from pjscript.models.literal.identifier import IdentifierLiteral
from pjscript.models.base import BaseModel


class AssignmentExpression(BaseExpression):

    """AssignmentExpression class"""

    _mutable: bool
    _lhs: IdentifierLiteral
    _rhs: BaseModel

    def __init__(self, mutable: bool, lhs: IdentifierLiteral, rhs: BaseModel) -> None:

        """Instantiate AssignmentExpression"""

        self._mutable = mutable
        self._lhs = lhs
        self._rhs = rhs

    def mutable(self) -> bool:

        """Returns AssignmentExpression mutability flag"""

        return self._mutable

    def lhs(self) -> IdentifierLiteral:

        """Returns AssignmentExpression left-hand-side"""

        return self._lhs

    def rhs(self) -> BaseModel:

        """Returns AssignmentExpression right-hand-side"""

        return self._rhs

    def to_dict(self) -> dict:

        """Returns dict representation"""

        return {
            "class": self.__class__.__name__,
            "mutable": self.mutable(),
            "lhs": self.lhs().to_dict(), "rhs": self.rhs().to_dict()
        }

    def __repr__(self) -> str:

        """Debugging simplified"""

        return self.__str__()

    def __str__(self) -> str:

        """Custom Assignment serializer was made with the aim to simplify debugging"""

        mutable = 'mutable' if self.mutable() else 'non-mutable'  # <-- 'mutable' flag

        return f'{self.__class__.__name__}(<{ mutable }>, {self.lhs()}, {self.rhs()})'
