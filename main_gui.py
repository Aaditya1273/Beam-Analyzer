import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from beam_engine import OverhangingBeam, Support, ConcentratedLoad, UniformlyVaryingLoad

class BeamAnalysisGUI(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("Professional Beam Analysis")
        self.geometry("1200x800")

        self.beam = None
        self.create_widgets()

    def create_widgets(self):
        main_frame = tb.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        # Configure grid layout
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # --- Input Frame ---
        input_frame = tb.Labelframe(main_frame, text="Configuration", padding=15, bootstyle="info")
        input_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        input_frame.grid_columnconfigure(0, weight=1)

        # --- Plot Frame ---
        plot_frame = tb.Labelframe(main_frame, text="Diagrams", padding=15, bootstyle="info")
        plot_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        plot_frame.grid_rowconfigure(0, weight=1)
        plot_frame.grid_columnconfigure(0, weight=1)

        # --- Results Frame ---
        results_frame = tb.Labelframe(main_frame, text="Numerical Results", padding=15, bootstyle="success")
        results_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)

        # --- Populate Input Frame ---
        self.populate_input_frame(input_frame)

        # --- Populate Plot Frame ---
        self.figure, self.axes = plt.subplots(3, 1, figsize=(8, 6), sharex=True)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=YES)

        # --- Populate Results Frame ---
        self.results_text = tk.Text(results_frame, height=10, width=50, state="disabled", font=("Courier", 10))
        self.results_text.pack(fill=BOTH, expand=YES, padx=5, pady=5)

    def populate_input_frame(self, parent_frame):
        # Beam Properties
        beam_props_frame = tb.Labelframe(parent_frame, text="Beam Properties", padding=10, bootstyle="primary")
        beam_props_frame.pack(fill=X, pady=5, padx=5)

        tb.Label(beam_props_frame, text="Length (m):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.beam_length_entry = tb.Entry(beam_props_frame, bootstyle="primary")
        self.beam_length_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(beam_props_frame, text="Support 1 Pos (m):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.support1_pos_entry = tb.Entry(beam_props_frame, bootstyle="primary")
        self.support1_pos_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(beam_props_frame, text="Support 2 Pos (m):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.support2_pos_entry = tb.Entry(beam_props_frame, bootstyle="primary")
        self.support2_pos_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.create_beam_btn = tb.Button(beam_props_frame, text="Create Beam", command=self.create_beam, bootstyle="success-outline")
        self.create_beam_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # Load Properties
        load_props_frame = tb.Labelframe(parent_frame, text="Add Load", padding=10, bootstyle="primary")
        load_props_frame.pack(fill=X, pady=15, padx=5)

        tb.Label(load_props_frame, text="Load Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.load_type_combo = tb.Combobox(load_props_frame, values=["Concentrated", "Uniformly Varying"], state="readonly", bootstyle="primary")
        self.load_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.load_type_combo.set("Concentrated")

        # Fields for all load types
        tb.Label(load_props_frame, text="Position/Start (m):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.load_pos1_entry = tb.Entry(load_props_frame, bootstyle="primary")
        self.load_pos1_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(load_props_frame, text="Magnitude/Start (N):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.load_mag1_entry = tb.Entry(load_props_frame, bootstyle="primary")
        self.load_mag1_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(load_props_frame, text="End Position (m):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.load_pos2_entry = tb.Entry(load_props_frame, bootstyle="primary")
        self.load_pos2_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        tb.Label(load_props_frame, text="End Magnitude (N):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.load_mag2_entry = tb.Entry(load_props_frame, bootstyle="primary")
        self.load_mag2_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        self.add_load_btn = tb.Button(load_props_frame, text="Add Load", command=self.add_load, bootstyle="success-outline", state="disabled")
        self.add_load_btn.grid(row=5, column=0, columnspan=2, pady=10)

        # Control Buttons
        control_frame = tb.Frame(parent_frame)
        control_frame.pack(fill=X, pady=20, padx=5)

        self.analyze_btn = tb.Button(control_frame, text="Analyze Beam", command=self.analyze_beam, bootstyle="danger", state="disabled")
        self.analyze_btn.pack(side=LEFT, expand=True, fill=X, padx=5)

        self.clear_btn = tb.Button(control_frame, text="Clear All", command=self.clear_all, bootstyle="warning")
        self.clear_btn.pack(side=LEFT, expand=True, fill=X, padx=5)

    def create_beam(self):
        pass # To be implemented

    def add_load(self):
        pass # To be implemented

    def analyze_beam(self):
        pass # To be implemented

    def clear_all(self):
        pass # To be implemented

if __name__ == "__main__":
    app = BeamAnalysisGUI()
    app.mainloop()
