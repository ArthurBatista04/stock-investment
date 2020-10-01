import random
import math


class NODE(object):
	def __init__(self, gene):
		self.fitness = 0
		self.gene = gene

	def calculate_fitness(self, indicators):
		for i in range(len(indicators)):
			self.fitness += self.gene[i] * indicators[i]


def selection(population):
	individuos = []
	random_positions = random.sample([i for i in range(len(population))], 32)
	for i in random_positions:
		individuos.append(population[i])
	parents = sorted(individuos, key=lambda agent: agent.fitness)
	return [parents[0], parents[1]]


def crossing_over(father, mother):
	required_gene_number = len(father.gene)
	total_sum = sum(father.gene) + sum(mother.gene)

	child_gene = [(mother.gene[i] + father.gene[i]) /
				  total_sum for i in range(required_gene_number)]
	return NODE(child_gene)


def initial_population(population_size, gene_size):
	population = []
	count = 0
	while(count < population_size):
		random_values = [random.random() for _ in range(gene_size)]
		sum_values = sum(random_values)
		gene = [i/sum_values for i in random_values]
		if (sum(gene) == 1.0):
			population.append(NODE(gene))
			count += 1
	return population


def fitness(population, indicators):
	for individual in population:
		individual.calculate_fitness(indicators)


def mutation(child):
	is_mutating = random.randrange(0, 2)
	if(is_mutating):
		gene_length = len(child.gene)
		rand_1, rand_2 = random.sample([i for i in range(gene_length)], 2)
		child.gene[rand_1], child.gene[rand_2] = child.gene[rand_2], child.gene[rand_1]
	return child


def get_lowest_fitness_index(population):
	lowest = math.inf
	index_lowest = 0
	for (index, individual) in enumerate(population):
		if (individual.fitness < lowest):
			lowest = individual.fitness
			index_lowest = index
	return index_lowest


def get_highest_fitness_index(population):
	highest = -math.inf
	index_highest = 0
	for (index, individual) in enumerate(population):
		if (individual.fitness > highest):
			highest = individual.fitness
			index_highest = index
	return index_highest


def include_child_in_population(child, population):
	lowest_index = get_lowest_fitness_index(population)
	lowest = population[lowest_index]
	return child.fitness < lowest.fitness


def genetic_algorithm(population_size, indicators):
	population = initial_population(population_size, len(indicators))
	fitness(population, indicators)

	for _ in range(500):
		father, mother = selection(population)
		child = crossing_over(father, mother)
		mutated_child = mutation(child)
		mutated_child.calculate_fitness(indicators)

		if(include_child_in_population(mutated_child, population)):
			population.pop(get_lowest_fitness_index(population))
			population.append(mutated_child)

	return population[get_lowest_fitness_index(population)]
