import os
import Model_class
import util
import summary
import perimeter
import Xo
import tidy

#Removes all unneseccary files
# os.system("find ./ -type d -name 'Simulations' -exec rm -r {} +")
# os.system("find ./ -type d -name 'Segmentations' -exec rm -r {} +")
# os.system("find ./ -type d -name 'flow-files' -exec rm -r {} +")

"""
This is the main file to run.
We assume that the models are stored in the './models' directory.
"""

util.create_directories("./models")
util.create_images()
print("Created Images and Directories")

#This creates files which will be used for filtering images and displaying them
perimeter.extract_perimeter() #This file creates a file with just the perimeter outlined
Xo.create_Xo_images("./files") #This file creates a 'Xo' file with the perimeter overlayed on top of the original image.
print("Created Complimentary Files")

#Filtering to only include good images and save these to 'files_clean.txt'
summary.find_all_image_attributes()
tidy.filter()
print("Applied Filtering to Images")

#Creating yaml file (adjust this)
#util.create_new_yaml("googlenet_c30_train300k_aug10_clean_base.yaml")

#zipping filters and load files from 'files_clean.txt'
tidy.create_zip_with_selected_files()


#This removes some extraneous files that would take up lots of storage
os.system("find ./ -name '.DS_Store' -type f -delete")
os.system("find results/ -type f -delete")
os.system("find 3D_points/ -type f -delete")
os.system("rm -r 3D_points")

