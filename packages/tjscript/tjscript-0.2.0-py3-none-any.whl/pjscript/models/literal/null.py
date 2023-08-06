"""PJScript NullLiteral"""

from .base import BaseLiteral


class NullLiteral(BaseLiteral):

    """NullLiteral class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate NullLiteral"""

        return '(new NullPrimitive())' + self._semicolon(top)
