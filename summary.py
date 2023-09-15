import numpy as np
import pandas as pd
import util
import PIL

#X_file should end in 'X.npy'
def get_gradient(X,Yp):
    # Apply Sobel filter to X image
    X_sobel = np.abs(np.gradient(X.astype(np.float32), axis=0)) + np.abs(np.gradient(X.astype(np.float32), axis=1))
    Yp_white_pixels = np.argwhere(Yp == 1)
    if len(Yp_white_pixels) == 0:
    	return None
    gradient = np.mean(X_sobel[Yp_white_pixels[:, 0], Yp_white_pixels[:, 1]])
    return round(gradient,3)

def get_eccentricity(Yp):
    white_pixels = np.where(Yp == 1)
    if len(white_pixels[0]) == 0:
        return None
    centroid_x = np.mean(white_pixels[0])
    centroid_y = np.mean(white_pixels[1])
    distance = np.sqrt((white_pixels[0] - centroid_x)**2 + (white_pixels[1] - centroid_y)**2)
    semi_major_axis = np.max(distance)
    semi_minor_axis = np.min(distance)
    eccentricity = np.sqrt(1 - (semi_minor_axis / semi_major_axis)**2)
    return round(eccentricity,3)

def get_std_dev(X,Yc):
    # Find white pixels in Y image
    Yc_white_pixels = np.argwhere(Yc == 1)
    if len(Yc_white_pixels) == 0:
        return None
    vessel_std_dev = np.std(X[Yc_white_pixels[:, 0], Yc_white_pixels[:, 1]])
    return round(vessel_std_dev,3)
def get_radius(Yc):
	area = len(np.argwhere(Yc==1))
	if area == 0:
		return 0
	radius = np.sqrt(1.0*area/np.pi)
	return radius

def normalize_X_image(X_file):
    X = np.load(X_file)
    try:
        if np.isclose(np.max(X),np.min(X)):
            return np.zeros((240, 240))
        else:
            norm_X = (2 * (X - X.min()) / (X.max() - X.min())) - 1  #between -1 and 1
            return norm_X
    except Exception as e:
    	print("An error occurred:", e)
    	print(np.max(X),np.min(X))

def get_attributes(file_prefix):
	#Name Files
	X_file = file_prefix + "X.npy"
	Yc_file = file_prefix + "Yc.npy"
	Yp_file = file_prefix + "Yp.npy"

	#Grab Images
	X = normalize_X_image(X_file)
	Yc = np.load(Yc_file)
	Yp = np.load(Yp_file)

	#Make calculations
	gradient = get_gradient(X,Yp)
	eccentricity = get_eccentricity(Yp)
	std_dev = get_std_dev(X,Yc)
	radius = get_radius(Yc)

	index = file_prefix.find('files')
	pathway = file_prefix[index:-1]
	pathway_arr = pathway.split('/')

	image = pathway_arr[1]
	path_name = pathway_arr[2]
	point = pathway_arr[3]
	return (pathway,image,path_name,point,radius,gradient,eccentricity,std_dev)

def find_all_image_attributes(root_dir = './files',csv_output_pwy='attributes.csv'):
	yaml_pathways = util.find_files_with_suffix('.yaml',directory = root_dir)

	data_prefixes = util.remove_file_extensions(yaml_pathways)
	attributes = [get_attributes(x) for x in data_prefixes]
	columns = ['pathway','image', 'path_name', 'point', 'radius','gradient','eccentricity','std_dev']
	df = pd.DataFrame(attributes, columns=columns)
	df.to_csv(csv_output_pwy, index=False)



if __name__ == "__main__":
	pass
	#find_all_image_attributes('/Users/noah/Desktop/Marsden/files/',"created_attributes_og.csv")
	#find_all_image_attributes(root_dir = '/Users/noah/Desktop/image-data-creation/files/',csv_output_pwy="created_attributes.csv")
