"""Platform-neutral structured message model."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypeAlias


@dataclass(frozen=True)
class Text:
    value: str


@dataclass(frozen=True)
class Bold:
    children: tuple["Inline", ...]
    def __init__(self, *children: "Inline | str"):
        object.__setattr__(self, "children", tuple(as_inline(x) for x in children))


@dataclass(frozen=True)
class Italic:
    children: tuple["Inline", ...]
    def __init__(self, *children: "Inline | str"):
        object.__setattr__(self, "children", tuple(as_inline(x) for x in children))


@dataclass(frozen=True)
class Underline:
    children: tuple["Inline", ...]
    def __init__(self, *children: "Inline | str"):
        object.__setattr__(self, "children", tuple(as_inline(x) for x in children))


@dataclass(frozen=True)
class Strike:
    children: tuple["Inline", ...]
    def __init__(self, *children: "Inline | str"):
        object.__setattr__(self, "children", tuple(as_inline(x) for x in children))


@dataclass(frozen=True)
class Spoiler:
    children: tuple["Inline", ...]
    def __init__(self, *children: "Inline | str"):
        object.__setattr__(self, "children", tuple(as_inline(x) for x in children))


@dataclass(frozen=True)
class Link:
    url: str
    children: tuple["Inline", ...]
    def __init__(self, url: str, *children: "Inline | str"):
        object.__setattr__(self, "url", url)
        object.__setattr__(self, "children", tuple(as_inline(x) for x in children))


@dataclass(frozen=True)
class Code:
    value: str


@dataclass(frozen=True)
class Pre:
    value: str
    language: str | None = None


Inline: TypeAlias = Text | Bold | Italic | Underline | Strike | Spoiler | Link | Code


def as_inline(value: Inline | str) -> Inline:
    return Text(value) if isinstance(value, str) else value


@dataclass(frozen=True)
class Paragraph:
    children: tuple[Inline, ...]
    def __init__(self, *children: Inline | str):
        object.__setattr__(self, "children", tuple(as_inline(x) for x in children))


@dataclass(frozen=True)
class Heading:
    children: tuple[Inline, ...]
    level: int = 1
    def __init__(self, *children: Inline | str, level: int = 1):
        object.__setattr__(self, "children", tuple(as_inline(x) for x in children))
        object.__setattr__(self, "level", level)


@dataclass(frozen=True)
class Quote:
    children: tuple[Inline, ...]
    expandable: bool = False
    def __init__(self, *children: Inline | str, expandable: bool = False):
        object.__setattr__(self, "children", tuple(as_inline(x) for x in children))
        object.__setattr__(self, "expandable", expandable)


@dataclass(frozen=True)
class ListBlock:
    items: tuple[tuple[Inline, ...], ...]
    ordered: bool = False
    def __init__(self, items: list[str | tuple[Inline | str, ...]], ordered: bool = False):
        normalized = []
        for item in items:
            vals = (item,) if isinstance(item, str) else item
            normalized.append(tuple(as_inline(x) for x in vals))
        object.__setattr__(self, "items", tuple(normalized))
        object.__setattr__(self, "ordered", ordered)


Block: TypeAlias = Paragraph | Heading | Quote | ListBlock | Pre


@dataclass
class Message:
    blocks: list[Block] = field(default_factory=list)
    media: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_markdown(cls, source: str) -> "Message":
        from .parser import parse_markdown
        return parse_markdown(source)

    def to_markdownv2(self) -> str:
        from .serializers import serialize_markdownv2
        return serialize_markdownv2(self)

    def to_html(self) -> str:
        from .serializers import serialize_html
        return serialize_html(self)

    def to_plain_text(self) -> str:
        from .serializers import serialize_plain_text
        return serialize_plain_text(self)
