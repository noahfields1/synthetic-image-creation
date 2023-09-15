#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name

import math
import vtk
import numpy as np
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

class Image(object):

    def __init__(self, params):
        self.parameters = params
        self.volume = None
        self.graphics = None
        self.paths = None
        self.logger = logging.getLogger(get_logger_name())
        self.greyscale_lut = None
        self.hue_lut = None 
        self.sat_lut = None
        self.colors = vtk.vtkNamedColors()
        self.results_dir = params.results_directory + "/"

    def create_greyscale_lut(self, scalar_range):
        imin = scalar_range[0]
        imax = scalar_range[1]
        table = vtk.vtkLookupTable()
        table.SetRange(imin, imax) # image intensity range
        table.SetValueRange(0.0, 1.0) # from black to white
        table.SetSaturationRange(0.0, 0.0) # no color saturation
        table.SetRampToLinear()
        table.Build()
        self.greyscale_lut = table

    def create_hue_lut(self, scalar_range):
        ''' Create a lookup table that consists of the full hue circle (from HSV).
        '''
        imin = scalar_range[0]
        imax = scalar_range[1]
        table = vtk.vtkLookupTable()
        table.SetTableRange(imin, imax)
        table.SetHueRange(0, 1)
        table.SetSaturationRange(1, 1)
        table.SetValueRange(1, 1)
        table.Build()
        self.hue_lut = table

    def create_sat_lut(self, scalar_range):
        imin = scalar_range[0]
        imax = scalar_range[1]
        table = vtk.vtkLookupTable()
        table.SetTableRange(imin, imax)
        table.SetHueRange(.6, .6)
        table.SetSaturationRange(0, 1)
        table.SetValueRange(1, 1)
        table.Build()
        self.sat_lut = table

    def read_volume(self):
        ''' Read in a 3D image volume.
        '''
        filename, file_extension = path.splitext(self.parameters.image_file_name)
        reader = None
        if file_extension == ".vti":
            reader = vtk.vtkXMLImageDataReader()
        reader.SetFileName(self.parameters.image_file_name)
        reader.Update()
        self.volume = reader.GetOutput()

        self.extent = self.volume.GetExtent()
        self.width = self.extent[1] - self.extent[0]
        self.height = self.extent[3] - self.extent[2]
        self.depth = self.extent[5] - self.extent[4]
        self.scalar_range = self.volume.GetScalarRange()
        self.dimensions = self.volume.GetDimensions()
        self.spacing = self.volume.GetSpacing()
        self.origin = self.volume.GetOrigin()
        self.bounds = self.volume.GetBounds()
        self.scalars = self.volume.GetPointData().GetScalars()

        self.create_greyscale_lut((0,200))
        #self.create_greyscale_lut(self.scalar_range)
        self.create_hue_lut(self.scalar_range)
        self.create_sat_lut(self.scalar_range)

        '''
        image_point_data = imageDataVTK.GetPointData()
        image_data = vtkNumPy.vtk_to_numpy(image_point_data.GetArray(0))
        '''

        self.logger.info("Volume: ")
        self.logger.info("  dimensions: %s" % str(self.dimensions))
        self.logger.info("  extent: %s" % str(self.extent))
        self.logger.info("  spacing: %s" % str(self.spacing))
        self.logger.info("  origin: %s" % str(self.origin))
        self.logger.info("  bounds: %s" % str(self.bounds))
        self.logger.info("  width: %d" % self.width)
        self.logger.info("  height: %d" % self.height)
        self.logger.info("  depth: %d" % self.depth)
        self.logger.info("  scalar_range: %s" % str(self.scalar_range))

        self.graphics.add_sphere(self.origin, radius=0.2)

        x0, y0, z0 = self.origin
        xSpacing, ySpacing, zSpacing = self.spacing
        xMin, xMax, yMin, yMax, zMin, zMax = self.extent
        center = [x0 + 0.5*xSpacing * (xMax-1), y0 + 0.5*ySpacing * (yMax-1), z0 + 0.5*zSpacing * (zMax-1)]
        #self.graphics.add_sphere(center, radius=0.1, color=[1.0,0.0,0.0])

    def display_edges(self):
        outline = vtk.vtkOutlineFilter()
        outline.SetInputData(self.volume)
        outline.Update()

        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(outline.GetOutput())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetColor(self.colors.GetColor3d("Black"))
        self.graphics.add_actor(actor)

    def display_axis_slice(self, axis, index):
        slice_colors = vtk.vtkImageMapToColors()
        slice_colors.SetInputData(self.volume)
        slice_colors.SetLookupTable(self.greyscale_lut)
        #slice_colors.SetLookupTable(self.hue_lut)
        #slice_colors.SetLookupTable(self.sat_lut)
        slice_colors.Update()

        slice = vtk.vtkImageActor()
        slice.GetMapper().SetInputData(slice_colors.GetOutput())

        if axis == 'i':
            imin = index 
            imax = index
            jmin = 0
            jmax = self.height
            kmin = 0
            kmax = self.depth

        elif axis == 'j':
            imin = 0
            imax = self.width
            jmin = index
            jmax = index 
            kmin = 0
            kmax = self.depth

        elif axis == 'k':
            imin = 0
            imax = self.width
            jmin = 0
            jmax = self.height
            kmin = index
            kmax = index 

        slice.SetDisplayExtent(imin,imax,jmin,jmax,kmin,kmax);
        slice.ForceOpaqueOn()
        slice.PickableOff()
        self.graphics.add_actor(slice)

    def extract_slice(self, path_data, verbose=False):
        '''Extract a 2D image slice from the image volume.
        '''
        point_id = path_data.id
        origin = path_data.point
        #name = path_data.name
        tangent = np.array(path_data.tangent)
        normal = np.array(path_data.rotation)
        binormal = np.cross(tangent, normal)

        if verbose:
            print(" ")
            print("---------- Image Extract Slice ----------") 
            print("point id: " + str(point_id))
            print("origin: " + str(origin))
            print("tangent: " + str(tangent))
            print("normal: " + str(normal))
            print("binormal: " + str(binormal))

        ## Define the slice plane.
        slice_plane = vtk.vtkPlane()
        slice_plane.SetOrigin(origin[0], origin[1], origin[2])
        slice_plane.SetNormal(tangent[0], tangent[1], tangent[2])

        ## Create interpolate slice plane points.
        #
        spacing = min(self.spacing) / 2.0
        #print("Spacing: {0:g} ".format(spacing))
        #xSpacing, ySpacing, zSpacing = self.spacing
        w = self.parameters.slice_width
        #w = self.parameters.slice_width * spacing
        num_u = int(w/spacing)
        num_v = int(w/spacing)
        #print("num_u: {0:d} ".format(num_u))
        u = normal
        v = binormal
        pt0 = origin - w * (u + v) / 2.0
        du = spacing
        dv = spacing 
        
        points = vtk.vtkPoints()
        for j in range(num_v):
            for i in range(num_u):
                pt = pt0 + i*du*u + j*dv*v
                #print("{0:d}  {1:d}  pt {2:s}".format(i, j, str(pt)))
                points.InsertNextPoint(pt[0], pt[1], pt[2])
        #_for j in range(num_v)
        ## Create probe used to interpolate image volume.
        #
        pts_polydata = vtk.vtkPolyData()
        pts_polydata.SetPoints(points)

        probe = vtk.vtkProbeFilter()
        probe.SetSourceData(self.volume)
        probe.SetInputData(pts_polydata)
        probe.Update()

        data = probe.GetOutput().GetPointData().GetScalars()
        num_values = data.GetNumberOfTuples()
        values = vtk.vtkDoubleArray()
        values.SetNumberOfValues(num_values);
  
        #print("Interpolated data:")
        for i in range(data.GetNumberOfTuples()):
            val = data.GetValue(i)
            values.SetValue(i, val);
            #print(val)

        ## Create image data and points.
        #
        #image_points = vtk.vtkPoints()
        image_data = vtk.vtkImageData()
        image_data.SetDimensions(num_u, num_u, 1)
        image_data.AllocateScalars(vtk.VTK_DOUBLE, 1)
        dims = image_data.GetDimensions()

        n = 0
        for j in range(num_v): 
            for i in range(num_u): 
                #pixel = image_data.GetScalarPointer(i,j,0)
                #pixel = values.GetValue(n)
                image_data.SetScalarComponentFromDouble(i,j,0,0,values.GetValue(n))
                n += 1
        
        image_file_name = self.results_dir + "image_slice_" + point_id + ".vti"
        image_writer = vtk.vtkXMLImageDataWriter()
        image_writer.SetFileName(image_file_name)
        image_writer.SetInputData(image_data)
        image_writer.Write()
        pts = []
        ## Show the outline of the slice plane.
        pt1 = pt0 + 0*du*u + 0*dv*v
        pt2 = pt0 + 0*du*u + (num_v-1)*dv*v
        a1 = pt1
        points.InsertNextPoint(a1)
        pts.append(pt1)
        self.graphics.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)
        pt1 = pt2 
        pt2 = pt0 + (num_u-1)*du*u + (num_v-1)*dv*v
        b1 = pt1
        points.InsertNextPoint(b1)
        pts.append(pt1)
        self.graphics.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)
        pt1 = pt2 
        pt2 = pt0 + (num_u-1)*du*u + 0*dv*v
        c1 = pt1
        points.InsertNextPoint(c1)
        pts.append(pt1)
        self.graphics.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)
        pt1 = pt2 
        pt2 = pt0 + 0*du*u + 0*dv*v
        d1 = pt1
        points.InsertNextPoint(d1)
        pts.append(pt1)
        self.graphics.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)
        f = open(self.results_dir.replace('results','3D_points').replace('Mesh/','').replace('Model/','') + '3D_points_' + str(point_id) + '.txt','w')
        f.write(str(a1[0]) + ' ' + str(a1[1]) + ' ' + str(a1[2]) + '\n')
        f.write(str(b1[0]) + ' ' + str(b1[1]) + ' ' + str(b1[2]) + '\n')
        f.write(str(c1[0]) + ' ' + str(c1[1]) + ' ' + str(c1[2]) + '\n')
        f.write(str(d1[0]) + ' ' + str(d1[1]) + ' ' + str(d1[2]) + '\n')
        f.close()
        """
                b1 =b1 -  d1
                a1 =a1 -  d1
                c1 =c1 -  d1
                vec1 = a1-b1
                vec2 = b1-c1
                normal_vec = np.cross(vec1,vec2)
                normal_vec = normal_vec/np.linalg.norm(normal_vec) #normalize
                a,b,c = normal_vec
                d = -b1[0] * a - b1[1] * b - b1[2] * c
                cos_theta = c/((a**2 + b**2 + c**2)**0.5)
                sin_theta = ((a**2 + b**2)/(a**2 + b**2 + c**2))**0.5
                mu_1 = b/((a**2 + b**2 + c**2)**0.5)
                mu_2 = -a/((a**2 + b**2 + c**2)**0.5)
                mat_1 = [cos_theta + (mu_1**2) * (1-cos_theta),mu_1 * mu_2 * (1-cos_theta),mu_2 * sin_theta]
                mat_2 = [mu_1 * mu_2 * (1-cos_theta), cos_theta + (mu_2**2) * (1-cos_theta), -1 * mu_1 * sin_theta]
                mat_3 = [-1 * mu_2 * sin_theta, mu_1 * sin_theta, cos_theta]
                mat = [mat_1,mat_2,mat_3]
                n = normal_vec
                denom = np.sqrt(n[0]**2 + n[1]**2)
                m = [[n[0]/denom,n[1]/denom,0],[-n[1]/denom,n[0]/denom,0],[0,0,1]]
                #print("coefficients")
                #print(a,b,c,d)
                print("Blah")
                for i in [a1,b1,c1,d1]:
                    blah = np.matmul(mat,i)
                    #blah = i[0] * a + i[1] * b + i[2] * c
                    print(blah)
                #print("Claw")
                exit()
                #print(pt0)
                #print(origin)
                #print(path_data.point)
        ## Show interpolation points.
        vertexFilter = vtk.vtkVertexGlyphFilter()
        vertexFilter.SetInputData(pts_polydata)
        vertexFilter.Update()
        polydata = vtk.vtkPolyData()
        polydata.ShallowCopy(vertexFilter.GetOutput())
        polydata.GetPointData().SetScalars(values)
        #print("Scalar range: " + str(polydata.GetScalarRange()))
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.SetLookupTable(self.greyscale_lut)
        mapper.SetScalarRange(polydata.GetScalarRange())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetPointSize(4)
        #actor.GetProperty().SetColor(1.0, 1.0, 0.0)
        self.graphics.add_actor(actor)"""
