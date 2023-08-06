"""PJScript BooleanLiteral"""

from .base import BaseLiteral


class BooleanLiteral(BaseLiteral):

    """BooleanLiteral class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate BooleanLiteral"""

        return f'(new BooleanPrimitive((char*)"{self.token().value()}"))' + self._semicolon(top)
