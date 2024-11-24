import os
import time
import numpy as np
import random


# OPT
def opt(pages, frame_size):
    frame = []
    page_faults = 0
    for i in range(len(pages)):
        if pages[i] not in frame:
            if len(frame) < frame_size:
                frame.append(pages[i])
            else:
                farthest = i
                index_to_replace = -1
                for j in range(len(frame)):
                    try:
                        next_use = pages[i + 1:].index(frame[j])
                    except ValueError:
                        next_use = float('inf')

                    if next_use > farthest:
                        farthest = next_use
                        index_to_replace = j

                frame[index_to_replace] = pages[i]

            page_faults += 1
        # in frame
        # Get it
    return page_faults


def fifo(pages, frame_size):
    frame = []
    page_faults = 0
    index = 0

    for page in pages:
        if page not in frame:
            if len(frame) < frame_size:
                frame.append(page)
            else:
                # frame[index] replace
                frame[index] = page
                index = (index + 1) % frame_size
            page_faults += 1

    return page_faults

def fifo_process(process, pages):
    frame = []
    page_faults = 0
    index = 0

    pages_access = pages['access']
    pages_modify = pages['modify']

    for page, rw in zip(pages_access, pages_modify):
        if process.page_table[page]['valid_bit'] == 0:
            if len(frame) < process.frame_size:
                frame.append(page)
                frame_id = process.frame_id[len(frame) - 1]
                process.frame_to_page_table[frame_id] = page
            else:
                old_page = frame[index]
                frame[index] = page
                frame_id = process.frame_id[index]
                process.frame_to_page_table[frame_id] = page
                index = (index + 1) % process.frame_size

                process.page_table[old_page]['frame_id'] = -1
                process.page_table[old_page]['valid_bit'] = 0
                process.page_table[old_page]['access_bit'] = 0


                pass
            # 页面 加入
            page_faults += 1
            process.page_table[page]['frame_id'] = frame_id
            process.page_table[page]['valid_bit'] = 1
            process.page_table[page]['access_bit'] = 1
            process.page_table[page]['modify_bit'] = rw



def lru(pages, frame_size):
    frame = []
    page_faults = 0
    page_indices = {}

    for i, page in enumerate(pages):
        if page not in frame:
            if len(frame) < frame_size:
                frame.append(page)
            else:
                lru_page = min(page_indices, key = page_indices.get)
                page_index = page_indices[lru_page] % frame_size
                frame[page_index] = page
                del page_indices[lru_page] # delete key
            page_faults += 1
        page_indices[page] = i

    return page_faults

def simple_clock(pages, frame_size):
    # clock
    frame = [-1] * frame_size
    use_bit = [0] * frame_size
    page_faults = 0
    pointer = 0

    for page in pages:
        if page not in frame:
            while use_bit[pointer] == 1:
                use_bit[pointer] = 0
                pointer = (pointer + 1) % frame_size

            frame[pointer] = page
            use_bit[pointer] = 1
            pointer = (pointer + 1) % frame_size
            page_faults += 1
        else:
            use_bit[frame.index(page)] = 1

    return page_faults

def enhanced_clock(pages, frame_size, pages_rw):
    # enhanced clock
    # (0, 0) -----> (0, 1) -----> (1, 0) -----> (1, 1)
    frame = [-1] * frame_size
    use_bit = [0] * frame_size
    modify_bit = [0] * frame_size
    page_faults = 0
    pointer = 0

    for i, page in enumerate(pages):
        if page not in frame:
            # 扫描一遍，寻找00, 01, 10, 11的页面
            found_00 = -1
            found_01 = -1
            found_10 = -1
            found_11 = -1
            time_pointer = pointer
            for _ in range(frame_size):
                if use_bit[time_pointer] == 0 and modify_bit[time_pointer] == 0:
                    found_00 = time_pointer if found_00 == -1 else found_00
                if use_bit[time_pointer] == 0 and modify_bit[time_pointer] == 1:
                    found_01 = time_pointer if found_01 == -1 else found_01
                if use_bit[time_pointer] == 1 and modify_bit[time_pointer] == 0:
                    found_10 = time_pointer if found_10 == -1 else found_10
                if use_bit[time_pointer] == 1 and modify_bit[time_pointer] == 1:
                    found_11 = time_pointer if found_11 == -1 else found_11
                time_pointer = (time_pointer + 1) % frame_size

            if found_00 > -1:
                pointer = found_00
            elif found_01 > -1:
                while pointer != found_01:
                    use_bit[pointer] = 0
                    pointer = (pointer + 1) % frame_size
            elif found_10 > -1:
                pointer = found_10
                use_bit = [0] * frame_size
            elif found_11 > -1:
                pointer = found_11
                use_bit = [0] * frame_size

            # 替换页面
            frame[pointer] = page
            use_bit[pointer] = 1
            modify_bit[pointer] = pages_rw[i]  # 根据读写参数设置修改位
            pointer = (pointer + 1) % frame_size
            page_faults += 1
        else:
            index = frame.index(page)
            use_bit[index] = 1
            modify_bit[index] = pages_rw[i]  # 更新修改位

    return page_faults

# todo 可以把要修改的页面加flag 这样可以用在clock上面
if __name__ == '__main__':
    pages = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    fifo_pages = [1, 2, 3, 4, 2, 1, 5, 6, 2, 1, 2, 3, 7, 6, 3, 2, 1, 2, 3, 6]
    lru_pages = [1,2,3,4,1,2,5,1,2,3,4,5]
    clock_pages = [1, 3, 4, 2, 5, 4, 7, 4]
    main_num = 4

    page_range = 80
    num_pages = 300


    rand_pages = [random.randint(0, page_range - 1) for _ in range(num_pages)]
    # T0 = time.perf_counter()

    enhanced_clock_pages = [0, 1, 3, 6, 2, 4, 5, 2, 5, 0, 3, 1, 2, 5, 4, 1, 0]
    enhanced_clock_pages_rw = [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0]


    print(enhanced_clock(enhanced_clock_pages, main_num, enhanced_clock_pages_rw))
    # T1 = time.perf_counter()
    # print((T1 - T0) * 1000)
