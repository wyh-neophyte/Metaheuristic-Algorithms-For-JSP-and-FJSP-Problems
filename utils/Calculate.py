import random


def find_critical_path(machine_operations, Cmax):
    """
    :param machine_operations:
    :param Cmax: makespan
    :return: [[part_id, process_id, start_time, end_time], ...]
    the {process_id + 1} process of the {part_id + 1} part starts from {start_time} and ends at {end_time}
    """
    from collections import defaultdict

    critical_path = []
    current_time = Cmax

    end_time_lookup = defaultdict(list)
    for machine_id, operations in machine_operations.items():
        for operation in operations:
            job_id, process_id, start_time, end_time = operation
            end_time_lookup[end_time].append((machine_id, operation))

    def dfs(current_time, path, visited):
        nonlocal critical_path
        if len(path) > len(critical_path):
            critical_path = path.copy()
        if current_time == 0:
            return
        if current_time not in end_time_lookup:
            return
        for machine_id, operation in end_time_lookup[current_time]:
            job_id, process_id, start_time, end_time = operation
            if (machine_id, job_id, process_id) not in visited:
                visited.add((machine_id, job_id, process_id))
                path.append([machine_id, operation])
                dfs(start_time, path, visited)
                path.pop()
                visited.remove((machine_id, job_id, process_id))

    dfs(current_time, [], set())
    critical_path.reverse()
    return critical_path


def calculate_fjsp_greedy(jsonfile, joborder, greedyrule=True):
    """
    :param jsonfile:
    :return: machine_operations
    """
    partnum = jsonfile['partnum']
    machinenum = jsonfile['machinenum']

    job_completion_time = {i: 0 for i in range(partnum)}
    job_operation_count = {i: 0 for i in range(partnum)}

    machine_avail_time = {i: 0 for i in range(machinenum)}
    machine_operations = {i: [] for i in range(machinenum)}

    for jobid in joborder:
        processid = job_operation_count[jobid]
        job_operation_count[jobid] += 1

        if greedyrule:
            best_avail_machine = None
            for idx, (machineid, processing_time) in enumerate(jsonfile[str(jobid)][str(processid)]):
                # find the earliest time to start
                starttime = max(job_completion_time[jobid], machine_avail_time[machineid])
                endtime = starttime + processing_time
                if best_avail_machine is None:
                    best_avail_machine = [machineid, (jobid, processid, starttime, endtime)]
                elif best_avail_machine[-1][-1] > endtime:
                    best_avail_machine = [machineid, (jobid, processid, starttime, endtime)]
        else:
            randomidx = random.randint(0, len(jsonfile[str(jobid)][str(processid)])-1)
            machineid, processing_time = jsonfile[str(jobid)][str(processid)][randomidx]
            starttime = max(job_completion_time[jobid], machine_avail_time[machineid])
            endtime = starttime + processing_time
            best_avail_machine = [machineid, (jobid, processid, starttime, endtime)]

        machineid, (jobid, processid, starttime, endtime) = best_avail_machine
        machine_operations[machineid].append((jobid, processid, starttime, endtime))
        job_completion_time[jobid] = endtime
        machine_avail_time[machineid] = endtime

    # calculate the makespan
    Cmax = max(machine_avail_time.values())

    return machine_operations, Cmax

