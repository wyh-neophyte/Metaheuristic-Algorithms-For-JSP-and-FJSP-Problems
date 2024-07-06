import numpy as np
import random
import matplotlib.pyplot as plt
import copy
import time
import json
import os
from utils.Calculate import *


class GASolver:
    def __init__(self, jobnum, machinenum, use_critical_path, population=30, crossover=0.9, mutation=0.9,
                 selectionmethod='competition', selection=0.2, iteration=2000):
        """
        :param jobnum: number of jobs
        :param machinenum: number of machines
        :param population: (hyper parameters for GA algorithm)
        :param crossover: the possibility of crossover (hyper parameters for GA algorithm)
        :param mutation: the possibility of mutation (hyper parameters for GA algorithm)
        :param selection: the possibility (hyper parameters for GA algorithm)
        :param iteration: iteration number
        """
        # basic settings
        self.jobnum = jobnum
        self.machinenum = machinenum
        self.use_critical_path = use_critical_path
        self.population = population
        self.crossover = crossover
        self.mutation = mutation
        self.selection = selection
        self.genlength = jobnum * machinenum
        self.iteration = iteration
        self.selectionmethod = selectionmethod

        self.iternow = 0
        self.processcount = 0
        self.decodedict = {}
        self.iteration_makespans = []
        self.bestindividual, self.bestfitness = None, None
        self.populations, self.parents, self.children = None, None, None
        self.parentfitness, self.parent_operations, self.parent_makespans = None, None, None
        self.childrenfitness, self.children_operations, self.children_makespans = None, None, None

    def initialize_solution(self, jsonfile):
        for partid in range(self.jobnum):
            self.processcount += len(jsonfile[str(partid)])
        populations = []
        for i in range(self.population):
            populations.append(list(np.random.permutation(self.processcount)))
        partid, partcount = 0, 0
        decodedict = {}
        for i in range(self.processcount):
            decodedict[str(i)] = partid
            partcount += 1
            if partcount == len(jsonfile[str(partid)]):
                partid += 1
                partcount = 0
        self.decodedict = decodedict
        return populations

    def crossoverop(self, populations):
        random.shuffle(populations)
        childpopulations = []
        for i in range(len(populations) // 2):
            prob = np.random.rand()
            if prob >= self.crossover:
                continue
            parent1 = copy.deepcopy(populations[2 * i])
            parent2 = copy.deepcopy(populations[2 * i + 1])
            # if self.problem.lower() == 'jsp':
            #     self.processcount = self.genlength
            crossoveridxs = [np.random.randint(0, 2) for _ in range(self.processcount)]
            subset1, subset2 = [], []
            for j in range(self.processcount):
                if crossoveridxs[j]:
                    try:
                        subset1.append(parent1[j])
                        subset2.append(parent2[j])
                    except:
                        print(f'parent1:{parent1}, which is {2*i} from populations, doent have index{j}')
                        print(f'parent2:{parent2}, which is {2*i+1} from populations, doent have index{j}')

            child1, child2 = [], []
            idx1, idx2 = 0, 0
            for j in range(self.processcount):
                if crossoveridxs[j]:
                    child1.append(parent2[j])
                    child2.append(parent1[j])
                else:
                    while True:
                        if parent1[idx1] not in subset2:
                            break
                        else:
                            idx1 += 1
                    child1.append(parent1[idx1])
                    idx1 += 1

                    while True:
                        if parent2[idx2] not in subset1:
                            break
                        else:
                            idx2 += 1
                    child2.append(parent2[idx2])
                    idx2 += 1
            childpopulations.append(child1)
            childpopulations.append(child2)
        return childpopulations

    def mutationop(self, populations):
        # three mutation operations are provided, namely swap, insert, and flip
        def swap(individual):
            idx = random.randint(0, len(individual) - 2)
            tmp = individual[idx]
            individual[idx] = individual[idx + 1]
            individual[idx + 1] = tmp
            return individual

        def insert(individual):
            idx = random.randint(0, len(individual) - 1)
            individual = list(individual)
            tmp = individual.pop(idx)
            while True:
                insertidx = random.randint(0, len(individual) - 1)
                if insertidx != idx:
                    break
            individual.insert(insertidx, tmp)
            return np.array(individual)

        def flip(individual):
            idx1 = random.randint(0, len(individual) - 3)
            idx2 = random.randint(idx1 + 2, len(individual) - 1)
            tmp = list(individual[idx1: idx2])
            tmp.reverse()
            individual[idx1: idx2] = tmp
            return individual

        # the three mutation types share the same probability
        for idx, individual in enumerate(populations):
            prob = np.random.rand()
            if prob < self.mutation:
                select = np.random.randint(low=0, high=2)
                if select == 0:
                    populations[idx] = swap(individual)
                elif select == 1:
                    populations[idx] = insert(individual)
                elif select == 2:
                    populations[idx] = flip(individual)
        return populations

    def update_by_critical_path(self, jsonfile, array):
        runtime = time.time()
        operation, makespan = self.calculate_maskespan(array, jsonfile)
        # convert critical path into blocks
        critical_path = find_critical_path(operation, makespan)
        critical_path_blocks = []
        if critical_path is not None:
            machineid, (partid, processid, starttime, endtime) = critical_path[0]
            current_machine = machineid
            critical_path_blocks.append([[machineid, partid, processid]])
            for machineid, (partid, processid, starttime, endtime) in critical_path[1:]:
                if machineid == current_machine:
                    critical_path_blocks[-1].append([machineid, partid, processid])
                else:
                    critical_path_blocks.append([])
                    current_machine = machineid
            critical_path_blocks = [item for item in critical_path_blocks if len(item) > 1]

        best_operation, best_neighbour, best_makespan = None, None, 1e10
        for block in critical_path_blocks:
            partset = list(set([item[1] for item in block]))
            if len(partset) == 1:
                continue
            for i in range(len(block) - 1):
                for j in range(i + 1, len(block)):
                    neighbour = np.copy(array)
                    _, partid1, processid1 = block[i]
                    _, partid2, processid2 = block[j]

                    decode = list(map(lambda x: self.decodedict[str(x)], neighbour))
                    idx1 = [idx for idx, item in enumerate(decode) if item == partid1]
                    idx2 = [idx for idx, item in enumerate(decode) if item == partid2]
                    idx1, idx2 = idx1[processid1], idx2[processid2]

                    # swap
                    tmp = neighbour[idx1]
                    neighbour[idx1] = neighbour[idx2]
                    neighbour[idx2] = tmp
                    newoperation, newmakespan = self.calculate_maskespan(neighbour, jsonfile)
                    if newmakespan < best_makespan:
                        best_neighbour = neighbour
                        best_makespan = newmakespan
                        best_operation = newoperation

                    # insert
                    neighbour = np.copy(array)
                    tmp = neighbour[max(idx1, idx2)]
                    neighbour = np.delete(neighbour, max(idx1, idx2))
                    neighbour = np.insert(neighbour, min(idx1, idx2), tmp)
                    newoperation, newmakespan = self.calculate_maskespan(neighbour, jsonfile)
                    if newmakespan < best_makespan:
                        best_neighbour = neighbour
                        best_makespan = newmakespan
                        best_operation = newoperation

                    if best_makespan < round(1/self.bestfitness):
                        return best_neighbour, best_operation, best_makespan
        return best_neighbour, best_operation, best_makespan

    def fitness(self, makespan):
        return 1 / makespan

    def calculate_maskespan(self, individual, jsonfile):
        """
        :param individual: a purmutation of 1,...,n, which is decoded into job schedule
        :param jsonfile:
        :return:
        """
        individualcopy = copy.deepcopy(individual)
        individualcopy = list(map(lambda x: self.decodedict[str(x)], individualcopy))
        machine_operations, cmax = calculate_fjsp_greedy(jsonfile, individualcopy)
        self.iternow += 1
        return machine_operations, cmax

    def selectionop(self, parents, children, parent_operations, parent_makespans, children_operations,
                    children_makespans, method='', parentfitness=None, childrenfitness=None):
        if method.lower() == '':
            population = parents + children
            operations = parent_operations + children_operations
            makespans = parent_makespans + children_makespans
            return population[-self.population:], operations[-self.population:], makespans[-self.population:]
        elif method.lower() == 'random':
            index = random.sample(list(range(len(parents + children))), self.population)
            population = parents + children
            operations = parent_operations + children_operations
            makespans = parent_makespans + children_makespans

            population = [population[idx] for idx in index]
            operations = [operations[idx] for idx in index]
            makespans = [makespans[idx] for idx in index]
            return population, operations, makespans

        # Elitism strategy
        elif method.lower() == 'elitism':
            top_k_populations, top_k_operations, top_k_makespans = [], [], []
            # select population * selection rate from parents
            parentfitness = [(idx, item) for idx, item in enumerate(parentfitness)]
            parentfitness.sort(key=lambda x: x[-1], reverse=True)
            top_k_indices = [item[0] for item in parentfitness[:int(self.population * self.selection)]]
            for indice in top_k_indices:
                top_k_populations.append(parents[indice])
                top_k_operations.append(parent_operations[indice])
                top_k_makespans.append(parent_makespans[indice])

            # select population * (1-selection rate) from children
            childrenfitness = [(idx, item) for idx, item in enumerate(childrenfitness)]
            childrenfitness.sort(key=lambda x: x[-1], reverse=True)
            top_k_indices = [item[0] for item in
                             childrenfitness[:self.population - int(self.population * self.selection)]]
            for indice in top_k_indices:
                top_k_populations.append(children[indice])
                top_k_operations.append(children_operations[indice])
                top_k_makespans.append(children_makespans[indice])
            return top_k_populations, top_k_operations, top_k_makespans

        # Competition strategy
        elif method.lower() == 'competition':
            fitness = parentfitness + childrenfitness
            populations = parents + children
            operations = parent_operations + children_operations
            makespans = parent_makespans + children_makespans
            fitness = [(idx, item) for idx, item in enumerate(fitness)]
            fitness.sort(key=lambda x: x[-1], reverse=True)
            top_k_indices = [item[0] for item in fitness[:self.population]]
            top_k_populations, top_k_operations, top_k_makespans = [], [], []
            for indice in top_k_indices:
                top_k_populations.append(populations[indice])
                top_k_operations.append(operations[indice])
                top_k_makespans.append(makespans[indice])
            return top_k_populations, top_k_operations, top_k_makespans

        # roulette wheel selection
        elif method.lower() == 'roulette':
            fitness = parentfitness + childrenfitness
            populations = parents + children
            operations = parent_operations + children_operations
            makespans = parent_makespans + children_makespans

            next_populations, next_operations, next_makespans = [], [], []
            probabilities = [self.population * fitness[idx] / sum(fitness) for idx in range(len(fitness))]
            for i, probability in enumerate(probabilities):
                if np.random.rand() < probability:
                    next_populations.append(populations[i])
                    next_operations.append(operations[i])
                    next_makespans.append(makespans[i])
            return next_populations, next_operations, next_makespans

    def solve(self, jsonfile):
        self.populations = self.initialize_solution(jsonfile)

        while self.iternow < self.iteration:
            # the first generation
            operation_list, makespan_list = [], []
            if self.iternow == 0:
                for individual in self.populations:
                    operation, makespan = self.calculate_maskespan(individual, jsonfile)
                    operation_list.append(operation)
                    makespan_list.append(makespan)
                fitness_list = list(map(self.fitness, makespan_list))
                self.parentfitness = fitness_list
                for index, fitness in enumerate(fitness_list):
                    if (self.bestfitness is None and self.bestindividual is None) or self.bestfitness < fitness:
                        self.bestfitness = fitness
                        self.bestindividual = copy.deepcopy(self.populations[index])
                self.plateau = 0
                self.parents = self.populations
                self.parentfitness = fitness_list
                self.parent_operations = operation_list
                self.parent_makespans = makespan_list
                continue

            # the second generations starts crossover and mutation
            self.children = []
            if self.use_critical_path and self.plateau > 10 * self.population:
                operation_list, makespan_list = [], []
                for idx, individual in enumerate(self.parents):
                    prob = np.random.rand()
                    if prob < 0.5:
                        child, operation, makespan = self.update_by_critical_path(jsonfile, individual)
                        if child is None:
                            child = self.mutationop([individual])[0]
                            operation, makespan = self.calculate_maskespan(child, jsonfile)
                    else:
                        child = self.mutationop([individual])[0]
                        operation, makespan = self.calculate_maskespan(child, jsonfile)
                    operation_list.append(operation)
                    makespan_list.append(makespan)
                    self.children.append(child)
                self.children_operations = operation_list
                self.children_makespans = makespan_list
                self.populations = self.parents + self.children
                self.plateau = 0
                print(f"update by critical path, population:{len(self.populations)}")
            else:
                # self.populations = [item for item in self.populations if item is not None]
                self.children = self.crossoverop(self.populations)
                self.children = self.mutationop(self.children)
                operation_list, makespan_list = [], []
                for individual in self.children:
                    operation, makespan = self.calculate_maskespan(individual, jsonfile)
                    operation_list.append(operation)
                    makespan_list.append(makespan)
                self.children_operations = operation_list
                self.children_makespans = makespan_list
                self.populations = self.parents + self.children

            self.childrenfitness = list(map(self.fitness, self.children_makespans))
            for index, fitness in enumerate(self.childrenfitness):
                if self.bestfitness < fitness:
                    self.bestfitness = fitness
                    self.bestindividual = copy.deepcopy(self.children[index])
                    self.plateau = 0
                else:
                    self.plateau += 1

            self.parents, self.parent_operations, self.parent_makespans \
                = self.selectionop(self.parents, self.children,
                                   parent_operations=self.parent_operations, parent_makespans=self.parent_makespans,
                                   children_operations=self.children_operations,
                                   children_makespans=self.children_makespans,
                                   parentfitness=self.parentfitness, childrenfitness=self.childrenfitness,
                                   method=self.selectionmethod)
            self.parentfitness = list(map(self.fitness, self.parent_makespans))
            print(f'iteration: {self.iternow}\t best makespan: {round(1 / self.bestfitness)} patience: {self.plateau} population:{len(self.parents)}')

        best_operations, best_makespan = self.calculate_maskespan(self.bestindividual, jsonfile)
        return list(map(lambda x: self.decodedict[str(x)], self.bestindividual)), best_makespan, best_operations
