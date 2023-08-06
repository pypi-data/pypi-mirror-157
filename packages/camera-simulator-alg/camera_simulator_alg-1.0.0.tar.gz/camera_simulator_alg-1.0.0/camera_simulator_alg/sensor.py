from camera_simulator_alg.base_processor import BaseProcessor
from camera_simulator_alg.lens import Lens
import camera_simulator_alg.contants as ct
import numpy as np 

class Sensor(BaseProcessor):

    def __init__(self, enable: bool, gain: int):
        """Initialize Sensor object.
          
        Args:
            enable (bool)
            gain (int)

        Returns:

        """

        super().__init__(enable)
        self._gain = gain

    @Lens(enable = True, height = ct.HEIGHT_SIZE, width = ct.WIDTH_SIZE).decorator
    def process(self, image: np.array) -> np.array:
        """This function first validate that the shape of the input numpy data 
           matches de Lens height and width properties and then returns the input 
           matrix times the gain attribute 
          
        Args:
            image (np.matrix): numpy matrix.

        Returns:
            np.matrix: returns input matrix times self.gain integer

        """
        return self._gain * image

    @property 
    def gain(self) -> None:
        """Returns gain value

        Args:

        Returns:
            gain (int)

        """
    
        return self._gain

    @gain.setter
    def gain(self, val: int) -> None:
        """Set gain value

        Args:
            val (int)

        Returns:
            None
        """

        self._gain = val

