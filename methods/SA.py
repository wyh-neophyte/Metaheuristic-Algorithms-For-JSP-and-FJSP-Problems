import random
import numpy as np
from utils.Calculate import *
import time


class SASolver:
    def __init__(self, machinenum, jobnum, use_critical_path, initial_temperature, cooling_rate, stop_temperature):
        """
        :param machinenum: number of machines
        :param jobnum: number of jobs
        :param initial_temperature: initial temperature for simulated annealing
        :param cooling_rate: rate at which the temperature decreases
        :param stop_temperature: temperature at which the algorithm stops
        """
        # basic settings
        self.machinenum = machinenum
        self.jobnum = jobnum
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.stop_temperature = stop_temperature
        self.use_critical_path = use_critical_path
        # decode array into understandable schedule
        self.decodedict = {}
        # counter of function calculate_makespan
        self.iteration = 0
        # temperature
        self.temperature = initial_temperature
        # record solutions
        self.iteration_makespans = []
        self.best_solution = None
        self.best_makespan = None
        self.best_operation = None

    def initialize_solution(self, jsonfile):
        # the solution is encoder into float array such as [0.2, 0.3, 0.5, 0.1],
        # which can be converted into [1,2,3,0], and can be decoded into job-shop schedule by remainder operators
        processcount = 0
        for partid in range(self.jobnum):
            processnum = len(jsonfile[str(partid)])
            for processid in range(processnum):
                self.decodedict[str(processcount + processid)] = partid
            processcount += processnum
        return np.random.rand(processcount)

    def calculate_maskespan(self, jsonfile, array):
        """
        :param jsonfile: jsonfile
        :param array: possible solution, float array such as [0.2, 0.3, 0.5, 0.1], which can be decoded into job schedule
        :return:
        """
        array = np.argsort(array)
        array = list(map(lambda x: self.decodedict[str(x)], array))
        machine_operations, cmax = calculate_fjsp_greedy(jsonfile, array)
        self.temperature *= self.cooling_rate
        return machine_operations, cmax

    def get_neighbor(self, array):
        """
        :param array: the encoded solution
        :return:
        """
        neighbour = np.copy(array)

        # we get neighbor by swaping two processes or perturbing the solution randomly
        def swap(solution):
            idx1 = random.randint(0, len(solution) - 1)
            while True:
                idx2 = random.randint(0, len(solution) - 1)
                if idx2 != idx1:
                    break
            tmp = solution[idx1]
            solution[idx1] = solution[idx2]
            solution[idx2] = tmp
            return solution

        def perturb(solution):
            idx = np.random.randint(0, len(solution) - 1)
            perturbation = np.random.uniform(min(solution), max(solution))
            solution[idx] = solution[idx] + perturbation
            return solution

        prob = np.random.randint(0, 2)
        if prob:
            neighbour = swap(neighbour)
        else:
            neighbour = perturb(neighbour)
        self.iteration += 1
        return neighbour

    def get_best_neighbour_by_critical_path(self, operation, makespan, jsonfile, array):
        runtime = time.time()
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
                    decode = list(map(lambda x: self.decodedict[str(x)], np.argsort(neighbour)))
                    idx1 = [idx for idx, item in enumerate(decode) if item == partid1]
                    idx2 = [idx for idx, item in enumerate(decode) if item == partid2]
                    idx1, idx2 = idx1[processid1], idx2[processid2]

                    # swap
                    tmp = neighbour[idx1]
                    neighbour[idx1] = neighbour[idx2]
                    neighbour[idx2] = tmp
                    newoperation, newmakespan = self.calculate_maskespan(jsonfile, neighbour)
                    self.iteration += 1
                    if newmakespan < best_makespan:
                        best_neighbour = neighbour
                        best_makespan = newmakespan
                        best_operation = newoperation

                    # insert
                    neighbour = np.copy(array)
                    tmp = neighbour[max(idx1, idx2)]
                    neighbour = np.delete(neighbour, max(idx1, idx2))
                    neighbour = np.insert(neighbour, min(idx1, idx2), tmp)
                    newoperation, newmakespan = self.calculate_maskespan(jsonfile, neighbour)
                    self.iteration += 1
                    if newmakespan < best_makespan:
                        best_neighbour = neighbour
                        best_makespan = newmakespan
                        best_operation = newoperation

        runtime = time.time() - runtime
        print(f"cost {runtime} seconds, now iteration:{self.iteration}, critical path result:{best_makespan}")
        return best_neighbour, best_operation, best_makespan

    def solve(self, jsonfile):
        """
        :param order: order[j] denotes the order of the machines needed to execute job j,\
                      assert machine index range from (1,..,self.machinenum)
        :param time: time[j][i] denotes how long the process i of job j takes
        :return: the best found solution and its makespan
        """
        current_solution = self.initialize_solution(jsonfile)
        current_operation, current_makespan = self.calculate_maskespan(jsonfile, current_solution)
        self.best_solution = current_solution
        self.best_makespan = current_makespan
        self.best_operation = current_operation
        self.plateau = 0

        while self.temperature > self.stop_temperature:
            # get a neighbor solution and calculate the makespan
            # new_solution = self.get_neighbor(current_operation, current_makespan, current_solution)
            # new_operation, new_makespan = self.calculate_maskespan(jsonfile, new_solution)
            if self.plateau > 500 and self.use_critical_path:
                new_solution, new_operation, new_makespan = \
                    self.get_best_neighbour_by_critical_path(self.best_operation, self.best_makespan, jsonfile,
                                                             self.best_solution)
                self.plateau = 0
            else:
                new_solution = self.get_neighbor(current_solution)
                new_operation, new_makespan = self.calculate_maskespan(jsonfile, new_solution)

            # calculate the probability that the new solution is accepted
            if new_makespan < current_makespan:
                accept = 1.0
            else:
                accept = np.exp((current_makespan - new_makespan) / self.temperature)
            if random.random() < accept:
                current_solution = new_solution
                current_makespan = new_makespan
                current_operation = new_operation
                if new_makespan < self.best_makespan:
                    self.best_solution = new_solution
                    self.best_makespan = new_makespan
                    self.best_operation = new_operation
                    self.plateau = 0
                else:
                    self.plateau += 1
            if self.iteration % 100 == 1:
                print(f'iteration: {self.iteration}\t best makespan: {self.best_makespan} patience:{self.plateau}')

        return list(map(lambda x: self.decodedict[str(x)], np.argsort(self.best_solution))),\
            self.best_makespan, self.best_operation