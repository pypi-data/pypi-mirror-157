from typing import TYPE_CHECKING, Optional

from astroid import nodes, Dict, Assign
from pylint.checkers import BaseChecker, utils

if TYPE_CHECKING:
    from pylint.lint import PyLinter


class NoDictDirectAccessChecker(BaseChecker):
    name = "no-dict-direct-access"
    msgs = {
        "W0001": (
            "Uses dict operator []",
            "dict-direct-access",
            "The operator[] is dangerous and might emit KeyError. Avoid it where possible.",
        ),
    }

    def __init__(self, linter: Optional["PyLinter"] = None) -> None:
        super().__init__(linter)

    def visit_subscript(self, node: nodes.Subscript) -> None:
        if isinstance(utils.safe_infer(node.value), Dict) and not isinstance(
            node.parent, Assign
        ):
            self.add_message("dict-direct-access", node=node)


def register(linter: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.

    :param linter: The linter to register the checker to.
    """
    linter.register_checker(NoDictDirectAccessChecker(linter))
