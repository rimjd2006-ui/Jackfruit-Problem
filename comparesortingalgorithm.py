import tkinter as tk
from tkinter import ttk
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import copy

# ---------------- Fixed Sorting Algorithms as Generators ---------------- #

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
            yield arr[:], (j, j+1)

def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]
            j -= 1
            yield arr[:], (j+1, i)
        arr[j+1] = key
        yield arr[:], (j+1, i)

def selection_sort(arr, ascending=True):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            yield arr[:], (i, j)
            if (arr[j] < arr[min_idx] and ascending) or (arr[j] > arr[min_idx] and not ascending):
                min_idx = j
                yield arr[:], (i, min_idx)
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
        yield arr[:], (i, min_idx)

def merge_sort(arr, ascending=True):
    def merge(left, right, start):
        i, j, k = 0, 0, start
        while i < len(left) and j < len(right):
            if (left[i] <= right[j] and ascending) or (left[i] >= right[j] and not ascending):
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1
            yield arr[:], tuple(range(start, min(k+1, len(arr))))

        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1
            yield arr[:], tuple(range(start, min(k+1, len(arr))))
        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1
            yield arr[:], tuple(range(start, min(k+1, len(arr))))

    def ms(low, high):
        if low < high:
            mid = (low + high) // 2
            yield from ms(low, mid)
            yield from ms(mid+1, high)
            yield from merge(arr[low:mid+1], arr[mid+1:high+1], low)

    yield from ms(0, len(arr)-1)

def quick_sort(arr, ascending=True):
    def qs(low, high):
        if low < high:
            pivot = arr[high]
            i = low - 1
            for j in range(low, high):
                yield arr[:], (j, high)
                if (arr[j] < pivot and ascending) or (arr[j] > pivot and not ascending):
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
                    yield arr[:], (i, j)
            arr[i+1], arr[high] = arr[high], arr[i+1]
            pi = i+1
            yield arr[:], (pi, high)
            yield from qs(low, pi-1)
            yield from qs(pi+1, high)

    yield from qs(0, len(arr)-1)

