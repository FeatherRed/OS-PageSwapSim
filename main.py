import time
import os
from process import Process
from utils import FIFO, OPT, LRU, S_CLOCK, E_CLOCK

def process_page_step(process, pages, function, page_list = None):
    # page_list is for OPT
    page_id, (page, rw) = pages

    if page >= process.total_pages:
        raise ValueError(f"Page {page} exceeds process total pages {process.total_pages}")

    # todo 快表

    # 检查页表中是否已有该页记录
    page_table = process.page_table
    page_data = page_table.get(page, None)

    if page_data is None or page_data['valid_bit'] == 0:
        # 页面不存在 缺页中断
        # print(f"缺页中断：进程 {process.pid} 访问页面 {page}")

        frame_id, old_page = function.step((page, rw), page_id, page_list)

        # board
        if old_page is None:
            pass
            # print(f"分配物理块 {process.frame_list[frame_id]} 给页面 {page}")
        else:
            # print(f"替换页面 {old_page}, 将物理块 {process.frame_list[frame_id]} 分配给页面 {page}")
            page_table[old_page] = {
                'frame': -1,
                'valid_bit': 0,
                'access_bit': 0,
                'modify_bit': 0,
                'swap_address': None
            }
        # 更新
        page_table[page] = {
            'frame': process.frame_list[frame_id],
            'valid_bit': 1,
            'access_bit': 1,
            'modify_bit': rw,
            'swap_address': None
        }
        process.frame[frame_id] = page
        out = 1
    else:
        page_table[page]['modify_bit'] = rw
        out = 0
    function.update((page, rw), page_id)
    process.update_table(page, out)
    return out



if __name__ == '__main__':
    pid = 1
    page_size = 4096  # 4KB
    frame_list = [3, 5, 8, 10]
    path_size = page_size * 10
    A = Process(pid, frame_list, path_size, page_size)


    pages = {
        'access': [7, 0, 1, 2, 0, 3, 0,4,2,3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1],
        'modify': [0] * 20
    }
    page_access = pages['access']
    page_modify = pages['modify']

    lru_pages = {
        'access': [1,2,3,4,1,2,5,1,2,3,4,5],
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
    for pages in enumerate(zip(page_access, page_modify)):
        fault = process_page_step(A, pages, fifo_fun, page_access)
        # A.display_frame()
    A.show_table()