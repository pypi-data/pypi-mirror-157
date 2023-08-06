from textwrap import wrap
from typing import Any, Dict, List, Optional, Tuple, Union

from colorama import Back, Fore, Style
from tabulate import tabulate

from .formatters import get_formatter


TableData = List[Dict[str, Any]]
TableStructure = Tuple[
    Tuple[
        Union[str, Tuple[str, ...]],
        Optional[str],
        Optional[str],
        Optional[int],
    ],
    ...,
]


def colourise(
    data: str,
    foreground: Optional[str] = None,
    background: Optional[str] = None,
    style: Optional[str] = None,
):

    prefix = "{}{}{}".format(
        getattr(Fore, foreground) if foreground else "",
        getattr(Back, background) if background else "",
        getattr(Style, style) if style else "",
    )
    return f"{prefix}{data}{Style.RESET_ALL}"


class TableFilter:
    def __init__(self, data: TableData, structure: TableStructure):
        self.data = data
        self.structure = structure

    def render(self) -> str:

        rows = []
        for d in self.data:
            row = []
            for column in self.structure:
                row.append(
                    self._get_row(
                        d,
                        *(column[:1] + column[2:]),  # type: ignore
                    )
                )
            rows.append(row)

        return "{}{}{}".format(
            Style.DIM,
            tabulate(
                rows,
                headers=[_[1] for _ in self.structure],
                tablefmt="fancy_grid",
            ),
            Style.RESET_ALL,
        )

    @classmethod
    def _get_row(
        cls,
        data: Dict[str, Any],
        key: Union[str, Tuple[str]],
        formatter_name: str = "str",
        width: int = 0,
    ):

        arg_names = key
        if isinstance(key, str):
            arg_names = (key,)

        formatter = get_formatter(formatter_name)

        return formatter(*[cls._wrap(data[name], width) for name in arg_names])

    @staticmethod
    def _wrap(text: str, width: int):
        if width:
            return f"{Style.DIM}\n{Style.NORMAL}".join(wrap(text, width))
        return text


def as_table(data: TableData, structure: TableStructure) -> str:
    return TableFilter(data=data, structure=structure).render()
