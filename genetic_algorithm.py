from initial_pop import create_initial_population
from helpers import write_fitness_scores_to_csv

import numpy as np
import random


def genetic_algorithm(constants, word):
    # Create initial population
    population = create_initial_population(constants, word)

    highest_fitness_child = None
    highest_fitness_score = float('-inf')

    for generation in range(constants['MAX_GENERATIONS']):
        row_fitness = []
        col_fitness = []
        subgroup_fitness = []
        # Evaluate fitness for each individual in the population
        fitness_scores = []
        for individual in population:
            fitness_score, row_score, col_score, subgroup_score = evaluate_fitness(constants, individual)
            fitness_scores.append(fitness_score)
            row_fitness.append(row_score)
            col_fitness.append(col_score)
            subgroup_fitness.append(subgroup_score)

        # Write fitness scores and get the highest fitness child
        highest_fitness_child, highest_fitness_score = write_fitness_scores_to_csv(fitness_scores,
                                                                                   population,
                                                                                   'fitness_scores.csv',
                                                                                   row_fitness,
                                                                                   col_fitness,
                                                                                   subgroup_fitness)

        # Check termination condition
        if constants['MAX_FITNESS'] in fitness_scores:
            break

        # Apply elitism by preserving a certain percentage of the fittest individuals
        num_elites = int(constants['ELITISM_RATE'] * constants['POPULATION_SIZE'])
        elite_indices = np.argsort(fitness_scores)[-num_elites:]
        elites = [population[i] for i in elite_indices]

        # Select best individuals as parents for the next generation (excluding elites)
        non_elite_indices = np.argsort(fitness_scores)[:-num_elites]
        selected_parents = [population[i] for i in non_elite_indices]

        # Create empty list for children
        children = []

        # Generate offspring through crossover
        for _ in range(constants['SELECTED_POPULATION_SIZE']):
            child = crossover(constants, selected_parents[0], selected_parents[1])
            children.append(child)

        # Mutate the children
        mutated_children = mutate(children, constants['MUTATION_RATE'], word)

        # Replace the population with mutated children and elites
        population = mutated_children + elites

    return highest_fitness_child, highest_fitness_score, row_score, col_score, subgroup_score


def evaluate_fitness(constants, grid):
    fitness = 0
    row_score = 0
    col_score = 0
    subgroup_score = 0

    # Check rows
    for row in grid:
        row_words = [cell.lower() if cell != '-' else '-' for cell in row]
        if len(row_words) == len(set(row_words)) and '-' not in row_words:
            row_score += 1
        else:
            row_score -= 1

    # Check columns
    for j in range(constants['GRID_SIZE']):
        column = [grid[i][j] for i in range(constants['GRID_SIZE'])]
        column_words = [cell.lower() if cell != '-' else '-' for cell in column]
        if len(column_words) == len(set(column_words)) and '-' not in column_words:
            col_score += 1
        else:
            col_score -= 1

    # Check subgroups
    for i in range(0, constants['GRID_SIZE'], constants['SUBGRID_SIZE']):
        for j in range(0, constants['GRID_SIZE'], constants['SUBGRID_SIZE']):
            subgrid_letters = []
            for x in range(i, i + constants['SUBGRID_SIZE']):
                for y in range(j, j + constants['SUBGRID_SIZE']):
                    letter = grid[x][y]
                    if letter != '-':
                        subgrid_letters.append(letter.lower())

            if len(set(subgrid_letters)) == constants['SUBGRID_SIZE'] * constants['SUBGRID_SIZE'] \
                    and '-' not in subgrid_letters:
                subgroup_score += 4
            else:
                subgroup_score -= 4

    fitness = row_score + col_score + subgroup_score

    return fitness, row_score, col_score, subgroup_score


def crossover(constants, parent1, parent2):
    child = [['-' for _ in range(constants['GRID_SIZE'])] for _ in range(constants['GRID_SIZE'])]

    for i in range(constants['GRID_SIZE']):
        for j in range(constants['GRID_SIZE']):
            if random.random() < constants['CROSSOVER_RATE']:
                # Select gene from parent 1 if crossover occurs
                child[i][j] = parent1[i][j]
            else:
                # Select gene from parent 2 if crossover doesn't occur
                child[i][j] = parent2[i][j]

    return child


def mutate(children, mutation_rate, word):
    for child in children:
        for i in range(len(child)):
            for j in range(len(child[i])):
                if child[i][j] == "-" or child[i][j].isupper():
                    if random.random() < mutation_rate:
                        valid_letters = [letter.upper() for letter in word]
                        # Mutate the gene by selecting a random letter from the valid letters
                        child[i][j] = random.choice(valid_letters)

    return children
