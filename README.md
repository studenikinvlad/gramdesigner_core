# gramDesigner Engine 0.3.0 · Workbench 0.4.0

Reusable Python core for image composition/rendering and structured text-message construction. The optional local Workbench lets you test both subsystems in a browser; the library itself does not depend on the web UI or on a Telegram SDK.

## Requirements

- Python 3.10+
- Pillow 10+

## Install

From the extracted project directory:

```bash
python -m pip install -e .
```

For development and tests:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

## Run the Workbench

```bash
python server.py
```

Open <http://127.0.0.1:8765>. The workbench has three sections:

- **Messages / Markdown** — parse a Markdown subset and inspect Telegram MarkdownV2, Telegram HTML, plain-text serialization, and validation output. Formatting buttons insert common Markdown markers.
- **Article / Rich Messages** — block editor for Telegram Bot API Rich Messages: paragraphs, headings, code, footer, divider, LaTeX, anchors, lists/checklists, quotes and expandable quotes, pull quotes, tables, details, maps, button rows, photos, videos, animations, audio, documents, voice notes, collages, slideshows, and draft-only thinking blocks. Text blocks accept Rich Markdown or raw RichText JSON for entity types not covered by the toolbar. Media is embedded in the exported project JSON as data URLs. This is a composer/preview, not a Telegram sender; media must be uploaded via multipart or replaced with `file_id`/HTTPS URLs before a Bot API request. Paragraph alignment is stored in the editor project and preview, but is not part of the documented `InputRichBlock` schema.
- **Images / Renderer** — upload assets, arrange layers, adjust opacity and position, then render PNG or lossless WebP through the Pillow renderer.

The local server binds to `127.0.0.1` only. Do not expose this development server directly to the public internet.

## Image engine quick start

```python
from gramdesigner import Canvas, Composition, Layer, GramDesigner

engine = GramDesigner(asset_root="./assets")
composition = Composition(
    canvas=Canvas(width=800, height=600),
    layers=[Layer(
        asset="logo.png",  # ./assets/logo.png
        x=240, y=150, width=320, height=320,
        opacity=1.0, visible=True,
    )],
)
engine.render_to_file(composition, "./output/result.png")
png_bytes = engine.render_to_bytes(composition, format="PNG")
```

Asset names are relative to the configured asset root; they are not arbitrary filesystem paths.

## Message engine quick start

```python
from gramdesigner import (
    MessageComposer, Bold, Link, parse_markdown,
    serialize_markdownv2, serialize_html, serialize_plain_text,
    validate_message,
)

message = (
    MessageComposer()
    .heading("Daily update")
    .paragraph("Status: ", Bold("ready"), " — ", Link("https://example.com", "details"))
    .list(["first", "second"], ordered=True)
    .build()
)

errors = validate_message(message)
markdownv2 = serialize_markdownv2(message)
telegram_html = serialize_html(message)
plain_text = serialize_plain_text(message)

# Or parse source Markdown:
parsed = parse_markdown("# Hello\\n\\nThis is **bold** and _italic_.")
```

The message core is framework-independent. It builds and serializes content; it does not send messages to Telegram. The Markdown parser intentionally supports a useful subset (paragraphs, headings, blockquotes, lists, fenced code, bold, italic, underline, strike, spoiler, links and inline code), not all CommonMark features. Always validate the actual output against Telegram Bot API requirements for your use case. HTML output uses Telegram-style tags, but URL schemes and platform-specific rules should also be checked by the application before sending.

## HTTP endpoints in the local Workbench

- `GET /api/health` — version/status.
- `POST /api/message` — accepts `{"markdown":"..."}` and returns `markdownv2`, `html`, `plain_text`, `plain_length`, `limit`, `errors`, and `blocks`.
- `POST /api/upload` — saves an image under the local workspace asset directory.
- `POST /api/render?format=png|webp` — renders a composition JSON object.

The included HTTP server is a development/test harness, not a production service. Add authentication, rate limits, request-size controls, logging and deployment hardening before hosting it remotely.

### Document workspace (v0.5.0)

The Rich Message workspace now includes a local Markdown document library, search, draft/archive filters, title editing, browser-local autosave, JSON import/export, block insertion shortcuts, media/file attachment shortcuts, and preview toggling. Documents remain in the browser's local storage; export JSON for backup or transfer. Telegram publishing and cloud synchronization are not included.
