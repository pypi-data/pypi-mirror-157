"""PJScript MemberAccessExpression"""

from pjscript.models.expression.access \
    import AccessExpression


class MemberAccessExpression(AccessExpression):

    """MemberAccessExpression class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate MemberAccessExpression"""

        environment = opts.get('env', '_env')  # <-------------------- environment to use

        return f'{self._get_member_gen(self.name(), environment)}' + self._semicolon(top)
