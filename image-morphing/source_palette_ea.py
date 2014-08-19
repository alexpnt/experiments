#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Genetic Algorithm - Morphing an image into another with the same color palette - Just for fun
"""

import random
from operator import itemgetter
from PIL import Image
from colormath.color_diff import delta_e_cie1976
from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor,sRGBColor

__author__ = 'Alexandre Pinto'
__email__ = "alexandpinto@gmail.com"
__date__='2014'

#evolutionary algorithm: finding the best permutation of pixels that gives the best approximation to a given source image
def ea(source_im,palette_im,n_generations,size_pop,selection,tournament_size,recombination_func,prob_cross,survivors,fitness_func,elite_size):

	print "initializing population"
	population = [[generate_palette(source_im,palette_im),0] for j in range(size_pop)]			#initialize population
	population = [[indiv[0], fitness_func(source_im,indiv[0])] for indiv in population]			#evaluate population

	print "sorting initial population\n\n"
	population.sort(key=itemgetter(1), reverse = False) # Minimizing

	print "This may take a while ... have a break, have a kitkat \n"
	for j in range(n_generations):
		print "\n\ngeneration: "+str(j)
		mate_pool=selection(population,tournament_size)

		print "recombination ..."
		offspring_pop=[]
		for i in  range(0,size_pop-1,2):
			cromo_1= mate_pool[i][0]
			cromo_2 = mate_pool[i+1][0]
			offsprings = recombination_func(cromo_1,cromo_2,prob_cross)
			offspring_pop.extend(offsprings)

		print "evaluating offspring and sorting..."			
		offspring_pop = [ [indiv[0], fitness_func(source_im,indiv[0])] for indiv in offspring_pop]	#evaluate new population
		offspring_pop.sort(key=itemgetter(1), reverse = False)									#sorting,minimization

		print "surviving ..."
		population = survivors(population,offspring_pop,elite_size)

		print "evaluating final population and sorting ..."
		population = [[indiv[0], fitness_func(source_im,indiv[0])] for indiv in population]
		population.sort(key=itemgetter(1), reverse = False)

		print "current best fitness: "+str(population[0][1])

	print "\n\ndone!"
	best=population[0][0]
	best.save("best_palette.png");

#generates a new individual(palette) with the same dimensions as the source but with its own colours
def generate_palette(source_im,palette_im):

	source_size=source_im.size
	palette_columns=source_size[0]
	palette_rows=source_size[1]

	new_palette=Image.new(palette_im.mode,(palette_columns,palette_rows))

	palette_pixels=list(palette_im.getdata())
	random.shuffle(palette_pixels)
	new_palette.putdata(palette_pixels)

	return new_palette


#Tournament Selection. Minimization
def tournament_selection(population,t_size):
    size= len(population)
    mate_pool = []
    for i in range(size):
        winner = tournament(population,t_size)
        mate_pool.append(winner)
    return mate_pool

def tournament(population,size):
    pool = random.sample(population, size)
    pool.sort(key=itemgetter(1), reverse=False)
    return pool[0]

#uniform crossover
def uniform_cross(parent1_im,parent2_im,prob_cross):
	parent1_pixels=list(parent1_im.getdata())
	parent2_pixels=list(parent2_im.getdata())

	if(random.random<prob_cross):
		offspring1_pixels=[]
		offspring2_pixels=[]
		for i in xrange(len(parent1_im)):
			if(random.random()<0.5):
				offspring1_pixels+=[parent1_pixels[i]]
				offspring2_pixels+=[parent2_pixels[i]]
			else:
				offspring2_pixels+=[parent2_pixels[i]]
				offspring1_pixels+=[parent1_pixels[i]]

		offspring1_im=Image.new(parent1_im.mode,(parent1_im.size[0],parent1_im.size[1]))
		offspring1_im.putdata(offspring1_pixels)

		offspring2_im=Image.new(parent1_im.mode,(parent1_im.size[0],parent1_im.size[1]))
		offspring2_im.putdata(offspring2_pixels)
		return [(offspring1_im,0),(offspring2_im,0)]
	else:
		return [(parent1_im,0),(parent2_im,0)] 

# Survivals: elitism
def survivors_elitism(parents,offspring,elite_size):
    size = len(parents)
    comp_elite = int(size* elite_size)
    new_population = parents[:comp_elite] + offspring[:size - comp_elite]
    return new_population

#http://python-colormath.readthedocs.org/en/latest/index.html
#calculate the fitness of an individual, based on the color differences in the L*ab space
#the less the better
#pros: better results, cons: very slow
def fitness_lab(source_im,palette_im):
	source_pixels=list(source_im.getdata())
	palette_pixels=list(palette_im.getdata())

	fit=0.0
	for i in xrange(len(palette_pixels)):
		#convert rgb values to L*ab values
		rgb_pixel_source=sRGBColor(source_pixels[i][0],source_pixels[i][1],source_pixels[i][2],True)
		lab_source= convert_color(rgb_pixel_source, LabColor)

		rgb_pixel_palette=sRGBColor(palette_pixels[i][0],palette_pixels[i][1],palette_pixels[i][2],True)
		lab_palette= convert_color(rgb_pixel_palette, LabColor)

		#calculate delta e
		delta_e = delta_e_cie1976(lab_source, lab_palette)

		fit+=delta_e

	return fit

#rgb distance between two colors
#pros: very fast 
def fitness_rgb(source_im,palette_im):
	source_pixels=list(source_im.getdata())
	palette_pixels=list(palette_im.getdata())

	fit=0.0
	for i in xrange(len(palette_pixels)):
		delta_red=source_pixels[i][0]-palette_pixels[i][0]
		delta_green=source_pixels[i][1]-palette_pixels[i][1]
		delta_blue=source_pixels[i][2]-palette_pixels[i][2]

		fit+=delta_red**2+delta_green**2+delta_blue**2
	return fit

def check(palette, copy):
    palette = sorted(Image.open(palette).convert('RGB').getdata())
    copy = sorted(Image.open(copy).convert('RGB').getdata())
    print 'Success' if copy == palette else 'Failed'

if __name__ == '__main__':
	source="american_gothic.png"
	palette="spheres.png"

	#algorithm parameters
	source_im=Image.open(source)
	palette_im=Image.open(palette)
	n_generations=250
	size_pop=100
	tournament_size=3
	prob_cross=0.9
	elite_size=0.05

	ea(source_im,palette_im,n_generations,size_pop,tournament_selection,tournament_size,uniform_cross,prob_cross,survivors_elitism,fitness_rgb,elite_size)

	


