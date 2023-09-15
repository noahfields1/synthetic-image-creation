import os
import numpy as np
import util
import pandas as pd
import shutil
from skimage.transform import resize
import yaml
import matplotlib
import PIL

"""
#Given a list of files, 'files.txt' we will zip the filtered files
#into a zip file ready to be exported to a GPU.
"""
def create_zip_with_selected_files(file_path = "files_clean.txt", zip_file_name = "files_tidy.zip"):

    pathways_list_yaml = util.file_to_array(file_path)
    pathways_list = util.remove_file_extensions(pathways_list_yaml)
    pathways_list_X_npy = util.add_file_extensions(pathways_list,"X.npy")
    pathways_list_Y_npy = util.add_file_extensions(pathways_list,"Y.npy")
    pathways_list_Yc_npy = util.add_file_extensions(pathways_list,"Yc.npy")

    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        zipf.write("files_clean.txt", os.path.relpath("files_clean.txt", 'files'))
        
        print("Starting Zipping")
        for pathway in pathways_list_yaml:
            zipf.write(pathway, os.path.relpath(pathway, 'files'))
        print("Finished yaml files, Starting X.npy files")
        for pathway in pathways_list_X_npy:
            zipf.write(pathway, os.path.relpath(pathway, 'files'))
        """
        print("Finished yaml files, Starting Y.npy files")
        for pathway in pathways_list_Y_npy:
            zipf.write(pathway, os.path.relpath(pathway, 'files'))
        """
        print("Finished X files, Starting Yc.npy files")
        for pathway in pathways_list_Yc_npy:
            zipf.write(pathway, os.path.relpath(pathway, 'files'))
            
def filter(csv_pathway='created_attributes.csv'):
    df = pd.read_csv(csv_pathway)
    output_file = "files_clean.txt"
    arr = []
    for index, row in df.iterrows():
        if row['gradient'] == None or row['std_dev'] == None:
            continue
        elif row['gradient'] == 0 or row['std_dev'] == 0:
            continue
        elif row['std_dev'] / row['gradient'] < 3 and row['eccentricity'] < 0.8 and row['std_dev'] < 0.27:
            arr.append(row['pathway'] + '.yaml')
    util.write_array_to_file(arr,output_file)

def resize_images(file_path = 'files_clean.txt', output_file = 'files_clean_resized.txt', source_dir = './files', destination_dir = './files_resized'):
    # List of file extensions to include
    allowed_extensions = ['.X.npy', '.Yc.npy', '.yaml']
    pathways_list_yaml = util.file_to_array(file_path)
    pathways_list = util.remove_file_extensions(pathways_list_yaml)
    pathways_list_X_npy = util.add_file_extensions(pathways_list,"X.npy")
    pathways_list_Yc_npy = util.add_file_extensions(pathways_list,"Yc.npy")

    # Create the destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Walk through the source directory and process files
    for files in [pathways_list_Yc_npy,pathways_list_yaml,pathways_list_X_npy]:
        for file in files:
            # Check if the file has an allowed extension
            if any(file.endswith(ext) for ext in allowed_extensions):

                # Build the destination file paths
                destination_file_path = file.replace('files','files_resized')

                # Create the destination directory structure if it doesn't exist
                os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)

                # Process the file based on its extension
                if file.endswith('.X.npy'):
                    # Load the numpy array
                    data = np.load(file)
                    initial_min = np.min(data)
                    initial_max = np.max(data)

                    # Perform array manipulation here (e.g., resizing)
                    # For example, to resize to 115x115:

                    data = resize(data, (120, 120),anti_aliasing=True)
                    current_min = np.min(data)
                    current_max = np.max(data)
                    data = ((data - current_min) / (current_max - current_min)) * (initial_max - initial_min) + initial_min
                    
                    # Create a 240x240 array filled with random values between min and max
                    random_array = np.random.randint(initial_min, initial_max, size=(240, 240), dtype=np.int16)

                    # Calculate the position to place the 80x80 array at the center of the 240x240 array
                    center_x = (240 - 120) // 2
                    center_y = (240 - 120) // 2


                    # Copy the data_array into the random_array at the center
                    random_array[center_x:center_x + 120, center_y:center_y + 120] = data
                    data = random_array

                    #matplotlib.image.imsave('temp.png', data,cmap='gray')
                    #img = PIL.Image.open('temp.png').convert('L')
                    #img.save(destination_file_path.replace('npy','png')) #saving png image

                    # Save the edited array to the destination
                    #np.save(destination_file_path, data)

                # Process the file based on its extension
                elif file.endswith('.Yc.npy'):
                    # Load the numpy array
                    data = np.load(file)

                    # Perform array manipulation here (e.g., resizing)
                    data = resize(data, (120, 120),anti_aliasing=True)

                    # Create a 240x240 array
                    random_array = np.zeros((240,240))


                    # Calculate the position to place the 80x80 array at the center of the 240x240 array
                    center_x = (240 - 120) // 2
                    center_y = (240 - 120) // 2


                    # Copy the data_array into the random_array at the center
                    random_array[center_x:center_x + 120, center_y:center_y + 120] = data
                    data = (random_array > 0).astype(np.uint8)
    

                    matplotlib.image.imsave('temp.png', data,cmap='gray')
                    img = PIL.Image.open('temp.png').convert('L')
                    img.save(destination_file_path.replace('npy','png')) #saving png image

                    # Save the edited array to the destination
                    #np.save(destination_file_path, data)

                    

                elif file.endswith('.yaml'):
                    # Load and process the YAML file
                    with open(file, 'r') as yaml_file:
                        yaml_data = yaml.safe_load(yaml_file)
                        yaml_data['X'] = yaml_data['X'].replace('files','files_resized')
                        yaml_data['Yc'] = yaml_data['Yc'].replace('files','files_resized')

                    # Perform YAML data manipulation here if needed

                    # Save the edited YAML data to the destination
                    with open(destination_file_path, 'w') as dest_yaml_file:
                        yaml.dump(yaml_data, dest_yaml_file, default_flow_style=False)

    #pathways_list_yaml_resized = [x.replace('files','files_resized') for x in pathways_list_yaml]
    #util.write_array_to_file(pathways_list_yaml_resized,output_file)

    print("Files copied and edited to '{}' directory.".format(destination_dir))






if __name__ == "__main__":
    resize_images()
    #filter('/Users/noah/Desktop/image-data-creation/created_attributes.csv')
    




