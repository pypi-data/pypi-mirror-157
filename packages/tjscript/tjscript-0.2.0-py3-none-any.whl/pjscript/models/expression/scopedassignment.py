"""PJScript ScopedAssignmentExpression"""

from pjscript.models.expression.assignment \
    import AssignmentExpression


class ScopedAssignmentExpression(AssignmentExpression):

    """ScopedAssignmentExpression class"""

    def generate(self, top: bool = False, **opts) -> str:

        """Generate ScopedAssignmentExpression"""

        environment = opts.get('env', '_env')  # <---------------------------------------- environment to use

        return f'{self._set_gen(self.lhs(), self.rhs(), self.mutable(), environment)}' + self._semicolon(top)
