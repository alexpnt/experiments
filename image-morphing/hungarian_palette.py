#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hungarian algorithm - Solving an assignment problem - Morphing an image into another with the same color palette - Just for fun
"""

from copy import deepcopy
from PIL import Image
from colormath.color_diff import delta_e_cie1976
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor,sRGBColor
from munkres import Munkres,print_matrix

__author__ = 'Alexandre Pinto'
__email__ = "alexandpinto@gmail.com"
__date__='2014'

#generates a new individual(palette) with the same dimensions as the source but with its own colours
def generate_palette(source_im,palette_im):

	source_size=source_im.size
	palette_columns=source_size[0]
	palette_rows=source_size[1]

	new_palette=Image.new(palette_im.mode,(palette_columns,palette_rows))

	palette_pixels=list(palette_im.getdata())
	new_palette.putdata(palette_pixels)

	return new_palette

#calculate color difference of two pixels in the RGB space
#the less the better
def colordiff_rgb(source_pixel,palette_pixel):

	delta_red=source_pixel[0]-palette_pixel[0]
	delta_green=source_pixel[1]-palette_pixel[1]
	delta_blue=source_pixel[2]-palette_pixel[2]

	fit=delta_red**2+delta_green**2+delta_blue**2
	return fit

#http://python-colormath.readthedocs.org/en/latest/index.html
#calculate color difference of two pixels in the L*ab space
#the less the better
#pros: better results, cons: very slow
def colordiff_lab(source_pixel,palette_pixel):

	#convert rgb values to L*ab values
	rgb_pixel_source=sRGBColor(source_pixel[0],source_pixel[1],source_pixel[2],True)
	lab_source= convert_color(rgb_pixel_source, LabColor)

	rgb_pixel_palette=sRGBColor(palette_pixels[0],palette_pixels[1],palette_pixels[2],True)
	lab_palette= convert_color(rgb_pixel_palette, LabColor)

	#calculate delta e
	delta_e = delta_e_cie1976(lab_source, lab_palette)
	return delta_e

#compute the cost matrix required for hungarian algorithm
#each cell represents the cost of placing the ith pixel in the jth position
def generate_cost_matrix(source_im,palette_im):
	source_pixels=list(source_im.getdata())
	palette_pixels=list(palette_im.getdata())
	dim=len(source_pixels)

	cost_matrix=[[0]*dim]*dim
	for i in xrange(dim):
		print "%.2f " % (i/float(dim)*100)+"%"
		for j in xrange(dim):
			cost_matrix[i][j]=colordiff_rgb(source_pixels[j],palette_pixels[i])

	return cost_matrix


#generates the final image using the solution to the assignment problem, 
#i.e, the best matching between the initial and final positions of each pixel that gives the lowest cost
def generate_best_palette(palette_im,indexes):
	palette_pixels=list(palette_im.getdata())
	new_alette_pixels=deepcopy(palette_pixels)

	for row, column in indexes:
		new_alette_pixels[row]=palette_pixels[column]

	new_palette=Image.new(palette_im.mode,(palette_im.size[0],palette_im.size[1]))
	new_palette.putdata(new_alette_pixels)
	new_palette.save("best_palette.png");



if __name__ == '__main__':
	source="american_gothic.png"
	palette="mona_lisa.png"

	source_im=Image.open(source)
	palette_im=Image.open(palette)

	new_palette=generate_palette(source_im,palette_im)

	print "building cost matrix (this may take a while)..."
	cost_matrix=generate_cost_matrix(source_im,new_palette)
	
	print "building indexes (this may take a while)..."
	m = Munkres()
	indexes = m.compute(cost_matrix)

	print "reconstructing the final image (this may take a while) ..."
	generate_best_palette(palette_im,indexes)
	print "done!"