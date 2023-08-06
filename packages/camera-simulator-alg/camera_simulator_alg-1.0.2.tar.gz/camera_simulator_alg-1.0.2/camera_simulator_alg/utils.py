
from .sensor import Sensor
from .contants import HEIGHT_SIZE, WIDTH_SIZE, GAIN
import numpy as np

def mymean():
    """This function generates a random image, pass it trough a Sensor 
       object a returns the average pixel value of the image.
    
    """
    # Generate random image.
    random_image = np.random.rand(HEIGHT_SIZE, WIDTH_SIZE) * 255

    # Pass the image through a Sensor object
    sensor = Sensor(enable = True, gain = GAIN)
    image = sensor.process(random_image)

    # Return the mean of the image.
    return np.average(image)