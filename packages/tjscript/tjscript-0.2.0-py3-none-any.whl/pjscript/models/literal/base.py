"""PJScript BaseLiteral"""

from pjscript.models.base import BaseModel
from pjscript.syntax.token import Token


class BaseLiteral(BaseModel):

    """BaseLiteral class"""

    _token: Token

    def __init__(self, token: Token) -> None:

        """Instantiate BaseLiteral"""

        self._token = token

    def token(self) -> Token:

        """Returns BaseLiteral token"""

        return self._token

    def to_dict(self) -> dict:

        """Returns dict representation"""

        return {
            "class": self.__class__.__name__,
            "value": self.token().value()
        }

    def __repr__(self) -> str:

        """Debugging simplified"""

        return self.__str__()

    def __str__(self) -> str:

        """Custom __str__() to simplify debugging"""

        value = f'"{self.token().value()}"' \
            if self.token().is_string() \
            else self.token().value()

        return f'{self.__class__.__name__}({value})'
