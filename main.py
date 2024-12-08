import time
import os
from process import Process
from Algorithms import FIFO, OPT, LRU, S_CLOCK, E_CLOCK
from utils import *
import argparse
import random
import numpy as np
def get_config(args = None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--page_size', type = int, default = 4,
                        help = 'The size of each memory page in kilobytes (KB). Determines the granularity of memory allocation and paging operations.')
    parser.add_argument('--pid_num', type = int, default = 3, help='Number of processes to simulate. Represents the total number of processes in the system.')
    parser.add_argument('--page_seq_count', type = int, default = 10,
                        help = 'Number of page sequences to generate for testing.')
    parser.add_argument('--frame_per_process', type = int, default = 5,
                        help = 'Number of physical frames allocated to each process.')
    parser.add_argument('--max_pages', type = int, default = 8,
                        help = 'Maximum number of pages in a process page table.')
    parser.add_argument('--sequence_length', type = list, default = [8, 20],
                        help = 'Length of the access sequence.')
    parser.add_argument('--seed', type = int, default = 42)
    parser.add_argument('--algorithm', type = list, default = ['OPT', 'FIFO', 'LRU', 'S_CLOCK', 'E_CLOCK'])


    config = parser.parse_args(args)

    config.page_size = config.page_size * 1024
    config.logic_size = config.max_pages * config.page_size
    config.max_frames = config.frame_per_process * config.pid_num + 10

    config.min_sequence_length = int(config.sequence_length[0])
    config.max_sequence_length = int(config.sequence_length[1])
    return config

def allocate_frames(total_frames, num_processes, frames_per_process):
    all_frames = list(range(total_frames))
    random.shuffle(all_frames)

    allocations = {}
    for pid in range(num_processes):
        allocations[pid] = all_frames[: frames_per_process]
        all_frames = all_frames[frames_per_process:]
    return allocations

def generate_access_sequence(max_page, length):
    if max_page < 1 or length < 1:
        raise ValueError('Both max_page and length must be greater than 0')

    access_sequence = [random.randint(0, max_page - 1) for _ in range(length)]
    modify_bits = [random.randint(0, 1) for _ in range(length)]

    return {
        'access': access_sequence,
        'modify': modify_bits
    }

def process_page_step(process, pages, function, page_list = None):
    page_id, (page, rw) = pages
    if page >= process.total_pages:
        raise ValueError(f"Page {page} exceeds process total pages {process.total_pages}")

        # 检查页表中是否已有该页记录
    page_table = process.page_table
    page_data = page_table[page]  # list
    frame = page_data[1]
    old_page = None
    if page_data is None or page_data[2] == 0:
        # 页面不存在 缺页中断
        # print(f"缺页中断：进程 {process.pid} 访问页面 {page}")
        # process.display_page_table((page, rw), flag = 1)
        frame_id, old_page = function.step((page, rw), page_id, page_list)

        process.frame[frame_id] = page
        out = 1
    else:
        # process.display_page_table((page, rw), flag = 0)
        frame_id = process.frame_list.index(frame)
        out = 0
    process.update_page_table((page, rw), frame_id, old_page)
    function.update((page, rw), page_id)
    process.update_table((page, rw), out)
    return out

def main():
    config = get_config()
    random.seed(config.seed)
    np.random.seed(config.seed)
    Process_allocations = allocate_frames(config.max_frames, config.pid_num, config.frame_per_process)
    Process_list = []

    for pid in range(config.pid_num):
        tmp_process = Process(pid, Process_allocations[pid], config.logic_size, config.page_size)
        Process_list.append(tmp_process)

    algorithms = config.algorithm

    results = {}
    for algorithm in algorithms:
        results[algorithm] = 0
    access_n = 0
    for _ in range(config.page_seq_count):
        # 循环每个进程
        for tmp_process in Process_list:
            # 循环每个算法

            length = random.randint(config.min_sequence_length, config.max_sequence_length)
            tmp_access_pages = generate_access_sequence(config.max_pages, length)
            page_access = tmp_access_pages['access']
            page_modify = tmp_access_pages['modify']

            access_n += length
            for algorithm in algorithms:
                tmp_process.reset()
                alg_fun = eval(algorithm)(tmp_process.frame_size)

                for alg_pages in enumerate(zip(page_access, page_modify)):
                    fault = process_page_step(tmp_process, alg_pages, alg_fun, page_access)
                    results[algorithm] += fault

    show_fault_table(results, access_n)

if __name__ == "__main__":
    main()