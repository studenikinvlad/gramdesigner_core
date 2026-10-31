"""Convenience API for rendering image compositions from Python applications."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image

from gramdesigner.assets import AssetLoader
from gramdesigner.core import Composition
from gramdesigner.renderers import PillowRenderer


class GramDesigner:
    """Reusable image composition engine bound to an asset directory.

    Asset paths in compositions are relative to ``asset_root``. For example,
    ``asset="uploads/logo.png"`` resolves to ``<asset_root>/uploads/logo.png``.
    """

    def __init__(self, asset_root: str | Path):
        self.asset_root = Path(asset_root).expanduser().resolve()
        self.renderer = PillowRenderer(AssetLoader(self.asset_root))

    def render(self, composition: Composition | dict[str, Any]) -> Image.Image:
        """Render a Composition or its JSON-compatible dictionary to RGBA Pillow image."""
        if isinstance(composition, dict):
            composition = Composition.from_dict(composition)
        if not isinstance(composition, Composition):
            raise TypeError("composition must be a Composition or dictionary")
        return self.renderer.render(composition)

    def render_to_file(
        self,
        composition: Composition | dict[str, Any],
        destination: str | Path,
        *,
        format: str | None = None,
        quality: int = 90,
        lossless: bool = True,
    ) -> Path:
        """Render and save an image as PNG or WebP, creating parent directories."""
        path = Path(destination)
        image_format = (format or path.suffix.lstrip(".")).upper()
        if image_format not in {"PNG", "WEBP"}:
            raise ValueError("Supported output formats are PNG and WEBP")
        image = self.render(composition)
        path.parent.mkdir(parents=True, exist_ok=True)
        if image_format == "PNG":
            image.save(path, format="PNG", optimize=True)
        else:
            if not 0 <= quality <= 100:
                raise ValueError("quality must be between 0 and 100")
            image.save(path, format="WEBP", lossless=lossless, quality=quality, method=6)
        return path

    def render_to_bytes(
        self,
        composition: Composition | dict[str, Any],
        *,
        format: str = "PNG",
        quality: int = 90,
        lossless: bool = True,
    ) -> bytes:
        """Render to encoded PNG/WebP bytes, convenient for HTTP and bot APIs."""
        image_format = format.upper()
        if image_format not in {"PNG", "WEBP"}:
            raise ValueError("Supported output formats are PNG and WEBP")
        image = self.render(composition)
        buffer = BytesIO()
        options: dict[str, Any] = {}
        if image_format == "WEBP":
            if not 0 <= quality <= 100:
                raise ValueError("quality must be between 0 and 100")
            options.update(lossless=lossless, quality=quality, method=6)
        image.save(buffer, format=image_format, **options)
        return buffer.getvalue()


def render_composition(
    composition: Composition | dict[str, Any],
    *,
    asset_root: str | Path,
) -> Image.Image:
    """One-shot convenience function returning a Pillow RGBA image."""
    return GramDesigner(asset_root).render(composition)
