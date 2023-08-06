"""PJScript StringLiteral"""

from .base import BaseLiteral


class StringLiteral(BaseLiteral):

    """StringLiteral class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate StringLiteral"""

        return f'(new StringPrimitive((char*)"{self.token().value()}"))' + self._semicolon(top)
