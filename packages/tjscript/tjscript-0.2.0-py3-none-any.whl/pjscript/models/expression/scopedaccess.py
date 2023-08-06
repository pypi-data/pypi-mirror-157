"""PJScript ScopedAccessExpression"""

from pjscript.models.expression.access \
    import AccessExpression


class ScopedAccessExpression(AccessExpression):

    """ScopedAccessExpression class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate ScopedAccessExpression"""

        environment = opts.get('env', '_env')  # <------------- environment to use

        return f'{self._get_gen(self.name(), environment)}' + self._semicolon(top)
