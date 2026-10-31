from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Layer:
    """A raster asset positioned on the canvas; list order determines z-order."""
    asset: str
    x: int
    y: int
    width: int | None = None
    height: int | None = None
    opacity: float = 1.0
    visible: bool = True

    def __post_init__(self) -> None:
        if not self.asset.strip():
            raise ValueError("Layer asset path cannot be empty.")
        if (self.width is not None and self.width <= 0) or (
            self.height is not None and self.height <= 0
        ):
            raise ValueError("Layer width and height must be positive when set.")
        if not 0.0 <= self.opacity <= 1.0:
            raise ValueError("Layer opacity must be between 0.0 and 1.0.")
