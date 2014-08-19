#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Brute Force - Morphing an image into another with the same color palette - Just for fun
"""

import random
from math import log
from copy import deepcopy
from operator import itemgetter
from PIL import Image
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor,sRGBColor
from colormath.color_diff import delta_e_cie1976

__author__ = 'Alexandre Pinto'
__email__ = "alexandpinto@gmail.com"
__date__='2014'

def search(source_im,palette_im,colordiff,new_filename):

	columns=source_im.size[0]
	rows=source_im.size[1]
	size=columns*rows

	#pixels
	source_pixels=list(source_im.getdata())
	palette_pixels=list(palette_im.getdata())

	#current and new order of pixels
	current_palete_order=[i for i in xrange(size)]
	random.shuffle(current_palete_order)
	new_palette_order=[]


	for i in xrange(size):
		print "%.2f " % (i/float(size)*100)+"%"
		best_order=current_palete_order[0]
		index=0
		best_index=0
		best_diff=colordiff(palette_pixels[best_order],source_pixels[i])
		for order in current_palete_order:
			candidate_diff=colordiff(palette_pixels[order],source_pixels[i])
			if candidate_diff<best_diff:
				best_order=order
				best_index=index
				best_diff=candidate_diff
			index+=1
		new_palette_order+=[best_order]
		del current_palete_order[best_index]
		random.shuffle(current_palete_order)

	build_final_solution(source_im,palette_im,new_palette_order,new_filename)

#generates the new palette with the same dimensions as the source but with its own colours
def build_final_solution(source_im,palette_pixels,new_palette_order,new_filename):

	source_size=source_im.size

	palette_columns=source_size[0]
	palette_rows=source_size[1]
	palette_pixels=list(palette_im.getdata())

	new_palette=Image.new(source_im.mode,(palette_columns,palette_rows))

	new_palette_pixels=[]
	for n in new_palette_order:
		new_palette_pixels+=[palette_pixels[new_palette_order[n]]]
	
	new_palette.putdata(new_palette_pixels)
	new_palette.save(new_filename)

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
	sources=["images/american_gothic.png","images/spheres.png","images/mona_lisa.png","images/nature.png","images/starry_night.png","images/the_scream.png","images/mona_lisa_small.png","images/american_gothic_small.png"]
	palettes=["images/american_gothic.png","images/spheres.png","images/mona_lisa.png","images/nature.png","images/starry_night.png","images/the_scream.png","images/mona_lisa_small.png","images/american_gothic_small.png"]
	source=sources[0]
	palette=palettes[2]

	# source="american_gothic.png"
	# palette="mona_lisa.png"

	#algorithm parameters
	source_im=Image.open(source)
	palette_im=Image.open(palette)
	colordiff=colordiff_rgb
	new_filename=palette.split(".")[0]+"_rearranged.png"

	search(source_im,palette_im,colordiff,new_filename)