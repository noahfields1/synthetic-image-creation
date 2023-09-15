import os
import glob
import numpy as np
import matplotlib.pyplot as plt

def extract_perimeter(root_dir = "./files"):
    # Get all file paths ending in Yc.npy recursively in directory './files'
    y_file_paths = glob.glob(os.path.join(root_dir, '**', '*Yc.npy'), recursive=True)

    for y_file_path in y_file_paths:
        # Load the Y.npy file
        y_arr = np.load(y_file_path)

        # Initialize empty list to store perimeter pixel coordinates
        perimeter = []

        # Loop through each pixel in the Yc.npy array except for the edges
        for i in range(1, 239):
            for j in range(1, 239):
                # Check if the pixel is white and has a black neighbor in any direction
                if y_arr[i][j] == 1 and (y_arr[i-1][j] == 0 or y_arr[i+1][j] == 0 or y_arr[i][j-1] == 0 or y_arr[i][j+1] == 0):
                    perimeter.append((i, j))

        # Create new array where every coordinate is black (0) except those in the 'perimeter' list
        new_arr = np.zeros((240, 240), dtype=int)
        for coord in perimeter:
            new_arr[coord[0]][coord[1]] = 1

        # Save the new array in a npy file with the same name but replace Y with Yp
        new_file_path = y_file_path.replace('Yc.npy', 'Yp.npy')
        np.save(new_file_path, new_arr)

        #new_image_path = y_file_path.replace('Yc.npy', 'Yp.png')
        #plt.imsave(new_image_path, new_arr, cmap='gray')

if __name__ == "__main__":
    pass
    #extract_perimeter(root_dir = "/Users/noah/Desktop/Marsden/files")

