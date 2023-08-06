import re
import textwrap
from string import Formatter
from typing import Any, List, Union


class CustomFormats(Formatter):
    def __init__(self) -> None:
        super().__init__()
        self.custom_specs = [
            # function, regex matcher, group casts (optional), return cast (optional)
            (self.boolean, r"^(?P<spec>!?(?:true|false))$", None, str),
            (self.length, "^len$", None, str),
            (self.bbimg, "^bbimg$", None, None),
            (self.layout, r"^layout,(?P<width>\d+)x(?P<height>\d+)x(?P<spacing>\d+)$", (int, int, int), None),
            (self.wrap, r"^>>(?P<indent>\d+)x(?P<width>\d+)$", (int, int), None),
            (self.center, r"^\^>(?P<center_width>\d+)x(?P<wrap_width>\d+)$", (int, int), None)
        ]

    def chain(self, value: Any, format_spec: str) -> Any:
        """Support chaining format specs separated by `:`."""
        for spec in format_spec.split(":"):
            value = self.format_field(value, spec)
        return value

    @staticmethod
    def boolean(value: Any, spec: str) -> int:
        """Return evaluated boolean value of input as a bool-int."""
        true = spec in ("true", "!false")
        false = spec in ("false", "!true")
        if not true and not false:
            raise ValueError("spec must be true, !false, false, or !true")
        b = bool(value)
        if false:
            b = not b
        return int(b)

    @staticmethod
    def length(value: Any) -> int:
        """Return object length."""
        return len(value)

    @staticmethod
    def bbimg(value: Union[List[Union[dict, str]], Union[dict, str]]) -> Union[List[str], str]:
        """
        Convert a list of values into a list of BBCode [LIST][IMG] strings.
        If only one item is provided, then a single BBCode string will be provided, not a list.

        Example:
            >>> f = CustomFormats()
            >>> f.bbimg("https://source.unsplash.com/random")
            '[URL=https://source.unsplash.com/random][IMG]https://source.unsplash.com/random[/IMG][/URL]'
            >>> f.bbimg({'url': 'https://picsum.photos/id/237/info', 'src': 'https://picsum.photos/id/237/200/300'})
            '[URL=https://picsum.photos/id/237/info][IMG]https://picsum.photos/id/237/200/300[/IMG][/URL]'
            >>> f.bbimg([{'url': 'https://foo...', 'src': 'https://bar...'}, 'https://bizz...', ...])
            ['[URL=https://foo...][IMG]https://bar...[/IMG][/URL]',
            '[URL=https://bizz...][IMG]https://bizz...[/IMG][/URL]', ...]
        """
        if not value:
            return ""
        if not isinstance(value, list):
            value = [value]
        images = [
            ({"url": x, "src": x} if not isinstance(x, dict) else x)
            for x in value
        ]
        bb = [f"[URL={x['url']}][IMG]{x['src']}[/IMG][/URL]" for x in images]
        if len(bb) == 1:
            return bb[0]
        return bb

    @staticmethod
    def layout(value: Union[List[str], str], width: int, height: int, spacing: int) -> str:
        """
        Lay out data in a grid with specific lengths, heights, and spacing.

        Example:
            >>> f = CustomFormats()
            >>> f.layout(['1', '2', '3', '4'], width=2, height=2, spacing=0)
            12
            34
            >>> f.layout(['1', '2', '3', '4'], width=2, height=2, spacing=1)
            1 2

            3 4
        """
        if not value:
            return ""
        if not isinstance(value, list):
            value = [value]
        if len(value) != width * height:
            # TODO: How about just ignore and try fill as much as it can?
            raise ValueError("Layout invalid, not enough images...")
        grid = [
            (value[i:i + width])
            for i in range(0, len(value), width)
        ]
        grid_indented = [(" " * spacing).join(x) for x in grid]
        grid_str = ("\n" * (spacing + 1)).join(grid_indented)
        return grid_str

    def wrap(self, value: Union[List[str], str], indent: int, width: int) -> str:
        """Text-wrap data at a specific width and indent amount."""
        if isinstance(value, list):
            return self.list_to_indented_strings(value, indent)
        return "\n".join(textwrap.wrap(value or "", width, subsequent_indent=" " * indent))

    @staticmethod
    def center(value: str, center_width: int, wrap_width: int) -> str:
        """Center data at a specific width, while also text-wrapping at a specific width."""
        return "\n".join([x.center(center_width) for x in textwrap.wrap(value or "", wrap_width)])

    def format_field(self, value: Any, format_spec: str) -> str:
        """Apply both standard formatters along with custom formatters to value."""
        if ":" in format_spec:
            return self.chain(value, format_spec)
        for func, match_str, group_casts, return_cast in self.custom_specs:
            match = re.match(match_str, format_spec)
            if not match:
                continue
            groups = match.groupdict()  # type: dict[str, Any]
            if group_casts:
                groups = {k: group_casts[i](v) for i, (k, v) in enumerate(groups.items())}
            new_value = func(value, **groups)
            if return_cast:
                new_value = return_cast(new_value)
            return new_value
        return super().format_field(value, format_spec)

    def list_to_indented_strings(self, value: list, indent: int = 0) -> str:
        """Recursively convert a list to an indented \n separated string."""
        if isinstance(value[0], list):
            return self.list_to_indented_strings(value[0], indent)
        return f"\n{' ' * indent}".join(value)
