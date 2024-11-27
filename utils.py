import os
import time
from colorama import Fore, init, Back, Style
from tabulate import tabulate
def clear_partial_lines(n):
    for _ in range(n):
        print("\033[F\033[K", end = "")


def cal_tabulate_lines(table):
    table_lines = table.splitlines()
    return table_lines[1], len(table_lines)


def show_all_table(table: list, delay: int = 1):
    algorithms = ['OPT', 'FIFO', 'LRU', 'S_CLOCK', "E_CLOCK"]
    access_list = table[0]
    table = table[1:]
    for i in range(len(access_list)):
        j = i + 1
        tep_tables = [[row[:j] for row in alg_table] for alg_table in table]
        headers = access_list[:j]

        disp_tables = [tabulate(tep_tables[0], headers = headers, tablefmt = 'presto', stralign = 'center')]

        for k in range(1, 5):
            disp_tables.append(tabulate(tep_tables[k], tablefmt = 'presto', stralign = 'center'))
        # disp_tables = [tabulate(tep_table, headers = headers, tablefmt = 'presto', stralign = 'center') for tep_table in tep_tables]

        del_line, table_line = cal_tabulate_lines(disp_tables[0])
        table_line -= 2
        total_line = 1 # todo
        title_texts = algorithms
        title_texts = [title_text.center(len(del_line)) for title_text in title_texts]
        title_texts = [Fore.CYAN + Style.BRIGHT + title_text + Style.NORMAL + Fore.RESET for title_text in title_texts]

        # 开始输出
        for k, algorithm in enumerate(algorithms):
            print(del_line)
            print(title_texts[k])
            print(del_line)
            print(disp_tables[k])
            total_line = total_line + table_line + 3

        time.sleep(delay)
        if i < len(access_list) - 1:
            clear_partial_lines(total_line)

