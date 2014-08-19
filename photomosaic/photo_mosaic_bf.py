#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Photomosaic - Just for fun
"""

from PIL import Image
from colormath.color_objects import LabColor,sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976

__author__ = 'Alexandre Pinto'
__email__ = "alexandpinto@gmail.com"
__date__='2014'

def build_photomosaic(mosaic_im,target_im,block_width,block_height,colordiff,new_filename):

	mosaic_width=mosaic_im.size[0]				#dimensions of the target image
	mosaic_height=mosaic_im.size[1]

	target_width=target_im.size[0]				#dimensions of the target image
	target_height=target_im.size[1]

	target_grid_width,target_grid_height=get_grid_dimensions(target_width,target_height,block_width,block_height)		#dimensions of the target grid
	mosaic_grid_width,mosaic_grid_height=get_grid_dimensions(mosaic_width,mosaic_height,block_width,block_height)		#dimensions of the mosaic grid

	target_nboxes=target_grid_width*target_grid_height
	mosaic_nboxes=mosaic_grid_width*mosaic_grid_height

	print "Computing the average color of each photo in the mosaic..."
	mosaic_color_averages=compute_block_avg(mosaic_im,block_width,block_height)
	print "Computing the average color of each block in the target photo ..."
	target_color_averages=compute_block_avg(target_im,block_width,block_height)

	print "Computing photomosaic ..."
	photomosaic=[0]*target_nboxes
	for n in xrange(target_nboxes):
		print "%.2f " % (n/float(target_nboxes)*100)+"%"
		for z in xrange(mosaic_nboxes):
			current_diff=colordiff(target_color_averages[n],mosaic_color_averages[photomosaic[n]])
			candidate_diff=colordiff(target_color_averages[n],mosaic_color_averages[z])

			if(candidate_diff<current_diff):
				photomosaic[n]=z

	print "Building final image ..."
	build_final_solution(photomosaic,mosaic_im,target_nboxes,target_im,target_grid_width,block_height,block_width,new_filename)

def build_initial_solution(target_nboxes,mosaic_nboxes):
	candidate=[0]*target_nboxes

	for n in xrange(target_nboxes):
		candidate[n]=random.randint(0,mosaic_nboxes-1)

	return candidate

def build_final_solution(best,mosaic_im,target_nboxes,target_im,target_grid_width,block_height,block_width,new_filename):

	for n in xrange(target_nboxes):

		i=(n%target_grid_width)*block_width				#i,j -> upper left point of the target image
		j=(n/target_grid_width)*block_height

		box = (i,j,i+block_width,j+block_height)		

		#get the best photo from the mosaic
		best_photo_im=get_block(mosaic_im,best[n],block_width,block_height)

		#paste the best photo found back into the image
		target_im.paste(best_photo_im,box)

	target_im.save(new_filename)


#get dimensions of the image grid
def get_grid_dimensions(im_width,im_height,block_width,block_height):
	grid_width=im_width/block_width		#dimensions of the target image grid
	grid_height=im_height/block_height
	return grid_width,grid_height

#compute the fitness of given candidate solution
def fitness(candidate,mosaic_color_averages,mosaic_nboxes,target_color_averages,target_nboxes):
	error=0.0
	for i in xrange(target_nboxes):
		error+=colordiff_rgb(mosaic_color_averages[candidate[i]],target_color_averages[i])
	return error

#get a list of color averages, i.e, the average color of each block in the given image
def compute_block_avg(im,block_height,block_width):

	width=im.size[0]
	height=im.size[1]

	grid_width_dim=width/block_width					#dimension of the grid
	grid_height_dim=height/block_height

	nblocks=grid_width_dim*grid_height_dim				#number of blocks

	avg_colors=[]
	for i in xrange(nblocks):
		avg_colors+=[avg_color(get_block(im,i,block_width,block_height))]
	return avg_colors

#returns the average RGB color of a given image
def avg_color(im):
	avg_r=avg_g=avg_b=0.0
	pixels=im.getdata()
	size=len(pixels)
	for p in pixels:
		avg_r+=p[0]/float(size)
		avg_g+=p[1]/float(size)
		avg_b+=p[2]/float(size)

	return (avg_r,avg_g,avg_b)

#get the nth block of the image
def get_block(im,n,block_width,block_height):

	width=im.size[0]

	grid_width_dim=width/block_width						#dimension of the grid

	i=(n%grid_width_dim)*block_width						#i,j -> upper left point of the target block
	j=(n/grid_width_dim)*block_height

	box = (i,j,i+block_width,j+block_height)
	block_im = im.crop(box)
	return block_im


#calculate color difference of two pixels in the RGB space
#less is better
def colordiff_rgb(pixel1,pixel2):

	delta_red=pixel1[0]-pixel2[0]
	delta_green=pixel1[1]-pixel2[1]
	delta_blue=pixel1[2]-pixel2[2]

	fit=delta_red**2+delta_green**2+delta_blue**2
	return fit

#http://python-colormath.readthedocs.org/en/latest/index.html
#calculate color difference of two pixels in the L*ab space
#less is better
def colordiff_lab(pixel1,pixel2):

	#convert rgb values to L*ab values
	rgb_pixel_1=sRGBColor(pixel1[0],pixel1[1],pixel1[2],True)
	lab_1= convert_color(rgb_pixel_1, LabColor)

	rgb_pixel_2=sRGBColor(pixel2[0],pixel2[1],pixel2[2],True)
	lab_2= convert_color(rgb_pixel_2, LabColor)

	#calculate delta e
	delta_e = delta_e_cie1976(lab_1, lab_2)
	return delta_e


if __name__ == '__main__':
	mosaic="images/25745_avatars.png"
	targets=["images/lightbulb.png","images/steve.jpg","images/sunday.jpg","images/spheres.png","images/kiss.jpg"]
	target=targets[0]
	mosaic_im=Image.open(mosaic)
	target_im=Image.open(target)
	new_filename=target.split(".")[0]+"_photomosaic.png"
	colordiff=colordiff_rgb

	build_photomosaic(mosaic_im,target_im,48,48,colordiff,new_filename)
