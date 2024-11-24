import time
import os
from process import Process

class fifo:
    def __init__(self, frame_size):
        self.frame_size = frame_size
        self.frame = []
        self.pointer = 0

    def reset(self):
        self.frame = []
        self.pointer = 0

    def step(self, page):
        old_page = None
        if len(self.frame) < self.frame_size:
            self.frame.append(page)
            frame_id = len(self.frame) - 1
        else:
            old_page = self.frame[self.pointer]
            self.frame[self.pointer] = page
            frame_id = self.pointer
            self.pointer = (self.pointer + 1) % self.frame_size
        return frame_id, old_page


def process_page_step(process, pages, function):
    page, rw = pages

    if page >= process.total_pages:
        raise ValueError(f"Page {page} exceeds process total pages {process.total_pages}")

    # todo 快表

    # 检查页表中是否已有该页记录
    page_table = process.page_table
    page_data = page_table.get(page, None)

    if page_data is None or page_data['valid_bit'] == 0:
        # 页面不存在 缺页中断
        # print(f"缺页中断：进程 {process.pid} 访问页面 {page}")

        frame_id, old_page = function.step(page)

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
    process.update_table(page, out)
    return out



if __name__ == '__main__':
    pid = 1
    page_size = 4096  # 4KB
    frame_list = [3, 5, 8]
    path_size = page_size * 10
    A = Process(pid, frame_list, path_size, page_size)


    pages = {
        'access': [7, 0, 1, 2, 0, 3, 0,4,2,3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1],
        'modify': [0] * 20
    }
    page_access = pages['access']
    page_modify = pages['modify']

    fifo_fun = fifo(A.frame_size)
    for pages in zip(page_access, page_modify):
        fault = process_page_step(A, pages, fifo_fun)
        # A.display_frame()
    # A.show_table()