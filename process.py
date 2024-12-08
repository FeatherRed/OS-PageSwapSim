import time
import os
from tabulate import tabulate
from utils import *
from colorama import Fore, init, Back, Style


class Process:
    def __init__(self, pid, frame_list, logic_size, page_size, access_window = 3):
        self.pid = pid
        self.frame_list = frame_list
        self.frame_size = len(frame_list)
        self.logic_size = logic_size
        self.page_size = page_size
        self.total_pages = int(self.logic_size / self.page_size)

        self.access_window = access_window
        self.access_history = []

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
        header = ["Page", "Frame", "Status Bit(P)", "Access Field(A)", "Modified Bit(M)", "Swap Address"]
        page_table = []
        for page in range(self.total_pages):
            page_table.append([str(page), -1, 0, 0, -1, "-"])
        return page_table

    def __build_table(self):
        header = ["Visit"]
        table = [["physical blocks-" + str(i)] for i in self.frame_list]
        table.append(["Page missing"])  # 添加缺页行
        return header, table

    def __update_access_history(self, page):
        self.access_history.append(page)
        if len(self.access_history) > self.access_window:
            removed_page = self.access_history.pop(0)
            self.page_table[removed_page][3] -= 1
        self.page_table[page][3] += 1

    def reset(self):
        self.access_history = []

        self.page_table = self.__build_page_table()
        self.frame = [-1] * self.frame_size

        self.headers, self.table = self.__build_table()

    def welcome(self, algoirthm_name):
        del_line = "---------------------------------------------------------------------------------------------"
        welcome_text = f"PID {self.pid} Use {algoirthm_name}"
        welcome_text = welcome_text.center(len(del_line))
        welcome_text = Back.WHITE + Fore.BLACK + welcome_text + Fore.RESET + Back.RESET
        print(del_line)
        print(welcome_text)

    def display_page_table(self, pages, flag = 0):
        page, rw = pages
        header = [Fore.RED + "Page", "Frame", "Status Bit(P)", "Access Field(A)", "Modified Bit(M)",
                  "Swap Address" + Fore.RESET]
        page_table = self.page_table

        table = tabulate(page_table, headers = header, tablefmt = 'presto', stralign = 'center', numalign = 'center', colalign = 'center')
        del_line, lines = cal_tabulate_lines(table)
        summary_text = f"Process PID: {self.pid} accessed page {page}"
        summary_text += " for reading and writing" if rw else " for reading"
        if flag:
            summary_text += f", page {page} was in memory, direct access"
        else:
            summary_text += f", page {page} was not in memory, a page fault occurred"
        summary_text = summary_text.center(len(del_line))
        summary_text = Fore.WHITE + summary_text + Fore.RESET
        print(del_line)
        print(table)
        print(del_line)
        print(summary_text)
        time.sleep(0.3)
        # 清
        clear_partial_lines(lines + 3)

    def display_frame(self):
        print(self.frame)

    def update_page_table(self, pages, frame_id, old_page):
        page, rw = pages

        if old_page is not None:
            self.page_table[old_page][0] = str(old_page)
            self.page_table[old_page][1] = -1
            self.page_table[old_page][2] = 0
            self.page_table[old_page][4] = -1
            self.page_table[old_page][-1] = str('-')

            self.table[frame_id][-1] = Fore.GREEN + self.table[frame_id][-1] + Fore.RESET

        self.page_table[page][0] = Fore.GREEN + self.page_table[page][0]
        self.page_table[page][1] = self.frame_list[frame_id]
        self.page_table[page][2] = 1
        self.page_table[page][4] = rw
        self.page_table[page][-1] = self.page_table[page][-1] + Fore.RESET
        self.__update_access_history(page)

    def update_table(self, pages, out):
        page, rw = pages
        self.headers.append(Fore.RED + str(page) + Fore.RESET if rw else Fore.BLUE + str(page) + Fore.RESET)
        new_column = [str(i) if i > -1 else "" for i in self.frame]
        new_column.append("√" if out else "")
        for i in range(len(self.table)):
            self.table[i].append(new_column[i])
        # self.__show_table()

    def show_page_table(self, algorithm_name):
        header = [Fore.RED + "Page", "Frame", "Status Bit(P)", "Access Field(A)", "Modified Bit(M)",
                  "Swap Address" + Fore.RESET]
        page_table = self.page_table

        table = tabulate(page_table, headers = header, tablefmt = 'presto')

        del_line, _ = cal_tabulate_lines(table)
        title_text = f"{algorithm_name} Page table"
        title_text = title_text.center(len(del_line))
        title_text = Fore.CYAN + Style.BRIGHT + title_text + Style.NORMAL + Fore.RESET
        print(del_line)
        print(title_text)
        print(del_line)
        print(table)

    def show_table(self, algorithm_name, delay = 1):
        for i in range(len(self.headers)):
            j = i + 1
            tep_table = [row[:j] for row in self.table]
            headers = self.headers[:j]

            disp_table = tabulate(tep_table, headers = headers, tablefmt = 'presto', stralign = "center")

            del_line, table_line = cal_tabulate_lines(disp_table)
            title_text = f'{algorithm_name} Frame Table'
            title_text = title_text.center(len(del_line))
            title_text = Fore.CYAN + Style.BRIGHT + title_text + Style.NORMAL + Fore.RESET
            table_line += 3
            print(del_line)
            print(title_text)
            print(del_line)
            print(disp_table)
            time.sleep(delay)
            if i < len(self.headers) - 1:
                clear_partial_lines(table_line)


if __name__ == '__main__':
    pid = 1
    page_size = 4096  # 4KB
    frame_list = [3, 5, 8]
    path_size = page_size * 10
    A = Process(pid, frame_list, path_size, page_size)
    A.display_page_table()
