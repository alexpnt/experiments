#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Iterated Local Search - An alternative to build a photomosaic - Just for fun
"""

import random
from copy import deepcopy
from math import exp
from PIL import Image

__author__ = 'Alexandre Pinto'
__email__ = "alexandpinto@gmail.com"
__date__='2014'

def build_photomosaic_ils(mosaic_im,target_im,block_width,block_height,nsteps,niterations,nperturbations,acceptance_mode,new_filename):

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
	print "Computing the average color of each photo in the target photo ..."
	target_color_averages=compute_block_avg(target_im,block_width,block_height)

	print "Computing initial solution ..."
	candidate=build_initial_solution(target_nboxes,mosaic_nboxes)

	print "Applying a local search ..."
	best,best_fitness=local_search(candidate,mosaic_color_averages,mosaic_nboxes,target_color_averages,target_nboxes,nsteps)

	print "Iterated local Search ..."
	for i in xrange(niterations):
		print "Progress: %.2f " % (i/float(niterations)*100)+"%"
		candidate=perturbation(best,target_nboxes,mosaic_nboxes,nperturbations)
		perturbed,perturbed_fitness=local_search(candidate,mosaic_color_averages,mosaic_nboxes,target_color_averages,target_nboxes,nsteps)
		best,best_fitness=acceptance(best,best_fitness,perturbed,perturbed_fitness,acceptance_mode)

	print "Building final image ..."
	build_final_solution(best,mosaic_im,target_nboxes,target_im,target_grid_width,block_height,block_width,new_filename)
	print "Best fitness achieved: ",best_fitness

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

	target_im.save(new_filename);



def local_search(candidate,mosaic_color_averages,mosaic_nboxes,target_color_averages,target_nboxes,nsteps):
	
	best=deepcopy(candidate)
	best_fitness=fitness(best,mosaic_color_averages,mosaic_nboxes,target_color_averages,target_nboxes)

	#For each photo, tries to change it with another from the pool, saves it if it's a better candidate
	#(e.g: change photo number 2 with 3,4,5,6,...) during nsteps
	for i in xrange(target_nboxes):
		# print "%.2f " % (i/float(target_nboxes)*100)+"%"
		for j in xrange(nsteps):
			candidate[i]=(candidate[i]+1)%mosaic_nboxes

			candidate_fit=fitness(candidate,mosaic_color_averages,mosaic_nboxes,target_color_averages,target_nboxes)
			if(candidate_fit<best_fitness):
				best=deepcopy(candidate)
				best_fitness=candidate_fit

	#For each photo, swap it with the next one, then the other, and so on... (1<->2, 1<-3, ...) during nsteps
	#saves it if it's a better candidate
	for i in xrange(target_nboxes):
		# print "%.2f " % (i/float(target_nboxes)*100)+"%"
		for j in xrange(1,nsteps+1):
			temp=candidate[i]
			candidate[i]=candidate[(i+j)%target_nboxes]
			candidate[(i+j)%target_nboxes]=temp

			candidate_fit=fitness(candidate,mosaic_color_averages,mosaic_nboxes,target_color_averages,target_nboxes)
			if(candidate_fit<best_fitness):
				best=deepcopy(candidate)
				best_fitness=candidate_fit

	return best,best_fitness


def perturbation(best,target_nboxes,mosaic_nboxes,nperturbations):
	perturbed=deepcopy(best)

	for i in xrange(nperturbations):
		if random.random()<0.5: 
			#choose a different headshot for a randomly chosen block
			rand_position=random.randint(0,target_nboxes-1)
			perturbed[rand_position]=random.randint(0,mosaic_nboxes-1)
		else:	
			#swaps the blocks of two randomly chosen positions
			rand_position_1=random.randint(0,target_nboxes-1)
			rand_position_2=random.randint(0,target_nboxes-1)
			while rand_position_1==rand_position_2:
				rand_position_2=random.randint(0,target_nboxes-1)

			temp=perturbed[rand_position_1]
			perturbed[i]=perturbed[rand_position_2]
			perturbed[rand_position_1]=temp

	return perturbed

def acceptance(best,best_fitness,perturbed,perturbed_fitness,acceptance_mode=1):
	if acceptance_mode==0: 
		#Random Walk
		return perturbed,perturbed_fitness
	elif acceptance_mode==1: 
		#Accept if Better
		if perturbed_fitness<best_fitness:
			return perturbed,perturbed_fitness
		else:
			return best,best_fitness
	else:
		#Simulated Annealing
		if perturbed_fitness<best_fitness:
			return perturbed,perturbed_fitness
		else:
			prob=exp(-(best_fitness-perturbed_fitness)/0.1)
			p = random.random()
			if p < prob:
				return perturbed,perturbed_fitness
			else:
				return best,best_fitness

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

#returns the average color of a given image
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
#the less the better
def colordiff_rgb(pixel1,pixel2):

	delta_red=pixel1[0]-pixel2[0]
	delta_green=pixel1[1]-pixel2[1]
	delta_blue=pixel1[2]-pixel2[2]

	fit=delta_red**2+delta_green**2+delta_blue**2
	return fit

if __name__ == '__main__':
	mosaic="images/25745_avatars.png"
	target="images/lightbulb.png"
	mosaic_im=Image.open(mosaic)
	target_im=Image.open(target)
	nsteps=10
	niterations=10000
	nperturbations=5
	acceptance_mode=1
	new_filename="photomosaic.png"

	build_photomosaic_ils(mosaic_im,target_im,48,48,nsteps,niterations,nperturbations,acceptance_mode,new_filename)
