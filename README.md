# OS-PageSwapSim

Simulate and analyze OS page replacement algorithms with Python.

## Overview
```
📂
├── algorithms.py      # Contains page replacement algorithms like OPT, FIFO, LRU, etc.
├── main.py            # Entry point of the project; coordinates the simulation workflow.
├── process.py         # Handles the page access simulation and sequence generation.
├── quick_start.py     # Provides a quick start script with simple examples or tests.
├── README.md          
├── utils.py           # Utility functions for tasks like table formatting and statistics.
```



## Quick Start

```python
python quick_start.py
```

![](image/Gif1.gif)

![](image/Gif2.gif)

1. 编程实现OPT算法、FIFO算法、LRU算法、简单时钟算法和改进时钟算法;
2. 编程实现页面访问序列的随机化机制，包括设置每个页面的读写访问方式，以满足改进时钟算法的要求。
3. 在进程执行和访问每一页的过程中，每一次对一页的访问都应显示输出当时进程页表的内容(包括页号、物理块号、状态位、读写访问方法等字段)和当前页访问操作(如该页已经在内存中或触发缺页中断);
4. 所有算法都应该基于相同的条件，包括:
   系统采用“固定分配，局部替换”策略;<br>
   进程逻辑地址空间的大小相同;<br>
   分配给进程的物理块数目相同。<br>
   相同页面访问序列(整数序列，整数区间[0,N));<br>
5. 进行多次测试，统计分析和比较算法的性能(如缺页率，缺页次数)



**进程**：分配各自的页表和物理块 互相不知道 不能共享

**关键点：进程访问的页面与物理块是严格隔离的**

1. 每个进程只能使用分配给它的物理块。
2. 页表负责维护虚拟页面到物理块的映射，而页表是按进程独立的。
3. 如果某进程访问一个页面时，发现页面不在内存，缺页中断会触发替换逻辑，但只会使用本进程的物理块。

这样，多个进程可以在同一物理内存中运行，互不干扰，且共享内存资源时也安全。

**固定分配：**准备时候给每个进程分配的物理块固定 运行时数量固定 按照分配数量

**局部替换：**进程缺页时，进程独立 置换分配给自身的物理块
