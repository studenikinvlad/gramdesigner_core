from pathlib import Path

from PIL import Image, UnidentifiedImageError


class AssetLoader:
    """Loads local raster assets from one trusted root directory."""
    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()

    def resolve(self, asset: str) -> Path:
        if not asset or Path(asset).is_absolute():
            raise ValueError("Asset must be a non-empty relative path.")
        candidate = (self.root / asset).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(f"Asset path escapes asset root: {asset}") from exc
        if not candidate.is_file():
            raise FileNotFoundError(f"Asset not found: {candidate}")
        return candidate

    def load(self, asset: str) -> Image.Image:
        path = self.resolve(asset)
        try:
            with Image.open(path) as source:
                source.load()
                return source.convert("RGBA")
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError(f"Could not load image asset '{asset}': {exc}") from exc
