from dataclasses import dataclass, field

from gramdesigner.core.canvas import Canvas
from gramdesigner.core.layer import Layer


@dataclass(frozen=True, slots=True)
class Composition:
    canvas: Canvas
    layers: list[Layer] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation independent of Pillow."""
        return {
            "canvas": {
                "width": self.canvas.width,
                "height": self.canvas.height,
                "background": self.canvas.background,
            },
            "layers": [
                {
                    "asset": layer.asset,
                    "x": layer.x,
                    "y": layer.y,
                    "width": layer.width,
                    "height": layer.height,
                    "opacity": layer.opacity,
                    "visible": layer.visible,
                }
                for layer in self.layers
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Composition":
        try:
            canvas_data = data["canvas"]
            canvas = Canvas(
                width=int(canvas_data["width"]),
                height=int(canvas_data["height"]),
                background=canvas_data.get("background", "transparent"),
            )
            layers = [Layer(**item) for item in data.get("layers", [])]
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid composition data: {exc}") from exc
        return cls(canvas=canvas, layers=layers)
