import time
import os
from process import Process
from Algorithms import FIFO, OPT, LRU, S_CLOCK, E_CLOCK
from utils import *
import argparse
import random
import numpy as np

# Parse configuration settings using command-line arguments
def get_config(args = None):
    parser = argparse.ArgumentParser()

    # Define argument for memory page size (in KB)
    parser.add_argument('--page_size', type = int, default = 4,
                        help = 'The size of each memory page in kilobytes (KB). Determines the granularity of memory allocation and paging operations.')
    # Define argument for the number of processes
    parser.add_argument('--pid_num', type = int, default = 3,
                        help = 'Number of processes to simulate. Represents the total number of processes in the system.')
    # Define argument for the number of page sequences to generate
    parser.add_argument('--page_seq_count', type = int, default = 10,
                        help = 'Number of page sequences to generate for testing.')
    # Define argument for the number of frames allocated per process
    parser.add_argument('--frame_per_process', type = int, default = 5,
                        help = 'Number of physical frames allocated to each process.')
    # Define argument for the maximum number of pages in a process page table
    parser.add_argument('--max_pages', type = int, default = 8,
                        help = 'Maximum number of pages in a process page table.')
    # Define argument for the length range of the access sequence
    parser.add_argument('--sequence_length', type = list, default = [8, 20],
                        help = 'Length of the access sequence.')
    # Define random seed for reproducibility
    parser.add_argument('--seed', type = int, default = 42)
    # Define available page replacement algorithms
    parser.add_argument('--algorithm', type = list, default = ['OPT', 'FIFO', 'LRU', 'S_CLOCK', 'E_CLOCK'])

    config = parser.parse_args(args)

    # Convert page size to bytes and calculate total logic size and max frames
    config.page_size = config.page_size * 1024
    config.logic_size = config.max_pages * config.page_size
    config.max_frames = config.frame_per_process * config.pid_num + 10

    # Define the minimum and maximum access sequence lengths
    config.min_sequence_length = int(config.sequence_length[0])
    config.max_sequence_length = int(config.sequence_length[1])
    return config


# Allocate frames for each process randomly
def allocate_frames(total_frames, num_processes, frames_per_process):
    all_frames = list(range(total_frames))
    random.shuffle(all_frames)

    allocations = {}
    for pid in range(num_processes):
        allocations[pid] = all_frames[:frames_per_process]
        all_frames = all_frames[frames_per_process:]
    return allocations


# Generate a random memory access sequence for testing
def generate_access_sequence(max_page, length):
    if max_page < 1 or length < 1:
        raise ValueError('Both max_page and length must be greater than 0')

    # Generate random page access and modify bit sequences
    access_sequence = [random.randint(0, max_page - 1) for _ in range(length)]
    modify_bits = [random.randint(0, 1) for _ in range(length)]

    return {
        'access': access_sequence,
        'modify': modify_bits
    }


# Perform a single step in page processing
def process_page_step(process, pages, function, page_list = None):
    page_id, (page, rw) = pages
    if page >= process.total_pages:
        raise ValueError(f"Page {page} exceeds process total pages {process.total_pages}")

    # Check if the page exists in the page table
    page_table = process.page_table
    page_data = page_table[page]
    frame = page_data[1]
    old_page = None

    if page_data is None or page_data[2] == 0:
        # Page not in memory, trigger page fault
        frame_id, old_page = function.step((page, rw), page_id, page_list)
        process.frame[frame_id] = page
        out = 1
    else:
        # Page already in memory
        frame_id = process.frame_list.index(frame)
        out = 0

    # Update the page table and algorithm state
    process.update_page_table((page, rw), frame_id, old_page)
    function.update((page, rw), page_id)
    process.update_table((page, rw), out)
    return out


# Main function for simulating memory management and page replacement
def main():
    # Load configuration and initialize random seeds
    config = get_config()
    random.seed(config.seed)
    np.random.seed(config.seed)

    # Allocate frames to processes
    Process_allocations = allocate_frames(config.max_frames, config.pid_num, config.frame_per_process)
    Process_list = []

    # Create a list of process objects
    for pid in range(config.pid_num):
        tmp_process = Process(pid, Process_allocations[pid], config.logic_size, config.page_size)
        Process_list.append(tmp_process)

    algorithms = config.algorithm
    results = {algorithm: 0 for algorithm in algorithms}
    access_n = 0

    # Simulate multiple page sequences
    for _ in range(config.page_seq_count):
        for tmp_process in Process_list:
            # Generate access sequences
            length = random.randint(config.min_sequence_length, config.max_sequence_length)
            tmp_access_pages = generate_access_sequence(config.max_pages, length)
            page_access = tmp_access_pages['access']
            page_modify = tmp_access_pages['modify']

            access_n += length

            for algorithm in algorithms:
                # Reset process and use specified algorithm
                tmp_process.reset()
                alg_fun = eval(algorithm)(tmp_process.frame_size)

                # Simulate each page access
                for alg_pages in enumerate(zip(page_access, page_modify)):
                    fault = process_page_step(tmp_process, alg_pages, alg_fun, page_access)
                    results[algorithm] += fault

    # Display results
    show_fault_table(results, access_n)


if __name__ == "__main__":
    main()
