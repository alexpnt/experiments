#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Iterated Local search - Morphing an image into another with the same color palette - Just for fun
"""

import random
from copy import deepcopy
from operator import itemgetter
from PIL import Image
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor,sRGBColor
from colormath.color_diff import delta_e_cie1976

__author__ = 'Alexandre Pinto'
__email__ = "alexandpinto@gmail.com"
__date__='2014'

#iterated local search
def ils(source_im,palette_im,iterations,convergence_width):
    best=[generate_palette(source_im,palette_im),0]
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

    best.save("best_palette.png");

def double_bridge_move(palette_pixels):
    size=len(palette_pixels)

    pos1=random.randint(1,size/4)
    pos2 = pos1 + random.randint(1,size/4)
    pos3 = pos2 + random.randint(1,size/4)
    p1 = palette_pixels[0:pos1] + palette_pixels[pos3:size]
    p2 = palette_pixels[pos2:pos3] + palette_pixels[pos1:pos2]

    assert(len(palette_pixels)==len(p1+p2))
    return p1 + p2

def perturb(best,source_im):
    candidate=[best[0],0]
    candidate[0]=double_bridge_move(best[0])
    candidate[1]=fitness(source_im,candidate[0])
    return [candidate[0],candidate[1]]

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


#generates a new random individual(permutation) with the same dimensions as the source but with its own colours
def generate_palette(source_im,palette_im):

    source_size=source_im.size
    palette_columns=source_size[0]
    palette_rows=source_size[1]

    palette_pixels=list(palette_im.getdata())
    random.shuffle(palette_pixels)

    return palette_pixels

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
    source="american_gothic.png"
    palette="spheres.png"

    source_im=Image.open(source)
    palette_im=Image.open(palette)
    iterations=100
    convergence_width=100

    ils(source_im,palette_im,iterations,convergence_width)