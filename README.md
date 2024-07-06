### Instruction
The Job-shop Scheduling Problem (JSP) and Flexible Job-shop Scheduling Problem (FJSP) are crucial in manufacturing and service industries. JSP involves scheduling a set of jobs, each consisting of a sequence of operations, on a set of machines, with the objective of optimizing certain criteria such as minimizing the total completion time (makespan), reducing idle time, or balancing the workload. FJSP extends JSP by allowing operations to be processed on any machine from a set of available machines, providing additional flexibility but increasing the complexity of the problem.

Both JSP and FJSP are classified as NP-hard problems, meaning they are computationally intensive and difficult to solve exactly within polynomial time as the problem size increases. The complexity arises from the combinatorial nature of the problem, where the number of possible schedules grows exponentially with the number of jobs and machines.

Due to the NP-hard nature of JSP and FJSP, exact algorithms become impractical for large instances, leading to the widespread application of metaheuristic algorithms. Metaheuristic algorithms, such as Genetic Algorithms (GA), Simulated Annealing (SA), and Particle Swarm Optimization (PSO), offer robust and flexible frameworks to find high-quality solutions within reasonable computational time. These algorithms are inspired by natural processes and are designed to explore the solution space efficiently, avoiding local optima and finding near-optimal solutions.

####:hammer_and_wrench: This repository provides implementations of GA, SA, and PSO for solving JSP and FJSP. By leveraging these metaheuristic algorithms, the repository aims to offer effective and scalable solutions to these complex scheduling problems, demonstrating their applicability and efficiency in real-world scenarios.

### 📣 Principles of Metaheuristic algorithms
Detailed explanation of GA/SA/PSO implementation will be updated in the methods folder.

### 🚀 Get started
#### 1. Installation
You may install the dependencies by the following command.
```
pip install -e .
```
#### 2. Data Preparation
You may use the demo jsonfiles in the data direction. Or you need to convert your custom data into Json file, which can be read into 
```
{partid:
    {processid:
        [[available machine id1, time1],
         [available machine id2, time2],
         ...
        ],
    ...
    },
...
}
```

#### 3. Run Metaheuristic Algorithms
To run the metaheauristic algorithms, you may simp main.py.
```
python main.py --solver select/a/solver/from/GA/SA/PSO --datapath path/to/json/file
```
