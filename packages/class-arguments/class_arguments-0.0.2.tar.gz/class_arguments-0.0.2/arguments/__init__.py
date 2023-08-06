from argparse import ArgumentParser, HelpFormatter
from typing import Any


def Option(*name_or_flags, **kwargs) -> Any:
    return _Option(*name_or_flags, **kwargs)


class _Option:
    def __init__(self, *name_or_flags, **kwargs):
        self.name_or_flags = name_or_flags
        self.kwargs = kwargs

    def params(self):
        return self.name_or_flags, self.kwargs

    def flags(self, prefix_chars: str):
        return self.name_or_flags[0].replace(prefix_chars, "")


class Argument(ArgumentParser):
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
    ):
        description = description or self.__doc__
        superinit = ArgumentParser.__init__
        superinit(
            self,
            prog=prog,
            usage=usage,
            epilog=epilog,
            parents=parents,
            formatter_class=formatter_class,
            prefix_chars=prefix_chars,
            fromfile_prefix_chars=fromfile_prefix_chars,
            add_help=add_help,
            allow_abbrev=allow_abbrev,
            description=description,
            argument_default=argument_default,
            conflict_handler=conflict_handler,
        )
        for alias, option in self.__class__.__dict__.items():
            if not alias.startswith("_"):
                _args, _kwargs = option.params()
                self.add_argument(*_args, **_kwargs)

        self._args = self.parse_args()

    def __getattribute__(self, __name: str):
        try:
            v = super().__getattribute__(__name)
        except AttributeError:
            return getattr(self._args, __name)

        if isinstance(v, _Option):
            return getattr(self._args, v.flags(self.prefix_chars))
        return v
