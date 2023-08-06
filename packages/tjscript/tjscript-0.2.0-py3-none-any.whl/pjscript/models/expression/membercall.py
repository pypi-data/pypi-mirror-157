"""PJScript MemberCallExpression"""

# pylint: disable=line-too-long  # :)

from pjscript.models.expression.call \
    import CallExpression


class MemberCallExpression(CallExpression):

    """MemberCallExpression class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate MemberCallExpression"""

        environ = opts.get('env', '_env')  # <------------------------------------------------ environment to use

        args = '{' + ','.join(map(lambda _argument: '(' + _argument.generate() + ')->some()', self.args())) + '}'

        inst = 'true' if self.instantiation() else 'false'  # <--------- ---------'$instantiation' argument value

        return f'{self._get_member_gen(self.name(), environ)}->operator()({args}, {inst})' + self._semicolon(top)