def heap_sort(arr, ascending=True):
    def heapify(n, i):
        largest = i
        l, r = 2*i+1, 2*i+2
        if l < n and arr[l] > arr[largest]:
            largest = l
        if r < n and arr[r] > arr[largest]:
            largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            yield arr[:], (i, largest)
            yield from heapify(n, largest)

    n = len(arr)
    for i in range(n//2 - 1, -1, -1):
        yield from heapify(n, i)
    for i in range(n-1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        yield arr[:], (0, i)
        yield from heapify(i, 0)

def radix_sort(arr, ascending=True):
    max_num = max(arr)
    exp = 1
    while max_num // exp > 0:
        buckets = [[] for _ in range(10)]
        for num in arr:
            digit = (num // exp) % 10
            buckets[digit].append(num)
        arr[:] = [num for bucket in buckets for num in bucket]
        yield arr[:], ()
        exp *= 10

ALGORITHMS = {
    "Bubble Sort": bubble_sort,
    "Insertion Sort": insertion_sort,
    "Selection Sort": selection_sort,
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort,
    "Heap Sort": heap_sort,
    "Radix Sort": radix_sort
}

# ---------------- Unlimited Algorithm Tkinter App ---------------- #

class SortingVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Algorithm Comparison - Unlimited")

        self.array = [random.randint(1, 50) for _ in range(20)]

        self.compare_vars = {}
        compare_frame = tk.LabelFrame(root, text="Select Any Number of Algorithms")
        compare_frame.pack(fill=tk.X, padx=5, pady=5)

        self.main_canvas = None


        for name in ALGORITHMS:
            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(compare_frame, text=name, variable=var)
            cb.pack(anchor="w")
            self.compare_vars[name] = var

        for name in ALGORITHMS:
            self.compare_vars[name].set(True)

        tk.Button(compare_frame, text="Start Comparison",
                  command=self.start_live_comparison).pack(pady=5)

        tk.Button(compare_frame, text="Select All",
                  command=lambda: [v.set(True) for v in self.compare_vars.values()]
                  ).pack(side=tk.LEFT, padx=5)

        tk.Button(compare_frame, text="Clear All",
                  command=lambda: [v.set(False) for v in self.compare_vars.values()]
                  ).pack(side=tk.LEFT)

        self.active_gens = {}
        self.canvases = {}
        self.alg_frames = {}

    def start_live_comparison(self):
        
        if self.main_canvas is not None:
            self.main_canvas.destroy()
            self.main_canvas = None

        selected_algorithms = [name for name, var in self.compare_vars.items() if var.get()]
        if not selected_algorithms:
            return

        for frame in self.alg_frames.values():
            frame.destroy()
        for canvas_tuple in self.canvases.values():
            canvas_tuple[2].get_tk_widget().destroy()

        self.active_gens.clear()
        self.canvases.clear()
        self.alg_frames.clear()

        base_array = self.array.copy()
        self.main_canvas = tk.Canvas(self.root)
        main_canvas = self.main_canvas

        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(main_canvas, orient=tk.VERTICAL, command=main_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.comparison_frame = tk.Frame(main_canvas)
        main_canvas.create_window((0, 0), window=self.comparison_frame, anchor='nw')
        self.comparison_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        main_canvas.configure(yscrollcommand=scrollbar.set)

        # ----------- FIXED LAYOUT LOGIC (ONLY CHANGE) ----------- #
        count = len(selected_algorithms)

        if count <= 3:
            cols = count
        elif count <= 6:
            cols = 3
        else:
            cols = 4

        rows = (count + cols - 1) // cols

        fig_width = max(3.5, 12 / cols)
        fig_height = max(2.5, 7 / rows)
        # ------------------------------------------------------- #

        for i, alg_name in enumerate(selected_algorithms):
            frame = tk.LabelFrame(self.comparison_frame, text=alg_name, padx=5, pady=5)
            frame.grid(row=i // cols, column=i % cols,
                       sticky='nsew', padx=5, pady=5)
            self.alg_frames[alg_name] = frame

            arr_copy = base_array.copy()
            gen = ALGORITHMS[alg_name](arr_copy)
            self.active_gens[alg_name] = (gen, arr_copy)

            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            ax.set_title(alg_name, fontsize=10)
            ax.set_ylim(0, 60)
            ax.tick_params(labelsize=6)

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.canvases[alg_name] = (fig, ax, canvas)

        for c in range(cols):
            self.comparison_frame.grid_columnconfigure(c, weight=1)
        for r in range(rows):
            self.comparison_frame.grid_rowconfigure(r, weight=1)

        self.animate_all_algorithms()

    def animate_all_algorithms(self):
        finished = []

        for alg_name, (gen, arr) in list(self.active_gens.items()):
            fig, ax, canvas = self.canvases[alg_name]
            try:
                arr_state, highlights = next(gen)

                ax.clear()
                ax.set_ylim(0, 60)

                colors = ['skyblue'] * len(arr_state)
                if highlights:
                    for i in highlights:
                        if 0 <= i < len(colors):
                            colors[i] = 'red'

                ax.bar(range(len(arr_state)), arr_state,
                       color=colors, edgecolor='black', linewidth=0.5)

                sorted_count = sum(
                    1 for k in range(1, len(arr_state))
                    if arr_state[k-1] <= arr_state[k]
                )
                ax.set_title(
                    f"{alg_name}\n({sorted_count}/{len(arr_state)} sorted)",
                    fontsize=9
                )

                canvas.draw()
                canvas.flush_events()

            except StopIteration:
                finished.append(alg_name)
                ax.clear()
                ax.set_ylim(0, 60)
                ax.bar(range(len(arr)), arr,
                       color='green', edgecolor='black', linewidth=0.5)
                ax.set_title(f"{alg_name}\nFINISHED ✓",
                             fontsize=9, color='green')
                canvas.draw()

        for alg in finished:
            self.active_gens.pop(alg, None)

        if self.active_gens:
            delay = max(100, 400 - len(self.active_gens) * 30)
            self.root.after(delay, self.animate_all_algorithms)

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1600x900")
    visualizer = SortingVisualizer(root)
    root.mainloop()



