"""Small dependency-free Markdown parser for common message formatting.

Supports paragraphs, headings, blockquotes, lists, fenced code, and common inline
Telegram Markdown markers. This intentionally isn't a full CommonMark parser.
"""
from __future__ import annotations
import re
from .models import Message, Paragraph, Heading, Quote, ListBlock, Pre, Text, Bold, Italic, Underline, Strike, Spoiler, Link, Code

_INLINE = re.compile(r'(\*\*.+?\*\*|__.+?__|\*.+?\*|_.+?_|~~.+?~~|~.+?~|\|\|.+?\|\||`.+?`|\[[^\]]+\]\([^)]+\))')


def _parse_inline(source: str):
    nodes = []
    pos = 0
    for match in _INLINE.finditer(source):
        if match.start() > pos: nodes.append(Text(source[pos:match.start()]))
        token = match.group(0)
        if token.startswith('**'): node = Bold(token[2:-2])
        elif token.startswith('__'): node = Underline(token[2:-2])
        elif token.startswith('*'): node = Bold(token[1:-1])
        elif token.startswith('_'): node = Italic(token[1:-1])
        elif token.startswith('~~'): node = Strike(token[2:-2])
        elif token.startswith('~'): node = Strike(token[1:-1])
        elif token.startswith('||'): node = Spoiler(token[2:-2])
        elif token.startswith('`'): node = Code(token[1:-1])
        elif token.startswith('['):
            m = re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)', token)
            node = Link(m.group(2), m.group(1)) if m else Text(token)
        else: node = Text(token)
        nodes.append(node); pos = match.end()
    if pos < len(source): nodes.append(Text(source[pos:]))
    return nodes


def parse_markdown(source: str) -> Message:
    if not isinstance(source, str): raise TypeError("Markdown source must be a string")
    lines = source.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    blocks = []; paragraph = []; i = 0
    def flush():
        if paragraph:
            blocks.append(Paragraph(*_parse_inline(' '.join(paragraph))))
            paragraph.clear()
    while i < len(lines):
        line = lines[i]
        if not line.strip(): flush(); i += 1; continue
        if line.startswith('```'):
            flush(); language = line[3:].strip() or None; code = []; i += 1
            while i < len(lines) and not lines[i].startswith('```'): code.append(lines[i]); i += 1
            if i < len(lines): i += 1
            blocks.append(Pre('\n'.join(code), language)); continue
        heading = re.match(r'^(#{1,6})\s+(.*)$', line)
        if heading:
            flush(); blocks.append(Heading(*_parse_inline(heading.group(2)), level=len(heading.group(1)))); i += 1; continue
        if line.startswith('>'):
            flush(); quote = []
            while i < len(lines) and lines[i].startswith('>'):
                quote.append(lines[i][1:].lstrip()); i += 1
            blocks.append(Quote(*_parse_inline('\n'.join(quote)))); continue
        if re.match(r'^\s*(?:[-*+]\s+|\d+[.)]\s+)', line):
            flush(); items = []; ordered = bool(re.match(r'^\s*\d+[.)]\s+', line))
            while i < len(lines) and re.match(r'^\s*(?:[-*+]\s+|\d+[.)]\s+)', lines[i]):
                items.append(tuple(_parse_inline(re.sub(r'^\s*(?:[-*+]\s+|\d+[.)]\s+)', '', lines[i])))); i += 1
            blocks.append(ListBlock(items, ordered=ordered)); continue
        paragraph.append(line.strip()); i += 1
    flush()
    return Message(blocks=blocks)
