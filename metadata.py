import numpy as np
import os
import matplotlib.pyplot as plt

def touching_pixels_diff(X_npy):
    Y_npy = X_npy.replace('X','Y')
    Yc_npy = X_npy.replace('X','Yc')
    """
    Takes a medical image and a numpy array of the perimeter pixels, and returns a list of
    the difference between pixels on the perimeter and pixels just outside the perimeter
    for the touching pixels only.
    
    Parameters:
    X (numpy array): 240x240 medical image containing vessels.
    Y (numpy array): numpy array of pixels labeled as perimeter of the vessel.
    
    Returns:
    diff_list (list): list of the difference between pixels on the perimeter and pixels just
                      outside the perimeter for the touching pixels only.
    """

    X = np.load(X_npy)
    Y_arr = np.load(Y_npy)
    Yc_arr = np.load(Yc_npy)
    Y_temp = np.where(Y_arr == 255)
    Yc_temp = np.where(Yc_arr == 255)
    Y = []
    Yc = set()

    for i in range(len(Y_temp[0])):
        Y.append((Y_temp[0][i],Y_temp[1][i]))
    for i in range(len(Yc_temp[0])):
        Yc.add((Yc_temp[0][i],Yc_temp[1][i]))

    # Initialize empty list to store differences
    diff_list = []
    
    # Loop through perimeter pixels
    for i in range(len(Y)):
        # Get current perimeter pixel coordinates
        x, y = Y[i]
        
        # Get neighboring pixels
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1), (x+1, y+1), (x-1, y-1), (x-1, y+1), (x+1, y-1)]
        
        # Loop through neighboring pixels
        for neighbor in neighbors:
            # Check if neighbor is outside the perimeter and within image bounds
            if neighbor not in Yc and neighbor[0] >= 0 and neighbor[0] < 240 and neighbor[1] >= 0 and neighbor[1] < 240:
                # Calculate difference between perimeter pixel and neighbor
                diff = round(X[x, y] - X[neighbor[0], neighbor[1]],2)
                
                # Append difference to list if neighbor is touching perimeter pixel
                if neighbor in neighbors:
                    diff_list.append(diff/255)
    #print(np.mean(diff_list), np.std(diff_list))
    
    return np.mean(diff_list)

#touching_pixels_diff("/Users/noah/Desktop/image-data-creation/files/0151_0001/aorta/10.X.npy")

def find_files():
    dir_path = "/Users/noah/Desktop/Marsden/files"
    files = []
    for root, dirs, filenames in os.walk(dir_path):
        for filename in filenames:
            if filename.endswith('X.npy'):
                files.append(os.path.join(root, filename))
    return files
files = find_files()
total = []
for f in files:
    num = touching_pixels_diff(f)
    total.append(num)
print(np.mean(total),np.std(total))

plt.hist(total, bins=100)
plt.xlim(0,0.4)
plt.title("Noah's Created Data")
plt.xlabel('Metric')
plt.ylabel('Frequency')
plt.show()

