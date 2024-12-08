import os
import time
from colorama import Fore, init, Back, Style
from tabulate import tabulate


# Function to clear a specified number of lines from the console
def clear_partial_lines(n):
    for _ in range(n):
        print("\033[F\033[K", end = "")  # Move cursor up and clear line


# Function to calculate the dividing line and the number of lines in a table
def cal_tabulate_lines(table):
    table_lines = table.splitlines()
    return table_lines[1], len(table_lines)  # Return the second line (divider) and total lines


# Function to display a fault table comparing different algorithms' page faults
def show_fault_table(alg_faults, length_pages):
    """
    Display the number of page faults and the page fault rate for each algorithm.
    :param alg_faults: Dictionary containing the number of page faults for each algorithm
    :param length_pages: Total number of pages accessed
    """
    algorithms = list(alg_faults.keys())
    headers = [''] + algorithms
    tables = [['Number of missing pages'], ['Page missing rate']]
    for fault in alg_faults.values():
        tables[0].append(str(fault))  # Append fault count
        tables[1].append(f"{fault / length_pages * 100:.2f}%")  # Calculate and append fault rate

    disp_tables = tabulate(tables, headers = headers, tablefmt = 'presto', stralign = 'center')
    del_line, _ = cal_tabulate_lines(disp_tables)
    title_texts = "The Performance of Algorithms".center(len(del_line))
    title_texts = Fore.CYAN + title_texts + Fore.RESET

    print('\n')
    print(del_line)
    print(title_texts)
    print(del_line)
    print(disp_tables)


# Function to display the page replacement simulation tables for all algorithms
def show_all_table(table: list, delay: int = 1):
    """
    Display the page replacement simulation for all algorithms step by step.
    :param table: A nested list containing page access sequences and tables for each algorithm
    :param delay: Time delay between each step
    """
    algorithms = ['OPT', 'FIFO', 'LRU', 'S_CLOCK', "E_CLOCK"]  # List of algorithms
    access_list = table[0]  # Sequence of page accesses
    table = table[1:]  # Remaining rows contain simulation tables for each algorithm

    for i in range(len(access_list)):
        j = i + 1
        # Extract partial tables for the current step
        tep_tables = [[row[:j] for row in alg_table] for alg_table in table]
        headers = access_list[:j]  # Use only headers up to the current step

        # Generate formatted tables for display
        disp_tables = [tabulate(tep_table, headers = headers, tablefmt = 'presto', stralign = 'center') for tep_table in tep_tables]

        del_line, table_line = cal_tabulate_lines(disp_tables[0])  # Get line details from first table
        total_line = 0  # Total lines to be cleared
        title_texts = [alg.center(len(del_line)) for alg in algorithms]
        title_texts = [Fore.CYAN + Style.BRIGHT + text + Style.NORMAL + Fore.RESET for text in title_texts]

        # Display each algorithm's table
        for k, algorithm in enumerate(algorithms):
            print(del_line)
            print(title_texts[k])
            print(del_line)
            print(disp_tables[k])
            total_line += table_line + 3  # Update the total lines to clear

        time.sleep(delay)
        # Clear previous outputs before showing the next step
        if i < len(access_list) - 1:
            clear_partial_lines(total_line)
