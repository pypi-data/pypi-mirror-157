from .base_processor import BaseProcessor
import numpy as np
from functools import wraps 

class Lens(BaseProcessor):

    def __init__(self, enable: bool, height: int, width: int):
        """Initialize Lense object.
          
        Args:
            enable (bool)
            height (int)
            width (int)

        Returns:

        """

        super().__init__(enable)
        self._height = height
        self._width = width

    def decorator(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            sensor = args[0]
            image = args[1]
            self.process(image)
            return f(sensor, image)
        return decorated

    def process(self, image: np.array) -> np.array:
        """Validate that the shape of the input numpy data matches de Lens height 
           and width properties
          
        Args:
            image (np.array)

        Returns:
            np.array: returns input image if the input numpyt data matches the 
            height and width properties, otherwise raise ValueError exception.

        """
        
        if image.shape == (self._height, self._width):
            return image
        else: 
            raise ValueError(
                "Image shape does not match height and width properties. \
                 Image shape is " + str(image.shape) + " but required dimensions \
                 are " + str((self._height, self._width))
            )

    @property
    def height(self) -> int:
        """Returns height value

        Args:

        Returns:
            height (int)

        """

        return self._height
    
    @property 
    def width(self) -> int:
        """Returns width value

        Args:

        Returns:
            width (int)

        """

        return self._width

    @height.setter
    def height(self, val: int) -> None:
        """Set height value

        Args:
            val (int)

        Returns:
            None
        """

        self._height = val

    @width.setter
    def width(self, val: int) -> None:
        """Set width value

        Args:
            val (int)

        Returns:
            None
        """

        self._width = val

if __name__ == "__main__":
    lens = Lens(enable = True, height = 2, width = 2)