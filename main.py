import time
import os
from process import Process
from Algorithms import FIFO, OPT, LRU, S_CLOCK, E_CLOCK
from utils import *
from colorama import Fore, init, Back, Style


def process_page_step(process, pages, function, page_list = None):
    # page_list is for OPT
    page_id, (page, rw) = pages

    if page >= process.total_pages:
        raise ValueError(f"Page {page} exceeds process total pages {process.total_pages}")

    # 检查页表中是否已有该页记录
    page_table = process.page_table
    page_data = page_table[page]  # list
    frame = int(page_data[1])
    old_page = None

    # 输出进程页表

    process.display_page_table()

    if page_data is None or int(page_data[2]) == 0:
        # 页面不存在 缺页中断
        # print(f"缺页中断：进程 {process.pid} 访问页面 {page}")

        frame_id, old_page = function.step((page, rw), page_id, page_list)

        process.frame[frame_id] = page
        out = 1
    else:
        frame_id = process.frame_list.index(frame)
        out = 0
    process.update_page_table((page, rw), frame_id, old_page)
    function.update((page, rw), page_id)
    process.update_table(page, out)
    return out


def main():
    A = Process(pid, frame_list, path_size, page_size)
    e_clock_pages = {
        'access': [0, 1, 3, 6, 2, 4, 5, 2, 5, 0, 3, 1, 2, 5, 4, 1, 0],
        'modify': [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0]
    }


if __name__ == '__main__':
    pid = 1
    page_size = 4096  # 4KB
    frame_list = [3, 5, 8, 10]
    path_size = page_size * 10
    A = Process(pid, frame_list, path_size, page_size)

    pages = {
        'access': [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1],
        'modify': [0] * 20
    }
    page_access = pages['access']
    page_modify = pages['modify']

    lru_pages = {
        'access': [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5],
        'modify': [0] * 12
    }

    clock_pages = {
        'access': [1, 3, 4, 2, 5, 4, 7, 4],
        'modify': [0] * 8
    }
    page_access = clock_pages['access']
    page_modify = clock_pages['modify']

    e_clock_pages = {
        'access': [0, 1, 3, 6, 2, 4, 5, 2, 5, 0, 3, 1, 2, 5, 4, 1, 0],
        'modify': [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0]
    }
    page_access = e_clock_pages['access']
    page_modify = e_clock_pages['modify']
    fifo_fun = E_CLOCK(A.frame_size)

    algorithms = ['OPT', 'FIFO', 'LRU', 'S_CLOCK', "E_CLOCK"]

    for algorithm in algorithms:
        A.reset()
        alg_fun = eval(algorithm)(A.frame_size)
        # print(Fore.CYAN + f'--------------- PID {A.pid} Use {Style.BRIGHT}{algorithm}{Style.NORMAL}---------------' + Fore.RESET)
        A.welcome(algorithm)
        for pages in enumerate(zip(page_access, page_modify)):
            fault = process_page_step(A, pages, alg_fun, page_access)
        # print(Fore.CYAN + f'--------------- {Style.BRIGHT}{algorithm}{Style.NORMAL} Page Table ---------------' + Fore.RESET)
        A.show_page_table(algorithm)
        # print(Fore.CYAN + f'--------------- {Style.BRIGHT}{algorithm}{Style.NORMAL} Frame Table ---------------' + Fore.RESET)
        A.show_table(algorithm)
        print('\n\n')

    # print(f"进程{A.pid}正在访问")
    # for pages in enumerate(zip(page_access, page_modify)):
    #     fault = process_page_step(A, pages, fifo_fun, page_access)
    #     # A.display_frame()
    # A.show_page_table()
    # A.show_table()
