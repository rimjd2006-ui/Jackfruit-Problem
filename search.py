import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import time
import threading

class AlgorithmVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Search Algorithm Visualizer")
        self.root.geometry("1200x700")
        
        # State variables
        self.is_running = False
        self.is_paused = False
        self.array = []
        self.search_value = 0
        self.start_time = 0
        self.algorithm = "linear"
        self.current_step = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        control_frame.pack_propagate(False)
        
        # Array generation
        ttk.Label(control_frame, text="Generate Array:").pack(pady=5)
        ttk.Label(control_frame, text="Min:").pack()
        self.min_entry = ttk.Entry(control_frame, width=10)
        self.min_entry.insert(0, "1")
        self.min_entry.pack()
        
        ttk.Label(control_frame, text="Max:").pack()
        self.max_entry = ttk.Entry(control_frame, width=10)
        self.max_entry.insert(0, "100")
        self.max_entry.pack()
        
        ttk.Label(control_frame, text="Size:").pack()
        self.size_entry = ttk.Entry(control_frame, width=10)
        self.size_entry.insert(0, "20")
        self.size_entry.pack()
        
        ttk.Button(control_frame, text="Generate Array", 
                  command=self.generate_array).pack(pady=10)
        
        # Search value
        ttk.Label(control_frame, text="Search Value:").pack(pady=(20,5))
        self.search_entry = ttk.Entry(control_frame, width=15)
        self.search_entry.pack()
        self.search_entry.insert(0, "50")
        
        # Algorithm selection
        ttk.Label(control_frame, text="Algorithm:").pack(pady=(20,5))
        self.algo_var = tk.StringVar(value="linear")
        algo_combo = ttk.Combobox(control_frame, textvariable=self.algo_var,
                                 values=["linear", "binary"], state="readonly")
        algo_combo.pack()
        
        # Control buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(pady=20)
        
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_search)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = ttk.Button(btn_frame, text="Pause", command=self.pause_search, state="disabled")
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_search, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Stats
        self.time_label = ttk.Label(control_frame, text="Time: 0.000s")
        self.time_label.pack(pady=20)
        
        self.result_label = ttk.Label(control_frame, text="Result: Not searched")
        self.result_label.pack()
        
        # Right panel - Visualization
        viz_frame = ttk.Frame(main_frame)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chart frame
        chart_frame = ttk.LabelFrame(viz_frame, text="Visualization")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Algorithm code text with highlighting
        steps_frame = ttk.LabelFrame(viz_frame, text="Algorithm Code")
        steps_frame.pack(fill=tk.X, pady=(10,0))
        
        self.code_text = tk.Text(steps_frame, height=10, width=60, wrap=tk.NONE, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(steps_frame, orient=tk.VERTICAL, command=self.code_text.yview)
        self.code_text.configure(yscrollcommand=scrollbar.set)
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure tags for highlighting
        self.code_text.tag_configure("highlight", background="yellow", foreground="black")
        self.code_text.tag_configure("normal", background="white", foreground="black")
        
    def generate_array(self):
        try:
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())
            size = int(self.size_entry.get())
            
            if min_val >= max_val or size <= 0:
                messagebox.showerror("Error", "Invalid array parameters")
                return
                
            self.array = np.random.randint(min_val, max_val, size)
            if self.algo_var.get() == "binary":
                self.array.sort()
            
            self.plot_array()
            self.setup_algorithm_code()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def setup_algorithm_code(self):
        self.code_text.delete(1.0, tk.END)
        self.current_step = 0
        
        if self.algo_var.get() == "linear":
            code = [
                "def linear_search(arr, target):",
                "    for i in range(len(arr)):",
                "        if arr[i] == target:",
                "            return i",
                "    return -1",
                "",
                f"Result = linear_search({list(self.array)}, {self.search_value})"
            ]
            self.linear_steps = [0, 1, 2, 3]  # line numbers to highlight
        else:
            code = [
                "def binary_search(arr, target):",
                "    left, right = 0, len(arr) - 1",
                "    while left <= right:",
                "        mid = (left + right) // 2",
                "        if arr[mid] == target:",
                "            return mid",
                "        elif arr[mid] < target:",
                "            left = mid + 1",
                "        else:",
                "            right = mid - 1",
                "    return -1",
                "",
                f"Result = binary_search({list(self.array)}, {self.search_value})"
            ]
            self.binary_steps = [0, 1, 2, 3, 4, 5, 6, 7]  # line numbers to highlight
        
        for i, line in enumerate(code):
            self.code_text.insert(tk.END, line + "\n")
    
    def plot_array(self, highlight_indices=None, found_index=None):
        self.ax.clear()
        
        if not self.array.size:
            return
            
        indices = np.arange(len(self.array))
        colors = ['lightblue'] * len(self.array)
        
        if highlight_indices:
            for idx in highlight_indices:
                if idx < len(colors):
                    colors[idx] = 'yellow'
        
        if found_index is not None and found_index >= 0:
            colors[found_index] = 'green'
        
        bars = self.ax.bar(indices, self.array, color=colors, alpha=0.7, edgecolor='black')
        self.ax.set_title(f"{'Binary' if self.algo_var.get() == 'binary' else 'Linear'} Search")
        self.ax.set_xlabel("Index")
        self.ax.set_ylabel("Value")
        self.ax.set_xticks(indices)
        self.ax.tick_params(axis='x', rotation=45)
        
        self.ax.axhline(y=self.search_value, color='red', linestyle='--', alpha=0.7, 
                       label=f'Target: {self.search_value}')
        self.ax.legend()
        
        self.canvas.draw()
    
    def start_search(self):
        if not self.array.size:
            messagebox.showerror("Error", "Please generate an array first")
            return
        
        try:
            self.search_value = int(self.search_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid search value")
            return
        
        self.is_running = True
        self.is_paused = False
        self.start_time = time.time()
        self.current_step = 0
        
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        self.setup_algorithm_code()  # Refresh with current search value
        
        thread = threading.Thread(target=self.run_search)
        thread.daemon = True
        thread.start()
    
    def pause_search(self):
        self.is_paused = not self.is_paused
        self.pause_btn.config(text="Resume" if self.is_paused else "Pause")
    
    def stop_search(self):
        self.is_running = False
        self.is_paused = False
        self.reset_buttons()
        self.update_time()
    
    def reset_buttons(self):
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="Pause")
        self.stop_btn.config(state="disabled")
    
    def run_search(self):
        # Clear all highlighting first
        self.clear_highlighting()
        
        if self.algo_var.get() == "linear":
            self.linear_search_animation()
        else:
            self.binary_search_animation()
        
        self.is_running = False
        self.root.after(0, self.search_complete)
    
    def clear_highlighting(self):
        self.code_text.tag_remove("highlight", "1.0", tk.END)
    
    def highlight_line(self, line_num):
        self.clear_highlighting()
        start_pos = f"{line_num + 1}.0"
        end_pos = f"{line_num + 1}.end"
        self.code_text.tag_add("highlight", start_pos, end_pos)
        self.code_text.see(start_pos)  # Scroll to highlighted line
        self.root.update()
    
    def linear_search_animation(self):
        # Highlight function definition
        self.root.after(0, lambda: self.highlight_line(0))
        time.sleep(1)
        
        for i in range(len(self.array)):
            if not self.is_running:
                return
            
            while self.is_paused:
                time.sleep(0.1)
            
            # Highlight for loop
            self.root.after(0, lambda: self.highlight_line(1))
            time.sleep(0.3)
            
            # Highlight if condition
            self.root.after(0, lambda: self.highlight_line(2))
            self.root.after(0, lambda idx=i: self.plot_array([i]))
            time.sleep(0.8)
            
            if self.array[i] == self.search_value:
                self.root.after(0, lambda idx=i: self.highlight_line(3))
                self.root.after(0, lambda idx=i: self.plot_array([i], found_index=i))
                time.sleep(1.5)
                return i
        
        # Not found
        self.root.after(0, lambda: self.highlight_line(4))
        time.sleep(1)
        self.root.after(0, lambda: self.plot_array([], found_index=-1))
        return -1
    
    def binary_search_animation(self):
        # Highlight function definition
        self.root.after(0, lambda: self.highlight_line(0))
        time.sleep(1)
        
        # Highlight initialization
        self.root.after(0, lambda: self.highlight_line(1))
        time.sleep(0.8)
        
        left, right = 0, len(self.array) - 1
        
        while left <= right:
            if not self.is_running:
                return
            
            while self.is_paused:
                time.sleep(0.1)
            
            # Highlight while loop
            self.root.after(0, lambda: self.highlight_line(2))
            time.sleep(0.3)
            
            # Highlight mid calculation
            self.root.after(0, lambda: self.highlight_line(3))
            mid = (left + right) // 2
            self.root.after(0, lambda m=mid: self.plot_array([left, mid, right]))
            time.sleep(0.8)
            
            # Highlight comparison
            self.root.after(0, lambda: self.highlight_line(4))
            time.sleep(0.5)
            
            if self.array[mid] == self.search_value:
                self.root.after(0, lambda m=mid: self.highlight_line(5))
                self.root.after(0, lambda m=mid: self.plot_array([mid], found_index=mid))
                time.sleep(1.5)
                return mid
            elif self.array[mid] < self.search_value:
                self.root.after(0, lambda: self.highlight_line(6))
                left = mid + 1
            else:
                self.root.after(0, lambda: self.highlight_line(7))
                right = mid - 1
            
            time.sleep(0.5)
        
        # Not found
        self.root.after(0, lambda: self.highlight_line(8))
        time.sleep(1)
        self.root.after(0, lambda: self.plot_array([], found_index=-1))
        return -1
    
    def search_complete(self):
        self.reset_buttons()
        self.update_time()
        self.clear_highlighting()
        result_text = "Found!" if self.search_value in self.array else "Not found"
        self.result_label.config(text=f"Result: {result_text}")
    
    def update_time(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.time_label.config(text=f"Time: {elapsed:.3f}s")

if __name__ == "__main__":
    root = tk.Tk()
    app = AlgorithmVisualizer(root)
    root.mainloop()


