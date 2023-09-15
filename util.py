from matplotlib import pyplot as plt
import numpy as np
import os
import glob
import Model_class
import zipfile
import yaml
from datetime import date

"""
This function is designed to be used after 'create_directories'.
This function rotates through all models,branches, and images
found in ./3D_points and creates 2D images and generates corresponding yaml files.
"""
def create_images():
	points3D_dir = "./3D_points"
	for model in os.listdir(points3D_dir):
		if model == ".DS_Store":
			continue


		m = Model_class.Model(model,".")
		branch_dir = points3D_dir + "/" + model
		for branch in os.listdir(branch_dir):
			if branch == ".DS_Store":
				continue

			b = Model_class.Branch(m,branch)
			image_dir = branch_dir + "/" + branch

			for image in os.listdir(image_dir):
				if image == ".DS_Store":
					continue

				im = image[0:-4].split('_')[2]
				i = Model_class.Image(b,im)
				i.generateFileNames()
				i.getPoints()
				i.getBifurcationID()
				if i.BifurcationID != -1:
					continue
				i.connectPoints()
				if len(i.points2D_filtered) < 4 or len(i.points2D_filtered) > 40000:
					continue
				i.generateYAML()
				i.createImg("X")
				i.createImg("Y")
				i.createImg("Yc")
"""
This function is used to make directories needed to run Dave's code.
If a directory already exist, then the directory is not added.
Input: The pathway to all of the models
Output: None
Function: Runs Dave's code on all models and all pathways available
using the directory holding all of the VMR models.
"""
def create_directories(models_dir):
	if not os.path.exists("./3D_points"):
		os.mkdir("./3D_points")
	if not os.path.exists("./files"):
		os.mkdir("./files")
	if not os.path.exists("./results"):
		os.mkdir("./results")
	models = set(os.listdir(models_dir))

	for m in models:
		if m == ".DS_Store":
			continue
		paths = os.listdir(models_dir + "/" + m + "/Paths/")
		if not os.path.exists("./3D_points/" + m): #if the pathway already exists, ignore it
			os.mkdir("./3D_points/" + m)
		else:
			continue
		if not os.path.exists("./files/" + m):
			os.mkdir("./files/" + m)
		else:
			continue
		if not os.path.exists("./results/" + m):
			os.mkdir("./results/" + m)
		for p in paths:
			if p == ".DS_Store":
				continue
			p = p[0:-4]
			if not os.path.exists("./3D_points/" + m + '/' + p):
				os.mkdir("./3D_points/" + m + '/' + p)
			if not os.path.exists("./files/" + m + '/' + p):
				os.mkdir("./files/" + m + '/' + p)
			if not os.path.exists("./results/" + m + '/' + p):
				os.mkdir("./results/" + m + '/' + p)
			create_slices(m,p)

#This function runs Dave's code to create image slices from a 3D volume.
def create_slices(model,path):
	images_path = "models/" + model + "/Images/OSMSC" + model.split('_')[0] + "-cm.vti"
	models_file = "models/" + model + "/Meshes/" + model + ".vtp"
	results_dir = "results/" + model + "/" + path
	path_dir = "models/" + model + "/Paths/" + path + ".pth"
	slice_increment = "1" #usually 10
	slice_width = "5"
	extract_slices = "True"
	os.system("python3 extract-2d-images.py --image-file " + images_path + " --path-file " + path_dir + " --model-file " + models_file + " --slice-increment " + slice_increment + " --path-sample-method number --slice-width " + slice_width + " --extract-slices " + extract_slices + " --results-directory " + results_dir)

#This function outputs the number of yaml files found, and outputs a file with the names of all the yaml files
def summary():
	yaml_count = count_yaml_files("./files")
	print("There are " + str(yaml_count) + " new training images!")
	write_files_txt("./files")

#this function takes in a pathways and returns the number of yaml files recursively found
def count_yaml_files(path):
    count = 0
    for file in glob.glob(path + "/**/*.yaml", recursive=True):
        if os.path.isfile(file):
            count += 1
    return count

