import util
import tools #from the github repository
from skimage.transform import resize
from vtk.util.numpy_support import vtk_to_numpy as v2n
import matplotlib.image
import numpy as np
import PIL 
import yaml
import vtk

#Model Class
class Model():
	def __init__(self,model_name, pathway):
		self.model_name = model_name
		self.pathway = pathway
	def filter_3Dpoints():
		pass

#Branch Class
class Branch(Model):
	def __init__(self, Model, branch_name):
		self.model_name = Model.model_name
		self.pathway = Model.pathway
		self.branch_name = branch_name

#Image Class
#Many of the attributes are unique to speficic images
class Image(Branch):
	def __init__(self, Branch, image_name):
		self.model_name = Branch.model_name
		self.pathway = Branch.pathway
		self.branch_name = Branch.branch_name
		self.image_name = image_name
		self.path_id = None
		self.yaml_file = None
		self.points3D_file = None
		self.points3D = []
		self.translation3D = None
		self.points2D = []
		self.points2D_filtered = [] #This only includes points that are in the vessel of interest
		self.image_corners3D = []
		self.radius = None
		self.BifurcationID = None
		self.spacing = None
		self.dimensions = 160
		self.extent = 240
		self.centerlines_vtp_file = None
		self.model_vtp_file = None #is not used
		self.mesh_vtp_file = None #for getting point data (extracting from vtp file was not working)
		self.vti_file = None
		self.X_np_file = None
		self.X_png_file = None
		self.Y_png_file = None
		self.Yc_np_file = None
		self.Yc_png_file = None
		self.ratio = None

	"""Each image uses specific files and filenames. This function assumes that there is a folder named
	./3D_points, ./centerlines, ./results, and ./files already in the relative location. ./centerlines is not
	created within the code, but may be acquired through the Marsden Lab.
	"""
	def generateFileNames(self):
		self.points3D_file = "./3D_points/" + self.model_name + "/" + self.branch_name + "/3D_points_" + self.image_name + ".txt"
		self.centerlines_vtp_file = "./centerlines/" + self.model_name + ".vtp"
		self.model_vtp_file = "./results/" + self.model_name + "/Model/" + self.branch_name + "/model_slice_" + self.image_name + ".vtp"
		self.mesh_vtp_file = "./results/" + self.model_name + "/" + self.branch_name + "/model_slice_" + self.image_name + ".vtp"
		self.vti_file = "./results/" + self.model_name + "/" + self.branch_name + "/image_slice_" + self.image_name + ".vti"
		self.yaml_file = "./files/" + self.model_name + "/" + self.branch_name + "/" + self.image_name + ".yaml"
		self.X_np_file = "./files/" + self.model_name + "/" + self.branch_name + "/" + self.image_name + ".X.npy"
		self.X_png_file = "./files/" + self.model_name + "/" + self.branch_name + "/" + self.image_name + ".X.png"
		self.Y_np_file = "./files/" + self.model_name + "/" + self.branch_name + "/" + self.image_name + ".Y.npy"
		self.Y_png_file = "./files/" + self.model_name + "/" + self.branch_name + "/" + self.image_name + ".Y.png"
		self.Yc_np_file = "./files/" + self.model_name + "/" + self.branch_name + "/" + self.image_name + ".Yc.npy"
		self.Yc_png_file = "./files/" + self.model_name + "/" + self.branch_name + "/" + self.image_name + ".Yc.png"

	"""
	To run Gabriel's code, a corresponding yaml file is required for each image set (label,input).
	Gabriel's neural network takes in np files, which is why the yaml file stores the numpy files for
	'X' and 'Yc'. The rest of the features are extraneous. 
	"""
	def generateYAML(self):
		yaml_dict = {'X':self.X_np_file,'Y':self.Y_np_file,'Yc':self.Yc_np_file,'dimensions':self.dimensions,'extent':self.extent,'image':self.model_name,'path_id':'','path_name':self.branch_name,'point':int(self.image_name),'radius':self.radius,'spacing':0.029,'bifurcation_id':self.BifurcationID,'ratio (circum^2/area)':round(self.ratio,2)}
		with open(self.yaml_file, 'w') as file:
			documents = yaml.dump(yaml_dict,file)

	"""
	We take a file containing the points of interest in a 3-dimensional volume
	and turn them into a 2-dimension plane. Note: these points were already on the
	same plane in the 3-dimensional volume so it's not hard to turn this into a 2-dimensional plane.
	"""
	def getPoints(self):
		#We read in the points form the points3D_file, and store these in the 'pts' array.
		pts = []
		f = open(self.points3D_file,'r')
		for line in f.readlines():
			coord = line.split()
			x = (float(coord[0]))
			y = (float(coord[1]))
			z = (float(coord[2]))
			pts.append(np.array([x,y,z]))
		#new_origin = pts[0]
		self.translation3D = pts[0]

		#For simplicity, we translate all the points so the plane goes through the origin: (0,0,0)
		for i in range(len(pts)):
			self.points3D.append(pts[i] - self.translation3D)
		"""
		The first four points in the array are obtained from the 'vti' image file.
		So these are part of no vessel and indicate the boundaries of our image.
		This is useful for scaling.
		"""
		self.image_corners = self.points3D[0:4]

		#linear algebra is done
		vec1 = self.image_corners[1] - self.image_corners[0] #points are being turned into vectors relative to the first point: pts[0]
		vec2 = self.image_corners[2] - self.image_corners[0]
		vec3 = self.image_corners[3] - self.image_corners[0]
		new_pts = []
		for i in self.points3D[4:]:
			a = int((np.dot(i,vec1)/np.dot(vec1,vec1)) * 240) #vessel points are turned into a linear combination of vec1 and vec3
			b = int((np.dot(i,vec3)/np.dot(vec3,vec3)) * 240)
			if a < 0 or a > 239 or b < 0 or b > 239: #If points are out of the frame, we ignore them
				continue
			new_pts.append((a,b))
		self.points2D = new_pts #the remaining points are added to a 2-dimensional array of points

	def connectPoints(self):
		#Reading in the points from 'path_2D'

		points = list(set(self.points2D))

		#If there are no points (or just the origin), we get rid of the point
		#This is the case when a pathway point is created without a segmentation
		if len(points) <= 1:
			return

		#The origin for an image is established (this is also the center of a 240x240 frame)
		origin = (121,121)
		min_val = 10000
		min_index = None

		"""
		Find the closest point to the origin.
		We assume that this point is in the vessel of interest.
		"""
		for i in range(0,len(points)):
			dist_from_origin = ((origin[0] - points[i][0])**2 + (origin[1] - points[i][1])**2)**0.5
			if dist_from_origin < min_val:
				min_val = dist_from_origin
				min_index = i
		first_point = points.pop(min_index)

		"""
		Using the first point found (old_point),
		we recursively find the next closest point to our current point until we
		come back to the first point found. This is when the circle (vessel) is 
		complete, and we can assume that the other points are part of a seperate
		vessel.
		"""
		old_point = first_point
		next_point = None
		next_point_index = None
		min_val = 10000
		vessel = []
		while next_point != first_point and len(points) != 0:
			min_val = 10000
			next_point_index = None
			for i in range(0,len(points)):
				dist_from_old_point = self.scoreDistance(util.euclideanDistance,old_point,points[i])
				if dist_from_old_point < min_val:
					min_val = dist_from_old_point
					next_point_index = i
			next_point = points[next_point_index]
			old_point = points.pop(next_point_index)
			vessel.append(old_point)
			if len(vessel) == 10:
				points.append(first_point)

		#add the first point back again, so we have a complete circle
		vessel.append(vessel[0])
		
		#Recursively go through all of the points and add the midpoints to the vessels
		#until all of the points are connected
		finished = False
		i = 0
		while not finished:
			if not util.isNeighbor(vessel[i],vessel[i+1]):
				x_mid = round((vessel[i][0] + vessel[i+1][0])/2)
				y_mid = round((vessel[i][1] + vessel[i+1][1])/2)
				midpoint = (x_mid,y_mid)
				vessel.insert(i+1,midpoint)
				i = i - 1
			i += 1
			if i == len(vessel)-1:
				finished = True

		"""
		Once we have the lining of our vessel, we use recursive backtracking
		(starting from the mean point of the vessel) to fill in the cirlce, and we 
		store all of the points in the set 'used'.
		"""
		#start = [(121,121)]
		used = set(vessel)
		sum_1 = sum(t[0] for t in used)
		sum_2 = sum(t[1] for t in used)
		start = [(int(sum_1/len(used)), int(sum_2/len(used)))]
		while len(start) != 0:
			next = start.pop(0)
			if next in used:
				continue
			if next[1] == 239 or next[1] == 0 or next[0] == 0 or next[0] == 239:
				used.add(next)
				return
			used.add(next)
			if (next[0]+1,next[1]) not in used:
				start.append((next[0]+1,next[1]))
			if (next[0],next[1]+1) not in used:
				start.append((next[0],next[1]+1))
			if (next[0]-1,next[1]) not in used:
				start.append((next[0]-1,next[1]))
			if (next[0],next[1]-1) not in used:
				start.append((next[0],next[1]-1))
		
		#If the vessel is not in the center, we don't use this vessel
		if (121,121) not in used:
			used.clear()
			return

		#This is a heuristic way to calculate radius based on A=pi * r^2.
		self.radius = round((len(used)/np.pi) ** 0.5,2)

		#This is the ratio between the circumference and the area
		#This is a heuristic measure for ho
		self.ratio = (len(set(vessel))**2)/len(used)
		
		self.points2D_filtered = used




		

	def scoreDistance(self,scorefxn,p1,p2):
		return scorefxn(p1,p2)

	def getBifurcationID(self): 
		#some model will have vtp files for each slice, some will only have them for centerlines
		#The code in the subsequent 4 lines only works for some of the models.
		# vtp = tools.read_geo(self.model_vtp_file)
		# point_data, _, points = tools.get_all_arrays(vtp.GetOutput())
		# bifurcationId = point_data['BifurcationId']
		# self.BifurcationID = int(bifurcationId[0])

		# Load the VTP file
		reader = vtk.vtkXMLPolyDataReader()
		reader.SetFileName(self.centerlines_vtp_file)
		reader.Update()

		# Get the vtkPolyData object
		polydata = reader.GetOutput()

		# Get the points and bifurcation IDs from the vtkPolyData object
		centerline_points = v2n(polydata.GetPoints().GetData())
		bifurcation_ids = v2n(polydata.GetPointData().GetArray("BifurcationId"))

		#The mean of all the points acts as the center of the vessel. Potentially problematic
		#beacuse we include multiple vessels. We add self.translation3D because all of these
		#3D points were translated.
		mean = np.mean(self.points3D, axis=0) + self.translation3D 

		# Define the query point
		query_point = mean  # replace with your own query point

		# Create a vtkPoints object to store the point cloud
		points = vtk.vtkPoints()

		# Add some points to the point cloud
		for i in centerline_points:
			points.InsertNextPoint(i[0],i[1],i[2])

		# Create a vtkKdTree object to search the point cloud
		kd_tree = vtk.vtkKdTree()
		kd_tree.BuildLocatorFromPoints(points)

		# Find the closest point in the point cloud to the query point
		closestPoint = vtk.mutable(0.2)
		closest_point_id = kd_tree.FindClosestPoint(query_point,closestPoint)

		# Get the BifurcationID of the nearest point
		bifurcation_id = int(bifurcation_ids[closest_point_id])
		self.BifurcationID = bifurcation_id

	"""
	#We can create X (raw input), Y (2-dimensionl points w/ all vessel outlines),
	Yc (2-dimensional points w/ just vessel of interest, and vessel filled in) images.
	This function creates these images based on one of the 3 input options: 'X','Y','Yc'.
	"""
	def createImg(self,image_type):
		arr = np.zeros((240,240))

		if image_type == "X":
			reader = vtk.vtkXMLImageDataReader()
			reader.SetFileName(self.vti_file)
			reader.Update()
			vtiimage = reader.GetOutput()
			extent = vtiimage.GetExtent()
			width = extent[1] - extent[0] + 1
			height = extent[3] - extent[2] + 1
			image_data = np.reshape(v2n(vtiimage.GetPointData().GetArray(0)), (width, height))

			# Resize the array to 240 by 240
			resized_image_data = resize(image_data, (240, 240), anti_aliasing=True)
			np.save(self.X_np_file,resized_image_data.astype(np.int16)) #saving npy image

			matplotlib.image.imsave('temp.png', resized_image_data,cmap='gray')
			img = PIL.Image.open('temp.png').convert('L')
			img.save(self.X_png_file) #saving png image

		elif image_type == "Yc":
			for i in self.points2D_filtered:
				arr[i[0],i[1]] = 1

			arr = arr.astype(np.uint8)
			im = PIL.Image.fromarray(arr * 255)
			im.save(self.Yc_png_file)
			np.save(self.Yc_np_file,arr)

		elif image_type == "Y":
			for i in self.points2D:
				arr[i[0],i[1]] = 1
			arr[121,121] = 1
			
			arr = arr.astype(np.uint8)
			im = PIL.Image.fromarray(arr * 255)
			im.save(self.Y_png_file)
			np.save(self.Y_np_file,arr)
		

