import tkinter as tk
from tkinter import ttk
import random
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# -------------------------------------------------
# Algorithm generators yield (array, index, line)
# -------------------------------------------------

def linear_search(arr, target):
    for i in range(len(arr)):
        yield arr, i, 1
        if arr[i] == target:
            yield arr, i, 2
            return
    yield arr, None, 3

def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    yield arr, None, 1
    while low <= high:
        yield arr, None, 3
        mid = (low + high) // 2
        yield arr, mid, 4
        if arr[mid] == target:
            yield arr, mid, 5
            return
        elif arr[mid] < target:
            yield arr, mid, 6
            low = mid + 1
        else:
            yield arr, mid, 7
            high = mid - 1
    yield arr, None, 8

# -------------------------------------------------
# Visualizer class
# -------------------------------------------------

class SearchComparison:
    def __init__(self, root):
        self.root = root
        self.root.title("Linear vs Binary Search Comparison")
        self.root.geometry("1600x900")

        self.running = False
        self.paused = False

        self.elapsed = {"Linear": 0, "Binary": 0}
        self.start_time = {}

        self.array = []
        self.gens = {}

        self.build_ui()

    # ---------------- UI ---------------- #

    def build_ui(self):
        control = tk.Frame(self.root)
        control.pack(fill=tk.X, pady=5)

        for lbl, default in [("Min", "1"), ("Max", "100"), ("Elements", "30")]:
            tk.Label(control, text=lbl + ":").pack(side=tk.LEFT)
            e = tk.Entry(control, width=6)
            e.insert(0, default)
            e.pack(side=tk.LEFT)
            setattr(self, lbl.lower(), e)

        tk.Label(control, text="Target:").pack(side=tk.LEFT, padx=5)
        self.target = tk.Entry(control, width=6)
        self.target.pack(side=tk.LEFT)

        tk.Button(control, text="Generate", command=self.generate).pack(side=tk.LEFT, padx=5)
        tk.Button(control, text="Start", command=self.start).pack(side=tk.LEFT)
        tk.Button(control, text="Pause", command=self.pause).pack(side=tk.LEFT)
        tk.Button(control, text="Stop", command=self.stop).pack(side=tk.LEFT)

        self.timer_l = tk.Label(control, text="Linear: 0.000 s")
        self.timer_l.pack(side=tk.RIGHT, padx=10)
        self.timer_b = tk.Label(control, text="Binary: 0.000 s")
        self.timer_b.pack(side=tk.RIGHT)

        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True)

        self.frames = {}
        self.axes = {}
        self.canvases = {}
        self.texts = {}

        for i, name in enumerate(["Linear", "Binary"]):
            frame = tk.LabelFrame(main, text=f"{name} Search")
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

            fig, ax = plt.subplots(figsize=(6, 4))
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            text = tk.Text(frame, font=("Consolas", 10), height=12)
            text.pack(fill=tk.X)
            text.tag_config("active", background="yellow")

            self.frames[name] = frame
            self.axes[name] = ax
            self.canvases[name] = canvas
            self.texts[name] = text

    # ---------------- Logic ---------------- #

    def generate(self):
        self.stop()
        mn = int(self.min.get())
        mx = int(self.max.get())
        n = int(self.elements.get())

        base = random.sample(range(mn, mx + 1), n)

        self.array = {
            "Linear": base[:],
            "Binary": sorted(base)
        }

        self.draw("Linear")
        self.draw("Binary")

    def start(self):
        if not self.array or self.running:
            return

        self.running = True
        self.paused = False

        target = int(self.target.get())

        self.gens["Linear"] = linear_search(self.array["Linear"], target)
        self.gens["Binary"] = binary_search(self.array["Binary"], target)

        self.start_time["Linear"] = time.time() - self.elapsed["Linear"]
        self.start_time["Binary"] = time.time() - self.elapsed["Binary"]

        self.load_texts()
        self.animate()

    def pause(self):
        if self.running:
            self.paused = True

    def stop(self):
        self.running = False
        self.paused = False
        self.elapsed = {"Linear": 0, "Binary": 0}
        self.timer_l.config(text="Linear: 0.000 s")
        self.timer_b.config(text="Binary: 0.000 s")

        for t in self.texts.values():
            t.tag_remove("active", "1.0", tk.END)

    def animate(self):
        if not self.running or self.paused:
            return

        finished = []

        for name in ["Linear", "Binary"]:
            try:
                arr, idx, line = next(self.gens[name])
                self.elapsed[name] = time.time() - self.start_time[name]

                if name == "Linear":
                    self.timer_l.config(text=f"Linear: {self.elapsed[name]:.3f} s")
                else:
                    self.timer_b.config(text=f"Binary: {self.elapsed[name]:.3f} s")

                self.draw(name, idx)
                self.highlight(name, line)

            except StopIteration:
                finished.append(name)

        if len(finished) == 2:
            self.running = False
        else:
            self.root.after(600, self.animate)

    # ---------------- Drawing ---------------- #

    def draw(self, name, highlight=None):
        ax = self.axes[name]
        arr = self.array[name]

        ax.clear()
        colors = ["skyblue"] * len(arr)
        if highlight is not None:
            colors[highlight] = "red"

        ax.bar(range(len(arr)), arr, color=colors)
        ax.set_ylim(0, max(arr) + 10)
        self.canvases[name].draw()

    # ---------------- Algorithm Text ---------------- #

    def load_texts(self):
        self.texts["Linear"].delete("1.0", tk.END)
        self.texts["Linear"].insert(tk.END,
            "1  for i in range(n):\n"
            "2      if arr[i] == target:\n"
            "3  return not found\n"
        )

        self.texts["Binary"].delete("1.0", tk.END)
        self.texts["Binary"].insert(tk.END,
            "1  low = 0\n"
            "2  high = n-1\n"
            "3  while low <= high:\n"
            "4      mid = (low+high)//2\n"
            "5      if arr[mid] == target:\n"
            "6      elif arr[mid] < target:\n"
            "7      else:\n"
            "8  return not found\n"
        )

    def highlight(self, name, line):
        text = self.texts[name]
        text.tag_remove("active", "1.0", tk.END)
        start = f"{line}.0"
        end = f"{line}.end"
        text.tag_add("active", start, end)
        text.see(start)

# ---------------- Run ---------------- #

if __name__ == "__main__":
    root = tk.Tk()
    SearchComparison(root)
    root.mainloop()
