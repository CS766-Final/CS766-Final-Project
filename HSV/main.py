from matplotlib.image import imread
import numpy as np

if __name__ == "__main__":
    image = imread("./HSV/example.jpg")
    array = np.array(image)

    
