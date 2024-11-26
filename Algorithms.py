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
                farthest = -1
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
                del page_indices[lru_page]  # delete key
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


class BasicAlgorithm:
    """
    A base class for page replacement algorithms.

    Attributes:
        frame_size (int): The size of the frame (maximum number of pages that can be stored).
        frame (list): A list representing the current state of the frame.
    """

    def __init__(self, frame_size):
        """
        Initialize the base algorithm with a given frame size.

        Args:
            frame_size (int): The maximum size of the frame.
        """
        self.frame_size = frame_size
        self.frame = []  # Initialize an empty frame.

    def reset(self):
        """
        Reset the frame to an empty state.
        """
        self.frame = []

    def step(self, pages, page_index = None, page_list = None):
        """
        Perform a single step of the algorithm.
        Must be implemented by subclasses.

        Args:
            pages (tuple): A tuple containing the page to process and its read/write bit.
                - pages[0] (int): The page number being accessed.
                - pages[1] (int): The read/write bit (0 for read, 1 for write).
            page_index (int, optional): The current index in the reference string.
            page_list (list, optional): The sequence of future pages to be accessed.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("The 'step' method must be implemented by subclasses.")

    def update(self, pages, page_index):
        """
        Maintain and update the internal state of the frame after a page has been accessed.
        This method is designed to handle any necessary updates to class variables,
        such as tracking the order of pages or updating metadata related to the frame.

        Args:
            pages (tuple): A tuple containing the page and its read/write bit.
                - pages[0] (int): The page number being accessed.
                - pages[1] (int): The read/write bit (0 for read, 1 for write).
            page_index (int): The current index in the reference string, representing the
                              order of page access.
        """
        pass


class OPT(BasicAlgorithm):
    """
    Optimal Page Replacement Algorithm (OPT).
    Selects the page to replace by looking ahead in the reference string and
    replacing the page that will not be used for the longest period of time.
    """

    def __init__(self, frame_size):
        """
        Initialize the OPT algorithm with a given frame size.

        Args:
            frame_size (int): The maximum size of the frame.
        """
        super().__init__(frame_size)  # Initialize the base class.

    def step(self, pages, page_index = None, page_list = None):
        """
        Process a page access using the OPT algorithm.

        Args:
            pages (tuple): A tuple representing the page to access and its read/write status.
                - pages[0] (int): The page number being accessed.
                - pages[1] (int): The read/write bit (0 for read, 1 for write).
            page_index (int, optional): The current index in the reference string.
                Must be provided to track the order of page accesses.
            page_list (list, optional): The sequence of future pages to be accessed,
                required for predicting future page usage.

        Returns:
            tuple: (frame_id, old_page)
                - frame_id (int): The index in the frame where the page was added or replaced.
                - old_page (int or None): The page that was replaced, or None if no replacement occurred.

        Raises:
            ValueError: If either `page_list` or `page_index` is not provided.
        """
        if page_list is None or page_index is None:
            raise ValueError("Both 'page_list' and 'page_index' arguments are required for the OPT algorithm.")

        page = pages[0]  # Extract the page number to process.

        old_page = None
        if page in self.frame:
            # Page is already in the frame; no replacement needed.
            frame_id = self.frame.index(page)
        elif len(self.frame) < self.frame_size:
            # Frame is not full; add the page directly.
            self.frame.append(page)
            frame_id = len(self.frame) - 1
        else:
            # Frame is full; find the page to replace.
            farthest_index = -1  # Track the farthest page's future index.
            frame_id = -1  # Track the frame index to replace.

            for j, current_page in enumerate(self.frame):
                try:
                    # Determine the next use of the current page.
                    next_use = page_list[page_index + 1:].index(current_page)
                except ValueError:
                    # If the page is not in the remaining sequence, it will not be used again.
                    next_use = float('inf')

                # Update the farthest page to replace.
                if next_use > farthest_index:
                    farthest_index = next_use
                    frame_id = j

            # Replace the selected page.
            old_page = self.frame[frame_id]
            self.frame[frame_id] = page

        return frame_id, old_page


class FIFO(BasicAlgorithm):
    """
    First-In-First-Out (FIFO) page replacement algorithm.
    Replaces the oldest page in the frame, following a cyclic order.
    """

    def __init__(self, frame_size):
        """
        Initialize the FIFO algorithm with a given frame size.

        Args:
            frame_size (int): The maximum size of the frame.
        """
        super().__init__(frame_size)  # Initialize the base class.
        self.pointer = 0  # Initialize the pointer for tracking the next replacement position.

    def reset(self):
        """
        Reset the frame and pointer to their initial states.
        """
        super().reset()  # Reset the frame using the base class method.
        self.pointer = 0  # Reset the pointer to the start of the frame.

    def step(self, pages, page_index = None, page_list = None):
        """
        Process a page access using the FIFO algorithm.

        Args:
            pages (tuple): A tuple representing the page to access and its read/write status.
                - pages[0] (int): The page number being accessed.
                - pages[1] (int): The read/write bit (0 for read, 1 for write).
            page_index (int, optional): Not used in this algorithm but included for consistency.
            page_list (list, optional): Not used in this algorithm but included for consistency.

        Returns:
            tuple: (frame_id, old_page)
                - frame_id (int): The index in the frame where the page was added or replaced.
                - old_page (int or None): The page that was replaced, or None if no replacement occurred.
        """
        old_page = None
        page = pages[0]  # Extract the page number to process.

        if len(self.frame) < self.frame_size:
            # Frame is not full; append the page.
            self.frame.append(page)
            frame_id = len(self.frame) - 1
        else:
            # Frame is full; replace the page at the current pointer position.
            old_page = self.frame[self.pointer]
            self.frame[self.pointer] = page
            frame_id = self.pointer
            # Update the pointer to the next position in a cyclic manner.
            self.pointer = (self.pointer + 1) % self.frame_size

        return frame_id, old_page


class LRU(BasicAlgorithm):
    """
    Least Recently Used (LRU) Page Replacement Algorithm.
    Replaces the page that has been used least recently.
    """

    def __init__(self, frame_size):
        """
        Initialize the LRU algorithm with a given frame size.

        Args:
            frame_size (int): The maximum size of the frame.
        """
        super().__init__(frame_size)
        self.page_indices = {}  # Tracks the last access index of pages.

    def reset(self):
        """
        Reset the frame and page indices to their initial states.
        """
        super().reset()  # Reset the frame using the base class method.
        self.page_indices = {}  # Clear the page access tracking dictionary.

    def step(self, pages, page_index = None, page_list = None):
        """
        Process a page using the LRU algorithm.

        Args:
            pages (tuple): A tuple representing the page to access and its read/write status.
                - pages[0] (int): The page number being accessed.
                - pages[1] (int): The read/write bit (0 for read, 1 for write).
            page_index (int, optional): The current index in the reference string.
            page_list (list, optional): Not used in LRU but included for consistency with other algorithms.

        Returns:
            tuple: (frame_id, old_page)
                - frame_id (int): The index in the frame where the page was added or replaced.
                - old_page (int or None): The page that was replaced, or None if no replacement occurred.

        Raises:
            ValueError: If `page_index` is not provided.
        """
        if page_index is None:
            raise ValueError("The 'page_index' argument is required for the LRU algorithm.")

        page = pages[0]  # Extract the page number to process.
        old_page = None

        if len(self.frame) < self.frame_size:
            # Frame is not full; add the page.
            self.frame.append(page)
            frame_id = len(self.frame) - 1
        else:
            # Frame is full; replace the least recently used page.
            lru_page = min(self.page_indices, key = self.page_indices.get)  # Identify LRU page.
            frame_id = self.page_indices[lru_page] % self.frame_size  # Find its index in the frame.
            old_page = self.frame[frame_id]

            # Replace the least recently used page.
            self.frame[frame_id] = page
            del self.page_indices[lru_page]  # Remove the LRU page from tracking.

        return frame_id, old_page

    def update(self, pages, page_index):
        """
        Update the access tracking for the current page.

        Args:
            pages (tuple): A tuple containing the page and its read/write bit.
                - pages[0] (int): The page number being accessed.
                - pages[1] (int): The read/write bit (0 for read, 1 for write).
            page_index (int): The current index in the reference string.

        Notes:
            This method updates the `page_indices` dictionary to reflect the
            most recent access of the page.
        """
        page = pages[0]  # Extract the page number.
        self.page_indices[page] = page_index  # Update its access index.


class S_CLOCK(BasicAlgorithm):
    """
    Second Chance (CLOCK) Page Replacement Algorithm.
    This algorithm uses a "use bit" to give pages a second chance before replacement,
    simulating a circular queue structure.
    """

    def __init__(self, frame_size):
        """
        Initialize the CLOCK algorithm with a given frame size.

        Args:
            frame_size (int): The maximum size of the frame.
        """
        super(S_CLOCK, self).__init__(frame_size)
        self.use_bit = [0] * self.frame_size  # Initialize use bits for all frame slots.
        self.pointer = 0  # Pointer to the current position in the circular frame.

    def reset(self):
        """
        Reset the frame, use bits, and pointer to their initial states.
        """
        super(S_CLOCK, self).reset()
        self.use_bit = [0] * self.frame_size  # Reset all use bits to 0.
        self.pointer = 0  # Reset the pointer to the start of the frame.

    def step(self, pages, page_index = None, page_list = None):
        """
        Process a page using the CLOCK algorithm.

        Args:
            pages (tuple): A tuple representing the page to access and its read/write status.
                - pages[0] (int): The page number being accessed.
                - pages[1] (int): The read/write bit (0 for read, 1 for write).
            page_index (int, optional): The current index in the reference string.
            page_list (list, optional): Not used in CLOCK but included for consistency.

        Returns:
            tuple: (frame_id, old_page)
                - frame_id (int): The index in the frame where the page was added or replaced.
                - old_page (int or None): The page that was replaced, or None if no replacement occurred.
        """
        old_page = None
        page = pages[0]  # Extract the page number to process.

        if len(self.frame) < self.frame_size:
            # Frame is not full; add the page to the frame.
            self.frame.append(page)
            frame_id = len(self.frame) - 1
            self.use_bit[frame_id] = 1  # Set the use bit for the new page.
        else:
            # Frame is full; find a page to replace using the CLOCK algorithm.
            while self.use_bit[self.pointer] == 1:
                # Skip pages with use bit set and reset their use bit to 0.
                self.use_bit[self.pointer] = 0
                self.pointer = (self.pointer + 1) % self.frame_size

            # Replace the page at the pointer position.
            old_page = self.frame[self.pointer]
            frame_id = self.pointer
            self.frame[self.pointer] = page
            self.use_bit[self.pointer] = 1  # Set the use bit for the new page.
            self.pointer = (self.pointer + 1) % self.frame_size  # Move the pointer forward.

        return frame_id, old_page

    def update(self, pages, page_index):
        """
        Update the use bit for a page that has been accessed.

        Args:
            pages (tuple): A tuple containing the page and its read/write bit.
                - pages[0] (int): The page number being accessed.
                - pages[1] (int): The read/write bit (0 for read, 1 for write).
            page_index (int): The current index in the reference string.

        Notes:
            This method sets the use bit to 1 for the accessed page if it exists in the frame.
        """
        page = pages[0]  # Extract the page number.
        self.use_bit[self.frame.index(page)] = 1


class E_CLOCK(BasicAlgorithm):
    """
    Enhanced CLOCK (E-CLOCK) Page Replacement Algorithm.
    This algorithm extends the basic CLOCK algorithm by introducing a "modify bit",
    allowing it to prioritize pages for replacement based on both usage and modification status.
    """

    def __init__(self, frame_size):
        """
        Initialize the E-CLOCK algorithm with a given frame size.

        Args:
            frame_size (int): The maximum size of the frame.
        """
        super(E_CLOCK, self).__init__(frame_size)
        self.use_bit = [0] * self.frame_size  # Tracks if a page has been accessed recently.
        self.modify_bit = [0] * self.frame_size  # Tracks if a page has been modified (write access).
        self.pointer = 0  # Pointer to the current position in the circular frame.

    def reset(self):
        """
        Reset the frame, use bits, modify bits, and pointer to their initial states.
        """
        super(E_CLOCK, self).reset()
        self.use_bit = [0] * self.frame_size  # Reset all use bits to 0.
        self.modify_bit = [0] * self.frame_size  # Reset all modify bits to 0.
        self.pointer = 0  # Reset the pointer to the start of the frame.

    def step(self, pages, page_index = None, page_list = None):
        """
        Process a page using the E-CLOCK algorithm.

        Args:
            pages (tuple): A tuple containing:
                - pages[0] (int): The page number being accessed.
                - pages[1] (int): The read/write bit (0 for read, 1 for write).
            page_index (int, optional): The current index in the reference string.
            page_list (list, optional): Not used in E-CLOCK but included for consistency.

        Returns:
            tuple: (frame_id, old_page)
                - frame_id (int): The index in the frame where the page was added or replaced.
                - old_page (int or None): The page that was replaced, or None if no replacement occurred.

        Algorithm Description:
            - The algorithm prioritizes page replacement based on the use bit (U) and modify bit (M):
                1. (U=0, M=0): Least recently used and not modified (highest priority).
                2. (U=0, M=1): Least recently used but modified.
                3. (U=1, M=0): Recently used and not modified.
                4. (U=1, M=1): Recently used and modified (lowest priority).
            - If no (U=0, M=0) pages are found, the pointer moves while resetting use bits as needed.

        Raises:
            ValueError: If `page_index` is required but not provided.
        """
        old_page = None
        page, rw = pages  # Extract the page number and read/write bit.

        if len(self.frame) < self.frame_size:
            # Frame is not full; add the page to the frame.
            self.frame.append(page)
            frame_id = len(self.frame) - 1
        else:
            # Frame is full; find a page to replace using (U, M) priority.
            found_00 = -1
            found_01 = -1
            found_10 = -1
            found_11 = -1
            time_pointer = self.pointer

            # Scan the frame for a page to replace.
            for _ in range(self.frame_size):
                if (self.use_bit[time_pointer], self.modify_bit[time_pointer]) == (0, 0):
                    found_00 = time_pointer if found_00 == -1 else found_00
                elif (self.use_bit[time_pointer], self.modify_bit[time_pointer]) == (0, 1):
                    found_01 = time_pointer if found_01 == -1 else found_01
                elif (self.use_bit[time_pointer], self.modify_bit[time_pointer]) == (1, 0):
                    found_10 = time_pointer if found_10 == -1 else found_10
                elif (self.use_bit[time_pointer], self.modify_bit[time_pointer]) == (1, 1):
                    found_11 = time_pointer if found_11 == -1 else found_11
                time_pointer = (time_pointer + 1) % self.frame_size

            # Select a page to replace based on priority.
            if found_00 > -1:
                # Case 1: Replace (U=0, M=0) page (highest priority).
                self.pointer = found_00
            elif found_01 > -1:
                # Case 2: Replace (U=0, M=1) page.
                # Reset the use bits while moving the pointer to the target page.
                while self.pointer != found_01:
                    self.use_bit[self.pointer] = 0
                    self.pointer = (self.pointer + 1) % self.frame_size
            else:
                # Case 3: No (U=0) pages found.
                # Reset all use bits to allow consideration of (U=1) pages.
                self.use_bit = [0] * self.frame_size
                # Replace (U=1, M=0) page if found, otherwise replace (U=1, M=1).
                self.pointer = found_10 if found_10 > -1 else found_11

            # Replace the selected page.
            old_page = self.frame[self.pointer]
            frame_id = self.pointer
            self.frame[self.pointer] = page
            self.use_bit[self.pointer] = 1  # Set use bit for the new page.
            self.modify_bit[self.pointer] = rw  # Set modify bit based on the access type.
            self.pointer = (self.pointer + 1) % self.frame_size  # Move the pointer forward.

        return frame_id, old_page

    def update(self, pages, page_index):
        """
        Update the use and modify bits for a page that has been accessed.

        Args:
            pages (tuple): A tuple containing:
                - pages[0] (int): The page number being accessed.
                - pages[1] (int): The read/write bit (0 for read, 1 for write).
            page_index (int): The current index in the reference string.

        Notes:
            - Sets the use bit to 1 for the accessed page.
            - Updates the modify bit based on the access type (read/write).
        """
        page, rw = pages  # Extract the page number and read/write bit.
        index = self.frame.index(page)
        self.use_bit[index] = 1  # Set use bit for the accessed page.
        self.modify_bit[index] = rw  # Update modify bit based on access type.


# todo 可以把要修改的页面加flag 这样可以用在clock上面
if __name__ == '__main__':
    pages = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    fifo_pages = [1, 2, 3, 4, 2, 1, 5, 6, 2, 1, 2, 3, 7, 6, 3, 2, 1, 2, 3, 6]
    lru_pages = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    clock_pages = [1, 3, 4, 2, 5, 4, 7, 4]
    main_num = 4

    page_range = 80
    num_pages = 300

    rand_pages = [random.randint(0, page_range - 1) for _ in range(num_pages)]
    # T0 = time.perf_counter()

    enhanced_clock_pages = [0, 1, 3, 6, 2, 4, 5, 2, 5, 0, 3, 1, 2, 5, 4, 1, 0]
    enhanced_clock_pages_rw = [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0]

    print(simple_clock(enhanced_clock_pages, main_num))
    # T1 = time.perf_counter()
    # print((T1 - T0) * 1000)
