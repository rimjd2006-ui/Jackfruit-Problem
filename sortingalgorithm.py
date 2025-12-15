import tkinter as tk
from tkinter import ttk
import random
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------- Sorting Algorithms ---------------- #

def bubble_sort(arr, ascending=True):
    n = len(arr)
    for i in range(n):
        yield arr, (), 0
        for j in range(n - i - 1):
            yield arr, (j, j+1), 1
            if (arr[j] > arr[j+1] and ascending) or (arr[j] < arr[j+1] and not ascending):
                yield arr, (j, j+1), 2
                arr[j], arr[j+1] = arr[j+1], arr[j]
                yield arr, (j, j+1), 3

def insertion_sort(arr, ascending=True):
    for i in range(1, len(arr)):
        yield arr, (i,), 0
        key = arr[i]
        yield arr, (i,), 1
        j = i - 1
        yield arr, (j,), 2
        while j >= 0 and ((arr[j] > key and ascending) or (arr[j] < key and not ascending)):
            yield arr, (j, j+1), 3
            arr[j+1] = arr[j]
            yield arr, (j, j+1), 4
            j -= 1
            yield arr, (j,), 5
        arr[j+1] = key
        yield arr, (j+1,), 6

def selection_sort(arr, ascending=True):
    n = len(arr)
    for i in range(n):
        yield arr, (i,), 0
        min_idx = i
        yield arr, (min_idx,), 1
        for j in range(i+1, n):
            yield arr, (j,), 2
            if (arr[j] < arr[min_idx] and ascending) or (arr[j] > arr[min_idx] and not ascending):
                min_idx = j
                yield arr, (min_idx,), 3
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        yield arr, (i, min_idx), 4

def merge_sort(arr, ascending=True):
    def merge(left, right):
        result = []
        while left and right:
            if (left[0] <= right[0] and ascending) or (left[0] >= right[0] and not ascending):
                result.append(left.pop(0))
            else:
                result.append(right.pop(0))
        return result + left + right

    if len(arr) > 1:
        mid = len(arr) // 2
        yield arr, (), 2
        left = arr[:mid]
        right = arr[mid:]
        yield from merge_sort(left, ascending)
        yield from merge_sort(right, ascending)
        merged = merge(left, right)
        for i in range(len(arr)):
            arr[i] = merged[i]
            yield arr, (i,), 5

def quick_sort(arr, ascending=True):
    def qs(low, high):
        if low < high:
            yield arr, (), 1
            pivot = arr[high]
            i = low - 1
            for j in range(low, high):
                yield arr, (j, high), 2
                if (arr[j] < pivot and ascending) or (arr[j] > pivot and not ascending):
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
                    yield arr, (i, j), 3
            arr[i+1], arr[high] = arr[high], arr[i+1]
            yield arr, (i+1, high), 4
            yield from qs(low, i)
            yield from qs(i+2, high)
    yield from qs(0, len(arr)-1)

def heapify(arr, n, i):
    largest = i
    l, r = 2*i+1, 2*i+2
    if l < n and arr[l] > arr[largest]:
        largest = l
    if r < n and arr[r] > arr[largest]:
        largest = r
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        yield arr, (i, largest), 3
        yield from heapify(arr, n, largest)

