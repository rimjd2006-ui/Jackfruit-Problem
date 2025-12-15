import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time
import threading

# ================= Maze Solver Algorithm ==================
def bfs_solver_steps(maze, start, end):
    """
    Generator-based BFS solver that yields (current_path, current_step)
    for each action, so visualization can sync with pseudocode.
    """
    rows, cols = maze.shape
    visited = np.zeros_like(maze)
    queue = [(start, [start])]

    # Step mapping
    INIT_QUEUE = 0
    WHILE_QUEUE = 1
    POP_NODE = 2
    MARK_VISITED = 3
    CHECK_END = 4
    ADD_NEIGHBORS = 5

    yield [], INIT_QUEUE  # Initialize queue

    while queue:
        yield [], WHILE_QUEUE  # Start of while loop

        (r, c), path = queue.pop(0)
        yield [], POP_NODE  # Pop node

        if visited[r, c]:
            continue

        visited[r, c] = 1
        yield path, MARK_VISITED  # Mark visited

        if (r, c) == end:
            yield path, CHECK_END  # End found
            return

        # Add neighbors
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr, nc] == 0 and not visited[nr, nc]:
                queue.append(((nr, nc), path + [(nr, nc)]))
        yield path, ADD_NEIGHBORS  # Neighbors added

# ================= Maze Visualizer ==================
class MazeVisualizer:
    def __init__(self, root, maze):
        self.root = root
        self.maze = maze
        self.running = False
        self.paused = False

        self.start = (0, 0)
        self.end = (maze.shape[0]-1, maze.shape[1]-1)

        # Pseudocode steps
        self.algorithm_steps = [
            "1. Initialize queue with start node",
            "2. While queue is not empty:",
            "3. Pop node from queue",
            "4. Mark node as visited",
            "5. If node is end, stop",
            "6. Add unvisited neighbors to queue"
        ]

        # Set up matplotlib figure
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=6)

        # Control buttons
        self.start_btn = ttk.Button(root, text="Start", command=self.start_visualization)
        self.start_btn.grid(row=0, column=1, sticky='ew')
        self.pause_btn = ttk.Button(root, text="Pause", command=self.pause_visualization)
        self.pause_btn.grid(row=1, column=1, sticky='ew')
        self.stop_btn = ttk.Button(root, text="Stop", command=self.stop_visualization)
        self.stop_btn.grid(row=2, column=1, sticky='ew')

        # Text area for pseudocode
        self.text = tk.Text(root, height=15, width=40)
        self.text.grid(row=3, column=1, rowspan=3)
        self.text.tag_configure("highlight", background="yellow")

        self.draw_maze()

    def draw_maze(self, path=[]):
        self.ax.clear()
        self.ax.imshow(self.maze, cmap='gray_r')
        if path:
            y, x = zip(*path)
            self.ax.plot(x, y, color='red', linewidth=2)
        self.canvas.draw()

    def start_visualization(self):
        if self.running:
            return
        self.running = True
        self.paused = False
        self.text.delete(1.0, tk.END)
        for line in self.algorithm_steps:
            self.text.insert(tk.END, line + "\n")

        threading.Thread(target=self.visualize_steps).start()

    def pause_visualization(self):
        self.paused = not self.paused

    def stop_visualization(self):
        self.running = False
        self.paused = False

    def highlight_step(self, step_num):
        self.text.tag_remove("highlight", "1.0", tk.END)
        line_start = f"{step_num+1}.0"
        line_end = f"{step_num+1}.end"
        self.text.tag_add("highlight", line_start, line_end)

    def visualize_steps(self):
        generator = bfs_solver_steps(self.maze, self.start, self.end)
        for path, step in generator:
            if not self.running:
                break
            while self.paused:
                time.sleep(0.1)
            self.draw_maze(path)
            self.highlight_step(step)
            time.sleep(0.3)
        self.running = False

# ================= Main ==================
if __name__ == "__main__":
    maze = np.zeros((10, 10))
    maze[1, 2:9] = 1
    maze[2:7, 5] = 1
    maze[7, 1:7] = 1
    maze[5, 7:9] = 1

    root = tk.Tk()
    root.title("Maze Solver Visualizer")
    app = MazeVisualizer(root, maze)
    root.mainloop()



