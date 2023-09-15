import os
import numpy as np
from PIL import Image


def create_Xo_images(home_dir = './files'):
    # Loop through all files and directories in the home directory
    for root, dirs, files in os.walk(home_dir):
        for file in files:
            # Check if the file ends with X.npy
            if file.endswith('X.npy'):
                # Load the X.npy file and standardize values to be between 0 and 1
                x = np.load(os.path.join(root, file))
                if np.max(x) != np.min(x): 
                    x = (x - np.min(x)) / (np.max(x) - np.min(x))

                # Load the corresponding Yp.npy file
                y = np.load(os.path.join(root, file.replace('X.npy', 'Yp.npy')))
                # Get the coordinates where y == 1
                coords = np.where(y == 1)
                # Set the corresponding values in x to 1
                x[coords] = 1
                # Save the new array as Xo.npy
                np.save(os.path.join(root, file.replace('X.npy', 'Xo.npy')), x)
                # Save the new array as an image with the suffix Xo.png
                img = Image.fromarray((x * 255).astype(np.uint8))
                img.save(os.path.join(root, file.replace('X.npy', 'Xo.png')))