def heap_sort(arr, ascending=True):
    n = len(arr)
    for i in range(n//2 - 1, -1, -1):
        yield arr, (), 0
        yield from heapify(arr, n, i)
    for i in range(n-1, 0, -1):
        yield arr, (0, i), 1
        arr[0], arr[i] = arr[i], arr[0]
        yield arr, (0, i), 2
        yield from heapify(arr, i, 0)
    if not ascending:
        arr.reverse()

def radix_sort(arr, ascending=True):
    max_num = max(arr)
    exp = 1
    yield arr, (), 0
    while max_num // exp > 0:
        yield arr, (), 1
        buckets = [[] for _ in range(10)]
        for num in arr:
            digit = (num // exp) % 10
            buckets[digit].append(num)
        arr[:] = [num for bucket in buckets for num in bucket]
        yield arr, (), 2
        exp *= 10
    if not ascending:
        arr.reverse()

# ---------------- Algorithm Steps ---------------- #
ALGORITHM_STEPS = {
    "Bubble Sort": [
        "for i in range(n):",
        "  for j in range(0, n-i-1):",
        "    if arr[j] > arr[j+1]:",
        "      swap(arr[j], arr[j+1])"
    ],
    "Insertion Sort": [
        "for i in range(1, n):",
        "  key = arr[i]",
        "  j = i - 1",
        "  while j >= 0 and arr[j] > key:",
        "    arr[j+1] = arr[j]",
        "    j -= 1",
        "  arr[j+1] = key"
    ],
    "Selection Sort": [
        "for i in range(n):",
        "  min_idx = i",
        "  for j in range(i+1, n):",
        "    if arr[j] < arr[min_idx]:",
        "      min_idx = j",
        "  swap(arr[i], arr[min_idx])"
    ],
    "Heap Sort": [
        "build max heap",
        "for i from n-1 down to 1:",
        "  swap(arr[0], arr[i])",
        "  heapify(arr, 0, i)"
    ],
    "Radix Sort": [
        "find max element",
        "for exp = 1; max/exp > 0:",
        "  counting sort by digit exp"
    ],
    "Quick Sort": [
        "quickSort(low, high):",
        "  if low < high:",
        "    p = partition(arr, low, high)",
        "    quickSort(low, p-1)",
        "    quickSort(p+1, high)"
    ],
    "Merge Sort": [
        "mergeSort(arr):",
        "  if len(arr) > 1:",
        "    split array",
        "    mergeSort(left)",
        "    mergeSort(right)",
        "    merge(left, right)"
    ]
}

# ---------------- Sorting Visualizer Class ---------------- #
class SortingVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Sorting Algorithm Visualizer")

        # Controls
        self.generate_button = tk.Button(root, text="Generate Array", command=self.generate_array)
        self.generate_button.pack()
        self.time_label = tk.Label(root, text="Time: 0.0 s")
        self.time_label.pack()

        tk.Label(root, text="Array Size:").pack()
        self.size_entry = tk.Entry(root)
        self.size_entry.insert(0, "20")
        self.size_entry.pack()

        tk.Label(root, text="Min Value:").pack()
        self.min_entry = tk.Entry(root)
        self.min_entry.insert(0, "1")
        self.min_entry.pack()

        tk.Label(root, text="Max Value:").pack()
        self.max_entry = tk.Entry(root)
        self.max_entry.insert(0, "50")
        self.max_entry.pack()

        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        right_frame = tk.Frame(main_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(right_frame, text="Algorithm Steps", font=("Arial", 12, "bold")).pack()
        self.code_text = tk.Text(right_frame, height=10, width=40, font=("Consolas", 11))
        self.code_text.pack(padx=5, pady=5)
        self.code_text.tag_configure("highlight", background="yellow")
        self.code_text.config(state=tk.DISABLED)

        # Algorithm selection
        self.algorithms = {
            "Bubble Sort": bubble_sort,
            "Insertion Sort": insertion_sort,
            "Selection Sort": selection_sort,
            "Merge Sort": merge_sort,
            "Quick Sort": quick_sort,
            "Heap Sort": heap_sort,
            "Radix Sort": radix_sort
        }
        self.array = []
        self.running = False
        self.paused = False

        self.alg_label = tk.Label(root, text="Algorithm:")
        self.alg_label.pack()
        self.alg_menu = ttk.Combobox(root, values=list(self.algorithms.keys()))
        self.alg_menu.pack()

        self.order_var = tk.StringVar(value="Ascending")
        tk.Radiobutton(root, text="Ascending Order", variable=self.order_var, value="Ascending").pack()
        tk.Radiobutton(root, text="Descending Order", variable=self.order_var, value="Descending").pack()

        self.start_button = tk.Button(root, text="Start", command=self.start_sort)
        self.start_button.pack()
        self.pause_button = tk.Button(root, text="Pause", command=self.pause_sort)
        self.pause_button.pack()
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_sort)
        self.stop_button.pack()

        # Matplotlib Figure
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

    # ---------------- GUI Helper Methods ---------------- #
    def load_algorithm_steps(self, steps):
        self.code_text.config(state=tk.NORMAL)
        self.code_text.delete("1.0", tk.END)
        for step in steps:
            self.code_text.insert(tk.END, step + "\n")
        self.code_text.config(state=tk.DISABLED)

    def highlight_step(self, step_index):
        self.code_text.config(state=tk.NORMAL)
        self.code_text.tag_remove("highlight", "1.0", tk.END)
        line_start = f"{step_index + 1}.0"
        line_end = f"{step_index + 1}.end"
        self.code_text.tag_add("highlight", line_start, line_end)
        self.code_text.config(state=tk.DISABLED)

    def draw_array(self, arr, color_positions=[]):
        self.ax.clear()
        color = ['black']*len(arr)
        for pos in color_positions:
            color[pos] = 'grey'
        self.ax.bar(range(len(arr)), arr, color=color)
        self.canvas.draw()

    def generate_array(self):
        try:
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())
            size = int(self.size_entry.get())
            if min_val >= max_val:
                raise ValueError
            if size <= 0:
                raise ValueError
        except ValueError:
            min_val, max_val, size = 1, 50, 20
        self.array = [random.randint(min_val, max_val) for _ in range(size)]
        self.draw_array(self.array)
        self.time_label.config(text="Time: 0.0 s")

    # ---------------- Sorting Controls ---------------- #
    def start_sort(self):
        if not self.alg_menu.get() or not self.array:
            return
        self.running = True
        self.paused = False
        self.start_time = time.time()
        alg_name = self.alg_menu.get()
        if alg_name in ALGORITHM_STEPS:
            self.load_algorithm_steps(ALGORITHM_STEPS[alg_name])
        arr_copy = self.array.copy()
        ascending = self.order_var.get() == "Ascending"
        gen = self.algorithms[alg_name](arr_copy, ascending)
        self.animate_sort(gen)

    def animate_sort(self, gen):
        try:
            if not self.running:
                return
            if not self.paused:
                arr, positions, step = next(gen)
                self.draw_array(arr, positions)
                self.highlight_step(step)
                current_time = time.time() - self.start_time
                self.time_label.config(text=f"Time: {current_time:.2f} s")
            self.root.after(100, lambda: self.animate_sort(gen))
        except StopIteration:
            self.running = False
            final_time = time.time() - self.start_time
            self.time_label.config(text=f"Completed in {final_time:.2f} s")

    def pause_sort(self):
        if not self.running:
            return
        if not self.paused:
            self.elapsed_time = time.time() - self.start_time
            self.paused = True
        else:
            self.start_time = time.time() - self.elapsed_time
            self.paused = False

    def stop_sort(self):
        self.running = False

# -------------------- Main -------------------- #
if __name__ == "__main__":
    root = tk.Tk()
    visualizer = SortingVisualizer(root)
    visualizer.array = [random.randint(1, 50) for _ in range(20)]
    visualizer.draw_array(visualizer.array)
    root.mainloop()
