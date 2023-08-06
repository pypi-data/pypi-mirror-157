
from camera_simulator_alg.sensor import Sensor
import camera_simulator_alg.contants as ct
import numpy as np

def mymean():
    """This function generates a random image, pass it trough a Sensor 
       object a returns the average pixel value of the image.
    
    """
    # Generate random image.
    random_image = np.random.rand(ct.HEIGHT_SIZE, ct.WIDTH_SIZE) * 255

    # Pass the image through a Sensor object
    sensor = Sensor(enable = True, gain = ct.GAIN)
    image = sensor.process(random_image)

    # Return the mean of the image.
    return np.average(image)