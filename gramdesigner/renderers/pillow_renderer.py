from PIL import Image

from gramdesigner.assets import AssetLoader
from gramdesigner.core.composition import Composition
from gramdesigner.renderers.base import Renderer


class PillowRenderer(Renderer):
    def __init__(self, assets: AssetLoader):
        self.assets = assets

    def render(self, composition: Composition) -> Image.Image:
        canvas = Image.new(
            "RGBA",
            (composition.canvas.width, composition.canvas.height),
            (0, 0, 0, 0),
        )
        for layer in composition.layers:
            if not layer.visible:
                continue
            asset = self.assets.load(layer.asset)
            if layer.width is not None or layer.height is not None:
                target_width = layer.width if layer.width is not None else asset.width
                target_height = layer.height if layer.height is not None else asset.height
                asset = asset.resize(
                    (target_width, target_height), Image.Resampling.LANCZOS
                )
            if layer.opacity < 1.0:
                alpha = asset.getchannel("A")
                alpha = alpha.point(lambda value: round(value * layer.opacity))
                asset.putalpha(alpha)
            canvas.alpha_composite(asset, dest=(layer.x, layer.y))
        return canvas
