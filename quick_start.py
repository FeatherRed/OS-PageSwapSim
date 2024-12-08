import time
import os
from process import Process
from Algorithms import FIFO, OPT, LRU, S_CLOCK, E_CLOCK
from utils import *
from colorama import Fore, init, Back, Style


def process_page_step(process, pages, function, page_list = None):
    """
    Simulates a single step in the page access process for a given process.

    Args:
        process: The process object whose pages are being accessed.
        pages: Tuple containing page ID and access type (read/write).
        function: Page replacement strategy object with step and update methods.
        page_list: Optional list of pages for certain strategies like OPT.

    Returns:
        int: 1 if a page fault occurs, otherwise 0.
    """
    # Unpack the page details
    page_id, (page, rw) = pages

    # Check if the page number exceeds the total number of pages in the process
    if page >= process.total_pages:
        raise ValueError(f"Page {page} exceeds process total pages {process.total_pages}")

    # Retrieve the process page table and data for the requested page
    page_table = process.page_table
    page_data = page_table[page]
    frame = page_data[1]  # Physical frame ID
    old_page = None

    # Check if the page exists in memory or a page fault occurs
    if page_data is None or page_data[2] == 0:
        # Page fault: The requested page is not in memory
        process.display_page_table((page, rw), flag = 0)
        # Perform the page replacement step
        frame_id, old_page = function.step((page, rw), page_id, page_list)
        # Update the frame with the new page
        process.frame[frame_id] = page
        page_fault = 1
    else:
        # Page is already in memory; no page fault
        process.display_page_table((page, rw), flag = 1)
        frame_id = process.frame_list.index(frame)
        page_fault = 0

    # Update the process page table and page replacement strategy state
    process.update_page_table((page, rw), frame_id, old_page)
    function.update((page, rw), page_id)
    # Update the memory table for visualization
    process.update_table((page, rw), page_fault)
    return page_fault


if __name__ == '__main__':
    pid = 1
    page_size = 4096  # 4KB
    frame_list = [3, 5, 8, 10]
    path_size = page_size * 10
    A = Process(pid, frame_list, path_size, page_size)

    e_clock_pages = {
        'access': [0, 1, 3, 6, 2, 4, 5, 2, 5, 0, 3, 1, 2, 5, 4, 1, 0],
        'modify': [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0]
    }
    page_access = e_clock_pages['access']
    page_modify = e_clock_pages['modify']
    # fifo_fun = E_CLOCK(A.frame_size)

    algorithms = ['OPT', 'FIFO', 'LRU', 'S_CLOCK', "E_CLOCK"]
    algorithms_table = [None]
    alg_faults = {}
    for algorithm in algorithms:
        alg_faults[algorithm] = 0
    for algorithm in algorithms:
        A.reset()
        alg_fun = eval(algorithm)(A.frame_size)
        # print(Fore.CYAN + f'--------------- PID {A.pid} Use {Style.BRIGHT}{algorithm}{Style.NORMAL}---------------' + Fore.RESET)
        A.welcome(algorithm)
        total_fault = 0
        for pages in enumerate(zip(page_access, page_modify)):
            fault = process_page_step(A, pages, alg_fun, page_access)
            total_fault += fault
        alg_faults[algorithm] = total_fault
        # print(Fore.CYAN + f'--------------- {Style.BRIGHT}{algorithm}{Style.NORMAL} Page Table ---------------' + Fore.RESET)
        A.show_page_table(algorithm)
        # print(Fore.CYAN + f'--------------- {Style.BRIGHT}{algorithm}{Style.NORMAL} Frame Table ---------------' + Fore.RESET)
        # A.show_table(algorithm)
        algorithms_table[0] = A.headers if algorithms_table[0] is None else algorithms_table[0]
        algorithms_table.append(A.table)
        print('\n\n')
    show_all_table(algorithms_table)
    show_fault_table(alg_faults, len(page_access))