#This function takes in a pathway and recursively finds all the '.yaml'; returns all the pathways in an array
def get_yaml_files(path):
    yaml_files = []
    for file in glob.glob(path + "/**/*.yaml", recursive=True):
        if os.path.isfile(file):
            yaml_files.append("./files/" + os.path.relpath(file, path))
    return yaml_files

#This function writes all the yaml files into 'files.txt'
def write_files_txt(path):
    yaml_files = get_yaml_files(path)
    with open('files.txt', 'w') as file:
        file.write('\n'.join(yaml_files))

#Given two 2-dimensional points, returns true if the two points are touching (including diagnolly), and false otherwise
def isNeighbor(p1,p2):
	x_true = True
	y_true = True
	if abs(p1[0]-p2[0]) > 1:
		x_true = False
	if abs(p1[1]-p2[1]) > 1:
		y_true = False
	return x_true and y_true

#This function takes in two 2-dimensional points and returns the euclidean distance between them
def euclideanDistance(p1,p2):
	dist = (p2[0]-p1[0]) **2 + (p2[1]-p1[1]) **2
	return dist ** 0.5

#This is an undefined function.
def findRadius():
	pass

def find_files_with_suffix(suffix, directory='./files'):
	file_paths = []
	for root, _, files in os.walk(directory):
		for filename in files:
			if filename.endswith(suffix):
				file_path = os.path.join(root, filename)
				file_paths.append(file_path)
	return file_paths

#This function takes in an array of pathways and removes the extension
#'.files/dir1/file1.X.txt' -> '.files/dir1/file1.'
def remove_file_extensions(pathways):
	modified_pathways = []

	for pathway in pathways:
		arr = pathway.split('/')
		arr[-1] = arr[-1].split('.')[0] + '.'
		modified_pathway = '/'.join(arr)
		modified_pathways.append(modified_pathway)

	return modified_pathways

def add_file_extensions(pathways, suffix):
    modified_pathways = [pathway + suffix for pathway in pathways]
    return modified_pathways

def write_array_to_file(my_array, output_file):
    # Open the file in write mode
    with open(output_file, 'w') as f_out:
        # Write each element of the array to a new line in the file
        for element in my_array:
            f_out.write(str(element) + '\n')

"""
Purpose: There may exist a file that has one pathway per line.
This function will read in the text file and turn this into an array.
"""
def file_to_array(file_path):
    # Initialize an empty list to store the pathways
    pathways_list = []

    # Read the file and extract the pathways
    with open(file_path, 'r') as f:
        for line in f:
            # Remove leading and trailing whitespaces and newline characters
            pathway = line.strip()
            # Append the pathway to the list
            pathways_list.append(pathway)

    return pathways_list



def create_new_yaml(yaml_file):
    # Load the YAML data from the existing file
    with open(yaml_file, 'r') as file:
        yaml_data = yaml.safe_load(file)

    # Create the new name with the current date
    current_date = date.today().strftime("%Y%m%d")
    name = f"{yaml_data['NAME']}_{current_date}"
    yaml_data['NAME'] = name

    # Update LOG_FILE, ITER_FILE, and MODEL_DIR with the new name
    yaml_data['LOG_FILE'] = f"{yaml_data['RESULTS_DIR']}/{name}/log/train.txt"
    yaml_data['ITER_FILE'] = f"{yaml_data['RESULTS_DIR']}/{name}/log/iter.txt"
    yaml_data['MODEL_DIR'] = f"{yaml_data['RESULTS_DIR']}/{name}/model"

    # Comment out TRAIN_PATTERNS and get all subdirectories as new TRAIN_PATTERNS
    yaml_data['TRAIN_PATTERNS'] = []

    directory = './files'
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            yaml_data['TRAIN_PATTERNS'].append(item_path.split('/')[-1])

    # Remove single quotes from the values
    yaml_data["TRAIN_PATTERNS"] = [pattern.strip("'") for pattern in yaml_data["TRAIN_PATTERNS"]]

    # Save the modified YAML data to the new file
    new_yaml_file = f"{name}.yaml"
    with open(new_yaml_file, 'w') as file:
        yaml.dump(yaml_data, file)

    return new_yaml_file
    




