import numpy as np
import random
from collections import Counter
import copy
from utils.Calculate import *


class PSOSolver:
    def __init__(self, job_num, process_num, num_particles=30, max_iterations=100000, w=0.3, c1=1.0, c2=2.0, w_min=0.1,
                 w_damp=0.99, tabu_tenure=100, mutation_prob=0.5):
        self.job_num = job_num
        self.process_num = process_num
        self.gen_length = job_num * process_num
        self.num_particles = num_particles
        self.max_iterations = max_iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.w_min = w_min
        self.w_damp = w_damp
        self.tabu_tenure = tabu_tenure
        self.tabu_list = []
        self.mutation_prob = mutation_prob
        self.real_data = {}
        self.no_improvement_count = 0
        self.use_critical_path_update = True
        self.global_best_scores = []
        self.global_best_score = 10000
        self.iteration_best_scores = []

    def initialize_particles(self, jsonfile):
        particles = []
        for i in range(self.num_particles):
            particle = []
            for i in range(self.job_num):
                particle.extend([i] * len(jsonfile[f"{i}"]))

            count = Counter(particle)  # Count the number of occurrences of each element
            unique_elements = list(count.keys())  # Get all unique elements
            result = []  
            max_length = max(count.values())  #  Find the number of occurrences of the element with the most occurrences

            # 创建一个字典来存储每个元素的随机排列
            random_order = {num: random.sample([num] * count[num], count[num]) for num in unique_elements}

            for i in range(max_length):
                random.shuffle(unique_elements)  # Randomise the unique elements in each round of the loop
                for num in unique_elements:
                    if random_order[num]:  
                        result.append(random_order[num].pop(0))

            particles.append(result)
        return particles

    def fitness_function(self, particle, jsonfile):
        job_order = particle
        operations, C_max = calculate_fjsp_greedy(jsonfile, job_order)
        critical_path = find_critical_path(operations, C_max)
        return C_max, critical_path

    def critical_path_exchange(self, particle, critical_path):
        mark_list = [0] * len(particle)
        particle_for_exchange = copy.deepcopy(particle)
        block_num = 1
        # 标记关键路径中的任务
        for j, process in critical_path:
            count = 0
            for k in range(len(particle_for_exchange)):
                if particle_for_exchange[k] == j:
                    if count == process:
                        mark_list[k] = block_num
                        block_num += 1
                    count += 1
        return mark_list

    def update_velocity(self, velocities, particles, personal_best_positions, global_best_position):
        for i in range(len(particles)):
            r1 = np.random.rand()
            r2 = np.random.rand()
            v_max = 15.0  # 假设最大速度限制为15.0
            sum = self.w + self.c1 * r1 + self.c2 * r2
            for j in range(len(particles[i])):
                velocities[i][j] = (
                        self.w/sum * velocities[i][j] +
                        self.c1 * r1/sum * (personal_best_positions[i][j] - particles[i][j]) +
                        self.c2 * r2/sum * (global_best_position[j] - particles[i][j])
                )
                # 速度限制
                if velocities[i][j] > v_max:
                    velocities[i][j] = v_max
                elif velocities[i][j] < -v_max:
                    velocities[i][j] = -v_max

        return velocities

    def update_particles(self, particles, velocities):
        for i in range(len(particles)):

            updated_particle = np.array(particles[i]) + np.array(velocities[i])

            sorted_indices = sorted(range(len(updated_particle)), key = lambda k:updated_particle[k])

            sorted_par = sorted(particles[i])

            updated_particle = [0] * len(particles[i])
            for idx, sorted_idx in enumerate(sorted_indices):
                updated_particle[sorted_idx] = sorted_par[idx]

            if random.random() < self.mutation_prob:
                num_mutations = random.randint(2, int(self.job_num/2))  # 随机选择2到20个工序进行交换
                for _ in range(num_mutations):
                    mutation_point = random.randint(0, len(updated_particle) - 1)
                    swap_point = random.randint(0, len(updated_particle) - 1)
                    updated_particle[mutation_point], updated_particle[swap_point] = updated_particle[swap_point], updated_particle[mutation_point]
            # 更新粒子
            particles[i] = updated_particle

        # 返回更新后的粒子群
        return particles

    def update_particles_critical(self, particles, velocities, jsonfile):
        for i in range(len(particles)):
            # 更新粒子位置
            updated_particle = np.array(particles[i]) + np.array(velocities[i])
            updated_particle = np.round(updated_particle).astype(int)
            updated_particle = np.clip(updated_particle, 0, self.job_num - 1)

            # 计算关键路径
            _, critical_path = self.fitness_function(particles[i], jsonfile)
            mark_list = self.critical_path_exchange(particles[i], critical_path)

            unique_block_nums = sorted(set(mark_list))
            block_updated = False
            critical_path_len = 1  #  Initial number of critical process blocks

            while not block_updated and critical_path_len <= len(unique_block_nums):
                for block_num in unique_block_nums:
                    if block_num != 0:
                        critical_indices = [j for j in range(len(particles[i])) if mark_list[j] == block_num]
                        if len(critical_indices) <= 1:
                            continue  # If there is only one process in the block, the update is skipped

                        # 更新当前关键路径块
                        to_updated_critical = [updated_particle[j] for j in critical_indices[:critical_path_len]]
                        critical_values = [particles[i][j] for j in critical_indices[:critical_path_len]]

                        # 对当前块的关键路径值进行排序
                        sorted_indices = sorted(range(len(to_updated_critical)), key=lambda k: to_updated_critical[k])
                        sorted_list2 = sorted(critical_values)

                        # 按照排序后的索引更新关键路径任务的位置
                        for idx, tmp in enumerate(sorted_indices):
                            updated_particle[critical_indices[idx]] = sorted_list2[tmp]

                        # 检查禁忌列表
                        if list(updated_particle) not in self.tabu_list:
                            self.tabu_list.append(list(updated_particle))
                            if len(self.tabu_list) > self.tabu_tenure:
                                self.tabu_list.pop(0)  # 维持禁忌列表的长度
                            block_updated = True
                            break
                        else:
                            updated_particle = particles[i]  

                if not block_updated:
                    critical_path_len += 1  # 增加关键工序块数量

            if not block_updated:
                # 如果没有任何关键路径块被更新，则保持原始粒子
                updated_particle = particles[i]

            # 保持非关键路径任务的位置不变
            for j in range(len(updated_particle)):
                if mark_list[j] == 0:
                    updated_particle[j] = particles[i][j]

            # 确保粒子合法性
            job_counts = np.bincount(updated_particle, minlength=self.job_num)
            new_particle = []
            for job in range(self.job_num):
                new_particle.extend([job] * job_counts[job])
            sorted_indices = np.argsort(updated_particle)
            sorted_new_particle = np.array(new_particle)[sorted_indices]
            particles[i] = sorted_new_particle

            # 引入变异操作以增加多样性
            if random.random() < self.mutation_prob:
                num_mutations = random.randint(2, 10)  # 随机选择2到10个工序进行交换
                for _ in range(num_mutations):
                    mutation_point = random.randint(0, len(updated_particle) - 1)
                    swap_point = random.randint(0, len(updated_particle) - 1)
                    updated_particle[mutation_point], updated_particle[swap_point] = updated_particle[swap_point], \
                    updated_particle[mutation_point]

        return particles

    def solve(self, jsonfile):
        particles = self.initialize_particles(jsonfile)
        velocities = [np.zeros_like(particle) for particle in particles]

        personal_best_positions = copy.deepcopy(particles)
        personal_best_scores = []
        for p in particles:
            C_max_personal, _ = self.fitness_function(p, jsonfile)
            personal_best_scores.append(C_max_personal)
        global_best_position = personal_best_positions[np.argmin(personal_best_scores)]
        self.global_best_score = min(personal_best_scores)
        best_operations, best_makespan = None, None

        for iteration in range(self.max_iterations):
            velocities = self.update_velocity(velocities, particles, personal_best_positions, global_best_position)

            # 根据标志使用不同的更新方法
            if self.use_critical_path_update:
                particles = self.update_particles_critical(particles, velocities, jsonfile)
            else:
                particles = self.update_particles(particles, velocities)

            iteration_scores = []
            for i in range(len(particles)):
                score, _ = self.fitness_function(particles[i], jsonfile)
                iteration_scores.append(score)
                if score < personal_best_scores[i]:
                    personal_best_scores[i] = score
                    personal_best_positions[i] = particles[i].copy()

            best_particle_index = np.argmin(personal_best_scores)
            if personal_best_scores[best_particle_index] < self.global_best_score:
                self.global_best_score = personal_best_scores[best_particle_index]
                global_best_position = personal_best_positions[best_particle_index].copy()
                self.no_improvement_count = 0  # 重置计数器
            else:
                self.no_improvement_count += 1  # 没有改进时计数加1

            # 如果连续10次没有改进，切换更新方法
            if self.no_improvement_count >= 10:
                self.use_critical_path_update = not self.use_critical_path_update
                self.no_improvement_count = 0  # 重置计数器

            # 记录全局最优和当前种群最优
            self.global_best_scores.append(self.global_best_score)
            self.iteration_best_scores.append(min(iteration_scores))

            print(f"Iteration {iteration + 1}/{self.max_iterations}, Best C_max: {self.global_best_score}, Current Iteration Best: {min(iteration_scores)}, counter: {self.no_improvement_count+1}, critical: {self.use_critical_path_update}")
            self.w = max(self.w_min, self.w * self.w_damp)

            best_operations, best_makespan = calculate_fjsp_greedy(jsonfile, global_best_position)

        return global_best_position, best_makespan, best_operations
