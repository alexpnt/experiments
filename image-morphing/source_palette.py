#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Iterated Local Search - Morphing an image into another with the same color palette - Just for fun
"""

import random
from math import log
from copy import deepcopy
from operator import itemgetter
from PIL import Image
from colormath.color_diff import delta_e_cie1976
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor,sRGBColor

__author__ = 'Alexandre Pinto'
__email__ = "alexandpinto@gmail.com"
__date__='2014'

def search(source_im,palette_im,diff,error,k1,k2):

	columns=source_im.size[0]
	rows=source_im.size[1]

	source_pixels=list(source_im.getdata())
	palette_pixels=list(palette_im.getdata())
	new_palette_pixels=deepcopy(palette_pixels)

	check_matrix=[False]*columns*rows

	error=diff(avg(source_pixels),avg(palette_pixels))

	progress=0
	original_error=error
	size=columns*rows

	#brute-force + greedy algorithm, the first pixel with a reasonable fitness is chosed
	for pixel in palette_pixels:
		print "%.2f " % (progress/float(len(palette_pixels))*100)+"%"
		done=False
		error=original_error
		while not done:
			for i in xrange(len(palette_pixels)):
				if(diff(source_pixels[i],pixel)<=error and not check_matrix[i]):
					new_palette_pixels[i]=pixel
					check_matrix[i]=True
					done=True
					palette_pixels.remove(pixel)
					random.shuffle(palette_pixels)
					break
			else:
				error*=k1
		error+=k2
		progress+=1

	print "\nFitness achieved: "+str(fitness(source_im,new_palette_pixels))
	best=Image.new(palette_im.mode,(columns,rows))
	best.putdata(new_palette_pixels)
	best.save("best_palette.png");

	print "First phase finished, runnning an iterated local search ..."
	ils(source_im,best,10000,1000)

#iterated local search
def ils(source_im,palette_im,iterations,convergence_width):
    best=[list(palette_im.getdata()),0]
    best[1]=fitness(source_im,best[0])

    candidate=[deepcopy(best[0]),best[1]]
    for i in range(iterations):
        print "\niteration "+str(i)+": Current Best Fitness: "+str(best[1])
        # candidate=perturb(best,source_im)
        candidate=local_search(source_im,candidate,convergence_width)

        if candidate[1]<best[1]:
            best[0]=deepcopy(candidate[0])
            best[1]=candidate[1]
            print "\timprovement made in ils: "+str(best[1])+" !"

    final_image=Image.new(palette_im.mode,(palette_im.size[0],palette_im.size[1]))
    final_image.putdata(best[0])
    final_image.save("best_palette.png");

def perturb(best,source_im):
    candidate=[best[0],0]
    candidate[0]=double_bridge_move(best[0])
    candidate[1]=fitness(source_im,candidate[0])
    return [candidate[0],candidate[1]]

def double_bridge_move(palette_pixels):
    size=len(palette_pixels)

    pos1=random.randint(1,size/4)
    pos2 = pos1 + random.randint(1,size/4)
    pos3 = pos2 + random.randint(1,size/4)
    p1 = palette_pixels[0:pos1] + palette_pixels[pos3:size]
    p2 = palette_pixels[pos2:pos3] + palette_pixels[pos1:pos2]

    assert(len(palette_pixels)==len(p1+p2))
    return p1 + p2

# def permut(palette_pixels):
#     size=len(palette_pixels)
#     cut1,cut2=random.randint(size-1),random.randint(size-1)
#     exclude=[cut1]
#     if cut1==0:
#         exclude+=[size-1]
#     else:
#         exclude+=[cut1-1]

#     if cut1==size-1:
#         exclude+=[0]
#     else:
#         exclude+=[cut1+1]

#     while(cut2 not in exclude):
#         cut2=random.randint(size-1)

#     if cut2<cut1:
#         cut1, cut2 = cut2, cut1

#     first=palette_pixels[0:cut1]

def permut(palette_pixels):
    random_pixel_pos1=random.randint(0,len(palette_pixels)-1)
    random_pixel_pos2=random_pixel_pos1

    while random_pixel_pos1==random_pixel_pos2:
        random_pixel_pos2=random.randint(0,len(palette_pixels)-1)

    tmp=palette_pixels[random_pixel_pos1]
    palette_pixels[random_pixel_pos1]=palette_pixels[random_pixel_pos2]
    palette_pixels[random_pixel_pos2]=tmp

    return palette_pixels

def local_search(source_im,best,convergence_width):

    counter=0
    candidate=[best[0],0]
    while True:
        candidate[0]=permut(best[0])
        candidate[1]=fitness(source_im,candidate[0])

        if candidate[1]>=best[1]:
            counter+=1
        else:
            best[0]=candidate[0]
            best[1]=candidate[1]
            counter=0
            print "\timprovement made in ls: "+str(best[1])+" !"
        if counter>=convergence_width:
            break

    return [best[0],best[1]]

#generates a new individual(palette) with the same dimensions as the source but with its own colours
def generate_palette(source_im,palette_im):

	source_size=source_im.size
	palette_columns=source_size[0]
	palette_rows=source_size[1]

	new_palette=Image.new(palette_im.mode,(palette_columns,palette_rows))

	palette_pixels=list(palette_im.getdata())
	new_palette.putdata(palette_pixels)

	return new_palette

def avg(pixels):
	avg_r=avg_g=avg_b=0.0
	size=len(pixels)
	for p in pixels:
		avg_r+=p[0]/float(size)
		avg_g+=p[1]/float(size)
		avg_b+=p[2]/float(size)

	return (avg_r,avg_g,avg_b)


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

	rgb_pixel_palette=sRGBColor(palette_pixel[0],palette_pixel[1],palette_pixel[2],True)
	lab_palette= convert_color(rgb_pixel_palette, LabColor)

	#calculate delta e
	delta_e = delta_e_cie1976(lab_source, lab_palette)
	return delta_e

#http://python-colormath.readthedocs.org/en/latest/index.html
#calculate the fitness of an individual, based on the color differences in the L*ab space
#the less the better
#pros: better results, cons: very slow
# def fitness(source_im,palette_pixels):
#     source_pixels=list(source_im.getdata())

#     fit=0.0
#     for i in xrange(len(palette_pixels)):
#         #convert rgb values to L*ab values
#         rgb_pixel_source=sRGBColor(source_pixels[i][0],source_pixels[i][1],source_pixels[i][2],True)
#         lab_source= convert_color(rgb_pixel_source, LabColor)

#         rgb_pixel_palette=sRGBColor(palette_pixels[i][0],palette_pixels[i][1],palette_pixels[i][2],True)
#         lab_palette= convert_color(rgb_pixel_palette, LabColor)

#         #calculate delta e
#         delta_e = delta_e_cie1976(lab_source, lab_palette)

#         fit+=delta_e

#     return fit

#calculate the fitness of an individual, based on the color differences in the RGB space
#the less the better
#pros: very fast 
def fitness(source_im,palette_pixels):
    source_pixels=list(source_im.getdata())

    fit=0.0
    for i in xrange(len(palette_pixels)):
        delta_red=source_pixels[i][0]-palette_pixels[i][0]
        delta_green=source_pixels[i][1]-palette_pixels[i][1]
        delta_blue=source_pixels[i][2]-palette_pixels[i][2]

        fit+=delta_red**2+delta_green**2+delta_blue**2
    return fit

if __name__ == '__main__':
	# source="american_gothic_small.png"
	# palette="mona_lisa_small.png"

	source="american_gothic.png"
	palette="mona_lisa.png"

	#algorithm parameters
	source_im=Image.open(source)
	palette_im=Image.open(palette)
	error=2
	k1=1.1
	k2=0.1
	diff=colordiff_rgb

	search(source_im,palette_im,diff,error,k1,k2)