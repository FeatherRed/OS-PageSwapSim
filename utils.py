import os
import time


def clear_partial_lines(n):
    for _ in range(n):
        print("\033[F\033[K", end = "")


def cal_tabulate_lines(table):
    table_lines = table.splitlines()
    return table_lines[1], len(table_lines)
