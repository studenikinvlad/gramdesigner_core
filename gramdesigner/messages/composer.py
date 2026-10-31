"""Programmatic message composition and validation."""
from __future__ import annotations
from .models import Message, Block, Paragraph, Inline, as_inline
from .serializers import serialize_markdownv2, serialize_html, serialize_plain_text

TELEGRAM_TEXT_LIMIT = 4096


class MessageComposer:
    def __init__(self): self._blocks: list[Block] = []
    def paragraph(self, *content: Inline | str) -> "MessageComposer":
        self._blocks.append(Paragraph(*content)); return self
    def heading(self, *content: Inline | str, level: int = 1) -> "MessageComposer":
        from .models import Heading
        self._blocks.append(Heading(*content, level=level)); return self
    def quote(self, *content: Inline | str, expandable: bool = False) -> "MessageComposer":
        from .models import Quote
        self._blocks.append(Quote(*content, expandable=expandable)); return self
    def list(self, items: list[str | tuple[Inline | str, ...]], *, ordered: bool = False) -> "MessageComposer":
        from .models import ListBlock
        self._blocks.append(ListBlock(items, ordered=ordered)); return self
    def pre(self, code: str, language: str | None = None) -> "MessageComposer":
        from .models import Pre
        self._blocks.append(Pre(code, language)); return self
    def build(self) -> Message: return Message(blocks=list(self._blocks))


def validate_message(message: Message, *, max_length: int = TELEGRAM_TEXT_LIMIT) -> list[str]:
    errors = []
    if not isinstance(message, Message): return ["message must be a Message instance"]
    plain = serialize_plain_text(message)
    if len(plain) > max_length: errors.append(f"Message is {len(plain)} characters; limit is {max_length}")
    for block in message.blocks:
        if hasattr(block, "level") and not 1 <= block.level <= 6: errors.append("Heading level must be between 1 and 6")
        if hasattr(block, "items") and not block.items: errors.append("List must contain at least one item")
    return errors


def validate_or_raise(message: Message, *, max_length: int = TELEGRAM_TEXT_LIMIT) -> None:
    errors = validate_message(message, max_length=max_length)
    if errors: raise ValueError("Invalid message: " + "; ".join(errors))
