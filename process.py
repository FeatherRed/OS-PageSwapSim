import time
import os
from tabulate import tabulate


class Process:
    def __init__(self, pid, frame_list, logic_size, page_size):
        self.pid = pid
        self.frame_list = frame_list
        self.frame_size = len(frame_list)
        self.logic_size = logic_size
        self.page_size = page_size
        self.total_pages = int(self.logic_size / self.page_size)

        self.page_table = self.__build_page_table()
        self.frame = [-1] * self.frame_size

        self.headers, self.table = self.__build_table()


    def __str__(self):
        return (f"Process {self.pid}:\n"
                f"  页大小: {self.page_size} 字节\n"
                f"  逻辑地址空间: {self.logic_size} 字节\n"
                f"  总页数: {self.total_pages}\n"
                f"  分配物理块数: {self.frame_size}\n"
                f"  物理块序号: {self.frame_list}")

    def __build_page_table(self):
        '''
        创建页表、初始化数据项
        :return:
        '''
        page_table = {}
        for page in range(self.total_pages):
            page_table[page] = {
                'frame': -1,  # 初始位 -1 表示页面不在内存
                'valid_bit': 0,  # 状态位 0 表示页面无效
                'access_bit': 0,  # 访问字段 0 表示未被访问
                'modify_bit': 0,  # 修改位 0 表示未被需改
                'swap_address': None  # 外存地址, 初始为None
            }
        return page_table

    def __build_table(self):
        header = ["Visit"]
        table = [["physical blocks-" + str(i)] for i in self.frame_list]
        table.append(["Page missing"]) # 添加缺页行
        return header, table


    def display_page_table(self):
        print(f"Page Table for Process {self.pid}:")
        print(f"{'Page':<6}{'Frame':<6}{'Valid':<6}{'Access':<6}{'Modify':<6}{'Swap Address':<12}")
        for page, data in self.page_table.items():
            # 使用 .get() 方法获取字典值，并提供默认值
            frame = data.get('frame', '-')
            valid_bit = data.get('valid_bit', '-')
            access_bit = data.get('access_bit', '-')
            modify_bit = data.get('modify_bit', '-')
            swap_address = data.get('swap_address', '-')

            # 防止 None 出现，确保每个字段都是字符串格式
            print(f"{page:<6}{frame if frame is not None else '-':<6}"
                  f"{valid_bit if valid_bit is not None else '-':<6}"
                  f"{access_bit if access_bit is not None else '-':<6}"
                  f"{modify_bit if modify_bit is not None else '-':<6}"
                  f"{swap_address if swap_address is not None else '-':<10}")

    def display_frame(self):
        print(self.frame)

    def update_table(self, page, out):
        self.headers.append(str(page))
        new_column = [i if i > -1 else "" for i in self.frame]
        new_column.append("√" if out else "")
        for i in range(len(self.table)):
            self.table[i].append(new_column[i])
        # self.__show_table()

    def show_table(self, delay = 0.6):
        for i in range(len(self.headers)):
            j = i + 1
            tep_table = [row[:j] for row in self.table]
            os.system('clear')
            print(tabulate(tep_table, headers = self.headers[:j], tablefmt = 'presto', stralign = "center"))
            time.sleep(delay)

if __name__ == '__main__':
    pid = 1
    page_size = 4096 # 4KB
    frame_list = [3, 5, 8]
    path_size = page_size * 10
    A = Process(pid, frame_list, path_size, page_size)
    A.display_page_table()