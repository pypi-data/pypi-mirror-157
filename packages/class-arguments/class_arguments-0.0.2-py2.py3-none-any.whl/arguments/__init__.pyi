from argparse import Action, FileType, HelpFormatter
from collections.abc import Callable, Iterable
from typing import (
    Any,
    Dict,
    NewType,
    Tuple,
    TypeVar,
)
from typing_extensions import TypeAlias

_T = TypeVar("_T")
# more precisely, Literal["store", "store_const", "store_true",
# "store_false", "append", "append_const", "count", "help", "version",
# "extend"], but using this would make it hard to annotate callers
# that don't use a literal argument
_ActionStr: TypeAlias = str
# more precisely, Literal["?", "*", "+", "...", "A...",
# "==SUPPRESS=="], but using this would make it hard to annotate
# callers that don't use a literal argument
_NArgsStr: TypeAlias = str

_SUPPRESS_T = NewType("_SUPPRESS_T", str)

def Option(
    *name_or_flags: str,
    action: _ActionStr | type[Action] = ...,
    nargs: int | _NArgsStr | _SUPPRESS_T = ...,
    const: Any = ...,
    default: Any = ...,
    type: Callable[[str], _T] | FileType = ...,
    choices: Iterable[_T] | None = ...,
    required: bool = ...,
    help: str | None = ...,
    metavar: str | tuple[str, ...] | None = ...,
    dest: str | None = ...,
    version: str = ...,
    **kwargs: Any,
) -> Any: ...

class _Option:
    def __init__(
        self,
        *name_or_flags: str,
        action: _ActionStr | type[Action] = ...,
        nargs: int | _NArgsStr | _SUPPRESS_T = ...,
        const: Any = ...,
        default: Any = ...,
        type: Callable[[str], _T] | FileType = ...,
        choices: Iterable[_T] | None = ...,
        required: bool = ...,
        help: str | None = ...,
        metavar: str | tuple[str, ...] | None = ...,
        dest: str | None = ...,
        version: str = ...,
        **kwargs: Any,
    ) -> None: ...
    def params(self) -> Tuple[Tuple, Dict]: ...
    def flags(self, prefix) -> str: ...

class Argument:
    def __init__(
        self,
        prog=None,
        usage=None,
        description=None,
        epilog=None,
        parents=[],
        formatter_class=HelpFormatter,
        prefix_chars="-",
        fromfile_prefix_chars=None,
        argument_default=None,
        conflict_handler="error",
        add_help=True,
        allow_abbrev=True,
        exit_on_error=True,
    ) -> None: ...
