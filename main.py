import json

# import solvers
from methods.GA import GASolver
from methods.SA import SASolver
from methods.PSO import PSOSolver
# calculate makespan
from utils.Calculate import *
# plot gantt chart
from utils.Gantt import *

import argparse

parser = argparse.ArgumentParser(description='System Dispatch')
parser.add_argument('--datapath', type=str, default='./data/ta40.json',
                    help='path to json file')
parser.add_argument('--savepath', type=str, default='',
                    help='path to save job schedule and gantt plot')
parser.add_argument('--solver', type=str, default='SA',
                    help='Available solvers include GA, SA, and PSO')
parser.add_argument('--use_critical_path', type=bool, default=True,
                    help='whether to use critical path in obtaining new solution')
# args for SASolver
parser.add_argument('--initial_temperature', type=float, default=100000)
parser.add_argument('--cooling_rate', type=float, default=0.9995)
parser.add_argument('--stop_temperature', type=float, default=1e-15)
# args for GASolver
parser.add_argument('--population_num', type=int, default=100)
parser.add_argument('--crossover_rate', type=float, default=0.90)
parser.add_argument('--mutation_rate', type=float, default=0.90)
parser.add_argument('--selection_rate', type=float, default=0.30)
parser.add_argument('--selection_mode', type=str, default='competition',
                    help='Available methods include random, competition and elitism, the last two recommended')
parser.add_argument('--ga_iteration', type=int, default=1000000)
# args for PSOSolver
parser.add_argument('--particle_num', type=int, default=30)
parser.add_argument('--pso_iteration', type=int, default=100000)
parser.add_argument('--w', type=float, default=0.3)
parser.add_argument('--c1', type=float, default=1.0)
parser.add_argument('--c2', type=float, default=2.0)
parser.add_argument('--w_min', type=float, default=0.1)
parser.add_argument('--w_damp', type=float, default=0.99)
parser.add_argument('--tabu_tenure', type=int, default=100)
parser.add_argument('--mutation_prob', type=float, default=0.5)
args = parser.parse_args()


def main():
    with open(args.datapath, 'r') as file:
        jsonfile = json.load(file)
    if 'sa' in args.solver.lower():
        solver = SASolver(jobnum=int(jsonfile['partnum']),
                          machinenum=int(jsonfile['machinenum']),
                          use_critical_path=args.use_critical_path,
                          initial_temperature=args.initial_temperature,
                          cooling_rate=args.cooling_rate,
                          stop_temperature=args.stop_temperature)
    elif 'ga' in args.solver.lower():
        solver = GASolver(jobnum=int(jsonfile['partnum']),
                          machinenum=int(jsonfile['machinenum']),
                          use_critical_path=args.use_critical_path,
                          population=args.population_num,
                          crossover=args.crossover_rate,
                          mutation=args.mutation_rate,
                          selection=args.selection_rate,
                          selectionmethod=args.selection_mode,
                          iteration=args.ga_iteration)
    elif 'pso' in args.solver.lower():
        solver = PSOSolver(job_num=int(jsonfile['partnum']),
                           process_num=int(jsonfile['machinenum']),
                           num_particles=args.particle_num,
                           max_iterations=args.pso_iteration,
                           w=args.w, c1=args.c1, c2=args.c2, w_min=args.w_min,
                           w_damp=args.w_damp, tabu_tenure=args.tabu_tenure, mutation_prob=args.mutation_prob)
    else:
        raise NotImplementedError
    best_solution, best_makespan, best_operation = solver.solve(jsonfile)
    filename = args.datapath.split('/')[-1].split('.')[0]
    plot_gantt_chart(best_operation, savepath=f'{filename}-{args.solver}.html')


if __name__ == '__main__':
    main()
