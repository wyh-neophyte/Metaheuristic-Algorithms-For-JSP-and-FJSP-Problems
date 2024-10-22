
# Metaheuristic Algorithms for JSP and FJSP Problems

This repository provides implementations of **Genetic Algorithms (GA)**, **Simulated Annealing (SA)**, and **Particle Swarm Optimization (PSO)** for solving the **Job-shop Scheduling Problem (JSP)** and **Flexible Job-shop Scheduling Problem (FJSP)**. These are complex optimization problems frequently encountered in manufacturing and service industries.

---

## 📖 Introduction

### What are JSP and FJSP?  
- **JSP**: A scheduling problem where a set of jobs, each with multiple operations, must be assigned to machines in a specific sequence. The goal is to **minimize makespan**, **reduce idle time**, or **balance workload**.
- **FJSP**: A variant of JSP that allows each operation to be processed on **multiple alternative machines**, increasing flexibility but also complexity.

Both JSP and FJSP are **NP-hard problems**, meaning exact solutions are impractical for large instances. This repository demonstrates the use of **metaheuristic algorithms** to efficiently find near-optimal solutions.

---

## ⚙️ Algorithms Implemented
1. **Genetic Algorithm (GA)**: Mimics evolution through selection, crossover, and mutation to explore the solution space.
2. **Simulated Annealing (SA)**: Models the cooling of metals, gradually refining solutions to escape local optima.
3. **Particle Swarm Optimization (PSO)**: Simulates the social behavior of birds to explore the solution space collectively.

These algorithms are ideal for **avoiding local minima** and **exploring large solution spaces** efficiently.

---

## 🚀 Getting Started

### 1. Installation
Ensure Python is installed, then set up the environment:

```bash
pip install -e .
pip install -r requirements.txt
```

---

### 2. Data Preparation
You can use the provided example datasets (e.g., `mk01.txt`) or prepare your own. Custom data should follow this JSON format:

```json
{
    "part1": {
        "process1": [[1, 5], [2, 3]],
        "process2": [[1, 8], [3, 6]]
    },
    "part2": {
        "process1": [[2, 7], [3, 2]]
    }
}
```

Each **process** lists the available machines and their respective processing times.

---

### 3. Running the Algorithms

To run a selected algorithm, execute the following command:

```bash
python main.py --solver GA --datapath ./data/mk01.json
```

Replace `GA` with `SA` or `PSO` depending on the algorithm you want to test. You can also modify **hyperparameters** within the algorithm scripts inside the `methods/` directory.

---

## 📊 Results

Results will be saved to the **`results/`** folder. Each result includes the following:
- **Makespan** (total completion time)
- **Machine utilization**
- **Gantt chart visualization** (optional: for visualizing schedules)

---

## 📂 Directory Structure

```
Metaheuristic-Algorithms-For-JSP-and-FJSP-Problems/
│
├── data/                # Sample datasets
├── methods/             # Algorithm implementations
├── results/             # Output files
├── utils/               # Helper functions
├── main.py              # Entry point for running algorithms
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## 🔧 Tuning and Customization

To modify the behavior of each algorithm:
- **GA**: Adjust mutation and crossover rates.
- **SA**: Modify the cooling schedule or initial temperature.
- **PSO**: Tune the inertia weight or cognitive/social parameters.

---

## 📑 Acknowledgements and References
This project is based on our own understanding of metaheuristic algorithms. You can explore related research and methodologies in the following papers:
- [Metaheuristics in Scheduling](https://www.sciencedirect.com/topics/computer-science/job-shop-scheduling)
- Example datasets: **[Brandimarte's instances](https://www.brandimarte.com/)** [8†source].

---

## 📬 Contact

For questions or feedback, feel free to open an issue or contact the repository owner via GitHub: [wyh-neophyte](https://github.com/wyh-neophyte)【7†source】.

---

