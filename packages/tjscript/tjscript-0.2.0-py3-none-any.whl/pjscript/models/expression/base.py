"""PJScript BaseExpression"""

# pylint: disable=R0903

from pjscript.models.base \
    import BaseModel
from pjscript.models.literal \
    import IdentifierLiteral


class BaseExpression(BaseModel):

    """Base expression class"""

    @staticmethod
    def _get_gen(
            identifier: IdentifierLiteral,
            env: str = '_env'
    ):

        """Generate ...env...->get(...)"""

        return f'{env}->get({identifier.generate()})'

    @staticmethod
    def _get_member_gen(
            identifier: IdentifierLiteral,
            env: str = '_env'
    ):

        """Generate ..env..->get(...) for obj. member"""

        parts = identifier.token().value().split('.')
        resulting = f'{ env }->get((char*)"{parts[0]}")'

        for identifier in parts[1:]:
            resulting += f'->get((char*)"{identifier}")'

        return resulting

    @staticmethod
    def _set_gen(
            lhs: IdentifierLiteral,
            rhs: BaseModel, mutable: bool,
            env: str = '_env'
    ):

        """Generate ...env...->set(...)"""

        return f'{{auto* _ = {env};' \
               f'_->set({lhs.generate()}, ' \
               f'{rhs.generate()}, ' \
               f'{ "true" if mutable else "false" });}}'

    @staticmethod
    def _set_member_gen(
            lhs: IdentifierLiteral,
            rhs: BaseModel,
            mutable: bool,
            env: str = '_env'
    ):

        """Generate ...env...->set(...) for obj. member"""

        parts = lhs.token().value().split('.')
        resulting = f'{{auto* _ = {env}->get((char*)"{parts[0]}")'

        for part in parts[1:-1]:
            resulting += f'->get((char*)"{part}")'

        resulting += ';'  # <---- separate get and set expressions

        return resulting + f'_->set((char*)"{parts[-1]}", ' \
                           f'{rhs.generate()}, ' \
                           f'{"true" if mutable else "false"});}}'
