from abc import ABC, abstractmethod
from PIL import Image
from gramdesigner.core.composition import Composition


class Renderer(ABC):
    """Contract: render a Composition into a Pillow-independent domain result."""
    @abstractmethod
    def render(self, composition: Composition) -> Image.Image:
        """Render composition and return an RGBA image."""
        raise NotImplementedError
