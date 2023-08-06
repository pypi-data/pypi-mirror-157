import numpy as np
import abc

class BaseProcessor():

    def __init__(self, enable: bool):
        """Initialize BaseProcessor object.
          
        Args:
            enable (bool)

        Returns:

        """

        self._enable = enable

    @abc.abstractmethod
    def process(self, image: np.array) -> np.array:
        """Returns same input image.
          
        Args:
            image (np.array)

        Returns:
            np.array : returns same input array

        """
        return image

    @property 
    def enable(self):
        """Returns enable value

        Args:

        Returns:
            enable (bool)

        """

        return self._enable

    @enable.setter
    def enable(self, val) -> None:
        """Set height value

        Args:
            val (int)

        Returns:
            None
        """

        self._enable = val
