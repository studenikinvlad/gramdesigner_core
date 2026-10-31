"""Serializers for Telegram and plain-text output."""
from __future__ import annotations
from html import escape as html_escape
from .models import *

_MD_SPECIAL = r"_ * [ ] ( ) ~ ` > # + - = | { } . ! \\".split()
_MD_CHARS = set("_ * [ ] ( ) ~ ` > # + - = | { } . ! \\".replace(" ", ""))


def _esc_md(text: str) -> str:
    return "".join("\\" + c if c in _MD_CHARS else c for c in text)


def _inline_md(node: Inline) -> str:
    if isinstance(node, Text): return _esc_md(node.value)
    if isinstance(node, Bold): return "*" + "".join(_inline_md(x) for x in node.children) + "*"
    if isinstance(node, Italic): return "_" + "".join(_inline_md(x) for x in node.children) + "_"
    if isinstance(node, Underline): return "__" + "".join(_inline_md(x) for x in node.children) + "__"
    if isinstance(node, Strike): return "~" + "".join(_inline_md(x) for x in node.children) + "~"
    if isinstance(node, Spoiler): return "||" + "".join(_inline_md(x) for x in node.children) + "||"
    if isinstance(node, Link): return "[" + "".join(_inline_md(x) for x in node.children) + "](" + node.url.replace("\\", "\\\\").replace(")", "\\)") + ")"
    if isinstance(node, Code): return "`" + node.value.replace("`", "\\`") + "`"
    raise TypeError(f"Unsupported inline node: {type(node).__name__}")


def _inline_html(node: Inline) -> str:
    if isinstance(node, Text): return html_escape(node.value, quote=False)
    if isinstance(node, Bold): return "<b>" + "".join(_inline_html(x) for x in node.children) + "</b>"
    if isinstance(node, Italic): return "<i>" + "".join(_inline_html(x) for x in node.children) + "</i>"
    if isinstance(node, Underline): return "<u>" + "".join(_inline_html(x) for x in node.children) + "</u>"
    if isinstance(node, Strike): return "<s>" + "".join(_inline_html(x) for x in node.children) + "</s>"
    if isinstance(node, Spoiler): return "<tg-spoiler>" + "".join(_inline_html(x) for x in node.children) + "</tg-spoiler>"
    if isinstance(node, Link): return '<a href="' + html_escape(node.url, quote=True) + '">' + "".join(_inline_html(x) for x in node.children) + "</a>"
    if isinstance(node, Code): return "<code>" + html_escape(node.value) + "</code>"
    raise TypeError(f"Unsupported inline node: {type(node).__name__}")


def _plain_inline(node: Inline) -> str:
    if isinstance(node, Text): return node.value
    if isinstance(node, (Bold, Italic, Underline, Strike, Spoiler, Link)):
        text = "".join(_plain_inline(x) for x in node.children)
        return text + (f" ({node.url})" if isinstance(node, Link) and node.url else "")
    if isinstance(node, Code): return node.value
    return ""


def serialize_markdownv2(message: Message) -> str:
    result = []
    for block in message.blocks:
        if isinstance(block, Pre):
            lang = block.language or ""
            result.append("```" + lang + "\n" + block.value.replace("```", "``\\`") + "\n```")
        elif isinstance(block, Heading): result.append("*" + "".join(_inline_md(x) for x in block.children) + "*")
        elif isinstance(block, Quote): result.append(">" + "".join(_inline_md(x) for x in block.children).replace("\n", "\n>"))
        elif isinstance(block, ListBlock):
            result.append("\n".join((f"{i}. " if block.ordered else "• ") + "".join(_inline_md(x) for x in item) for i, item in enumerate(block.items, 1)))
        elif isinstance(block, Paragraph): result.append("".join(_inline_md(x) for x in block.children))
        else: raise TypeError(f"Unsupported block: {type(block).__name__}")
    return "\n\n".join(result)


def serialize_html(message: Message) -> str:
    result = []
    for block in message.blocks:
        if isinstance(block, Pre):
            code = "<code" + (f' class="language-{html_escape(block.language, quote=True)}"' if block.language else "") + ">" + html_escape(block.value) + "</code>"
            result.append("<pre>" + code + "</pre>")
        elif isinstance(block, Heading): result.append("<b>" + "".join(_inline_html(x) for x in block.children) + "</b>")
        elif isinstance(block, Quote): result.append("<blockquote>" + "".join(_inline_html(x) for x in block.children) + "</blockquote>")
        elif isinstance(block, ListBlock):
            result.append("\n".join((f"{i}. " if block.ordered else "• ") + "".join(_inline_html(x) for x in item) for i, item in enumerate(block.items, 1)))
        elif isinstance(block, Paragraph): result.append("".join(_inline_html(x) for x in block.children))
        else: raise TypeError(f"Unsupported block: {type(block).__name__}")
    return "\n\n".join(result)


def serialize_plain_text(message: Message) -> str:
    result = []
    for block in message.blocks:
        if isinstance(block, Pre): result.append(block.value)
        elif isinstance(block, (Paragraph, Heading, Quote)): result.append("".join(_plain_inline(x) for x in block.children))
        elif isinstance(block, ListBlock): result.append("\n".join((f"{i}. " if block.ordered else "• ") + "".join(_plain_inline(x) for x in item) for i, item in enumerate(block.items, 1)))
    return "\n\n".join(result)
