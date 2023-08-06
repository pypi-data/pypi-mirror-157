"""PJScript IdentifierLiteral"""

from .base import BaseLiteral


class IdentifierLiteral(BaseLiteral):

    """IdentifierLiteral class"""

    def generate(self, top: bool = False, **opts):

        """Generate "IdentifierLiteral"""

        return f'(char*)"{self.token().value()}"' + self._semicolon(top)
