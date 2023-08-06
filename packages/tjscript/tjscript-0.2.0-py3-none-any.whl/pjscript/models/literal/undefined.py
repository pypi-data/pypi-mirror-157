"""PJScript UndefinedLiteral"""

from .base import BaseLiteral


class UndefinedLiteral(BaseLiteral):

    """UndefinedLiteral class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate UndefinedLiteral"""

        return '(new UndefinedPrimitive())' + self._semicolon(top)
