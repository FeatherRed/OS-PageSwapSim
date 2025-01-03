import time
import os
from tabulate import tabulate
from utils import *
from colorama import Fore, init, Back, Style


class Process:
    def __init__(self, pid, frame_list, logic_size, page_size, access_window = 3):
        """
        Initializes a Process instance.

        :param pid: Process ID
        :param frame_list: List of physical frames allocated to the process
        :param logic_size: Logical address space size in bytes
        :param page_size: Page size in bytes
        :param access_window: Size of the access history window for tracking recent accesses
        """
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
        """
        String representation of the Process instance.

        :return: Process details as a string
        """
        return (f"Process {self.pid}:\n"
                f"  页大小: {self.page_size} 字节\n"
                f"  逻辑地址空间: {self.logic_size} 字节\n"
                f"  总页数: {self.total_pages}\n"
                f"  分配物理块数: {self.frame_size}\n"
                f"  物理块序号: {self.frame_list}")

    def __build_page_table(self):
        """
        Creates and initializes the page table with default values.

        :return: Initialized page table
        """
        header = ["Page", "Frame", "Status Bit(P)", "Access Field(A)", "Modified Bit(M)", "Swap Address"]
        page_table = []
        for page in range(self.total_pages):
            page_table.append([str(page), -1, 0, 0, -1, "-"])
        return page_table

    def __build_table(self):
        """
        Initializes the table structure for tracking frame usage.

        :return: Table headers and table content
        """
        header = ["Visit"]
        table = [["physical blocks-" + str(i)] for i in self.frame_list]
        table.append(["Page missing"])  # Adds a row for page faults
        return header, table

    def __update_access_history(self, page):
        """
        Updates the access history for a page and adjusts the access field.

        :param page: Page number to update
        """
        self.access_history.append(page)
        if len(self.access_history) > self.access_window:
            removed_page = self.access_history.pop(0)
            self.page_table[removed_page][3] -= 1
        self.page_table[page][3] += 1

    def reset(self):
        """
        Resets the process to its initial state.
        """
        self.access_history = []

        self.page_table = self.__build_page_table()
        self.frame = [-1] * self.frame_size

        self.headers, self.table = self.__build_table()

    def welcome(self, algoirthm_name):
        """
        Displays a welcome message for the selected algorithm.

        :param algoirthm_name: Name of the algorithm being used
        """
        del_line = "---------------------------------------------------------------------------------------------"
        welcome_text = f"PID {self.pid} Use {algoirthm_name}"
        welcome_text = welcome_text.center(len(del_line))
        welcome_text = Back.WHITE + Fore.BLACK + welcome_text + Fore.RESET + Back.RESET
        print(del_line)
        print(welcome_text)

    def display_page_table(self, pages, flag = 0, delay = 0.5):
        """
        Displays the page table with the current status.

        :param pages: Tuple containing page number and read/write flag
        :param flag: Indicates whether the page is in memory
        :param delay: Time delay for displaying the page table
        """
        page, rw = pages
        header = [Fore.RED + "Page", "Frame", "Status Bit(P)", "Access Field(A)", "Modified Bit(M)", "Swap Address" + Fore.RESET]
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
        time.sleep(delay)
        # Clear partial lines
        clear_partial_lines(lines + 3)

    def display_frame(self):
        """
        Displays the current frame contents.
        """
        print(self.frame)

    def update_page_table(self, pages, frame_id, old_page):
        """
        Updates the page table based on the current operation.

        :param pages: Tuple containing page number and read/write flag
        :param frame_id: Frame index being updated
        :param old_page: Page being replaced in memory
        """
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
        """
        Updates the frame table for display.

        :param pages: Tuple containing page number and read/write flag
        :param out: Indicates if a page fault occurred
        """
        page, rw = pages
        self.headers.append(Fore.RED + str(page) + Fore.RESET if rw else Fore.BLUE + str(page) + Fore.RESET)
        new_column = [str(i) if i > -1 else "" for i in self.frame]
        new_column.append("√" if out else "")
        for i in range(len(self.table)):
            self.table[i].append(new_column[i])

    def show_page_table(self, algorithm_name):
        """
        Displays the current page table with the specified algorithm name.

        :param algorithm_name: Name of the algorithm used
        """
        header = [Fore.RED + "Page", "Frame", "Status Bit(P)", "Access Field(A)", "Modified Bit(M)", "Swap Address" + Fore.RESET]
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
        """
        Displays the frame usage table.

        :param algorithm_name: Name of the algorithm used
        :param delay: Delay between updates
        """
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
