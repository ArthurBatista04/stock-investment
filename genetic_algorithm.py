import random
import math



class NODE(object):
	def __init__(self, gene):
		self.fitness = 0
		self.gene = gene

	def calculate_fitness(self, indicators):
		for i in range(len(indicators)):
			self.fitness+= self.gene[i] * indicators[i]

def selection(population):
	individuos = []
	random_positions = random.sample([i for i in range(len(population))], 32)
	for i in random_positions:
		individuos.append(population[i])
	parents = sorted(individuos, key=lambda agent: agent.fitness, reverse=True)
	return [parents[0], parents[1]]


def crossing_over(father, mother):
	required_gene_number = len(father.gene)
	child_gene = [-1 for _ in range(required_gene_number)]

	for i in range(required_gene_number):
		if(father.gene[i] == mother.gene[i]):
			child_gene[i] = father.gene[i]
	
	while(-1 in child_gene):
		random_position = random.randrange(0, required_gene_number) 
		if(child_gene[random_position] == -1):
			choice_father_gene = random.randrange(0,2)
			if(choice_father_gene):
				child_gene[random_position] = father.gene[random_position]
			else:
				child_gene[random_position] = mother.gene[random_position]
	
	return NODE(child_gene)

def inicial_polutation(population_size, gene_size):
	population = []
	count = 0
	while(count < population_size):
		random_values = [random.random() for _ in range(gene_size)]
		sum_values = sum(random_values)
		gene = [ i/sum_values for i in random_values ]
		if (sum(gene) == 1.0):
			population.append(NODE(gene))
			count+=1
	return population
	


def fitness(population, indicators):
	for individual in population: individual.calculate_fitness(indicators)
	
	
def mutation(child):
	is_mutating = random.randrange(0,2)
	if(is_mutating):
		gene_length = len(child.gene)
		rand_1, rand_2 = random.sample([i for i in range(gene_length)],2)
		child.gene[rand_1], child.gene[rand_2] = child.gene[rand_2], child.gene[rand_1]
	return child


def get_weakest_individual_index(population):
	weakest = math.inf
	index_weakest = 0
	for (index,individual) in enumerate(population):
		if (individual.fitness < weakest):
			weakest = individual.fitness
			index_weakest = index
	return index_weakest


def get_strongest_individual_index(population):
	strongest = -math.inf
	index_strongest = 0
	for (index,individual) in enumerate(population):
		if (individual.fitness > strongest):
			strongest = individual.fitness
			index_strongest = index
	return index_strongest


def include_in_population(individuo, population):
	weakest_index = get_weakest_individual_index(population)
	weakest = population[weakest_index]
	return individuo.fitness < weakest.fitness


def genetic_algorithm(population_size, indicators):
	population = inicial_polutation(population_size, len(indicators))
	fitness(population, indicators)		
	
	for _ in range(500):
		father, mother = selection(population)
		child = crossing_over(father, mother)
		mutated_child = mutation(child)
		mutated_child.calculate_fitness(indicators)

		if(include_in_population(mutated_child, population)):
			population.pop(get_weakest_individual_index(population))
			population.append(mutated_child)
	return population[get_weakest_individual_index(population)], population[get_strongest_individual_index(population)]


