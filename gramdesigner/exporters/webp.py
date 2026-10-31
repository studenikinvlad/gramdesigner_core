from pathlib import Path
from PIL import Image


def save_webp(
    image: Image.Image,
    destination: str | Path,
    *,
    lossless: bool = True,
    quality: int = 90,
) -> Path:
    """Save an image as WebP, preserving its alpha channel."""
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGBA").save(
        path, format="WEBP", lossless=lossless, quality=quality, method=6
    )
    return path
