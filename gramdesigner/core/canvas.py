from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Canvas:
    width: int
    height: int
    background: str = "transparent"

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Canvas width and height must be positive.")
        if self.background != "transparent":
            raise ValueError("v0.1 currently supports only a transparent background.")
