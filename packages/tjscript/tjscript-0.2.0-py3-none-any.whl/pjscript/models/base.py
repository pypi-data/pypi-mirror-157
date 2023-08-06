"""PJScript BaseModel"""

# pylint: disable=R0903


class BaseModel:

    """BaseModel class"""

    def to_dict(self) -> dict:

        """Returns dict representation"""

    @staticmethod
    def _semicolon(top: bool) -> str:

        """Returns ; if expression/literal on top"""

        return ';' if top else ''

    def generate(self, top: bool = False, **opts) -> str:

        """Generate C++ for some expression or literal"""
