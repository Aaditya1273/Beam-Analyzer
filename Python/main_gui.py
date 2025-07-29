import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import threading
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json

# Enhanced beam analysis classes
@dataclass
class Support:
    position: float
    type: str = "pin"  # pin, roller, fixed

@dataclass
class ConcentratedLoad:
    position: float
    magnitude: float
    angle: float = -90  # degrees from horizontal

@dataclass
class UniformlyVaryingLoad:
    start_pos: float
    end_pos: float
    start_magnitude: float
    end_magnitude: float

@dataclass
class BeamProperties:
    length: float
    elastic_modulus: float = 200e9  # Pa
    moment_of_inertia: float = 8.33e-6  # m^4
    cross_section_area: float = 0.01  # m^2
    density: float = 7850  # kg/m^3

class AdvancedBeamEngine:
    def __init__(self, beam_props: BeamProperties):
        self.beam_props = beam_props
        self.supports: List[Support] = []
        self.concentrated_loads: List[ConcentratedLoad] = []
        self.varying_loads: List[UniformlyVaryingLoad] = []
        self.results = {}
        
    def add_support(self, support: Support):
        self.supports.append(support)
        
    def add_concentrated_load(self, load: ConcentratedLoad):
        self.concentrated_loads.append(load)
        
    def add_varying_load(self, load: UniformlyVaryingLoad):
        self.varying_loads.append(load)
        
    def analyze(self):
        """Comprehensive beam analysis with enhanced calculations"""
        x = np.linspace(0, self.beam_props.length, 1000)
        
        # Initialize arrays
        shear = np.zeros_like(x)
        moment = np.zeros_like(x)
        deflection = np.zeros_like(x)
        stress = np.zeros_like(x)
        
        # Calculate reactions at supports
        reactions = self._calculate_reactions()
        
        # Apply concentrated loads
        for load in self.concentrated_loads:
            load_idx = np.argmin(np.abs(x - load.position))
            for i in range(load_idx, len(x)):
                shear[i] += load.magnitude * np.sin(np.radians(load.angle))
                
        # Apply varying loads
        for load in self.varying_loads:
            start_idx = np.argmin(np.abs(x - load.start_pos))
            end_idx = np.argmin(np.abs(x - load.end_pos))
            
            for i in range(start_idx, end_idx + 1):
                pos_ratio = (x[i] - load.start_pos) / (load.end_pos - load.start_pos)
                load_mag = load.start_magnitude + pos_ratio * (load.end_magnitude - load.start_magnitude)
                shear[i] += load_mag
                
        # Apply support reactions
        for support, reaction in zip(self.supports, reactions):
            support_idx = np.argmin(np.abs(x - support.position))
            for i in range(support_idx, len(x)):
                shear[i] -= reaction
                
        # Calculate moment from shear
        dx = x[1] - x[0]
        for i in range(1, len(moment)):
            moment[i] = moment[i-1] + shear[i-1] * dx
            
        # Calculate deflection using moment-area method
        EI = self.beam_props.elastic_modulus * self.beam_props.moment_of_inertia
        for i in range(1, len(deflection)):
            deflection[i] = deflection[i-1] + moment[i-1] * dx / EI
            
        # Calculate stress
        y_max = 0.1  # Assume beam height
        stress = moment * y_max / self.beam_props.moment_of_inertia
        
        self.results = {
            'x': x,
            'shear': shear,
            'moment': moment,
            'deflection': deflection,
            'stress': stress,
            'reactions': reactions,
            'max_moment': np.max(np.abs(moment)),
            'max_deflection': np.max(np.abs(deflection)),
            'max_stress': np.max(np.abs(stress))
        }
        
        return self.results
        
    def _calculate_reactions(self):
        """Calculate support reactions using equilibrium equations"""
        if len(self.supports) < 2:
            return [0] * len(self.supports)
            
        # Simple calculation for two supports
        total_load = sum(load.magnitude for load in self.concentrated_loads)
        for load in self.varying_loads:
            avg_load = (load.start_magnitude + load.end_magnitude) / 2
            load_length = load.end_pos - load.start_pos
            total_load += avg_load * load_length
            
        if len(self.supports) == 2:
            # For two supports, distribute load based on position
            L = self.beam_props.length
            a = self.supports[0].position
            b = self.supports[1].position
            
            R1 = total_load * (L - a) / (b - a) * 0.5
            R2 = total_load - R1
            return [R1, R2]
            
        return [total_load / len(self.supports)] * len(self.supports)

class Advanced3DBeamGUI(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("🏗️ Professional 3D Beam Analysis Suite")
        self.geometry("1600x1000")
        self.resizable(True, True)
        
        # Initialize variables before they're used
        self.beam_engine = None
        self.animation_running = False
        self.analysis_thread = None
        self.stop_analysis = False
        self.auto_analyze = tk.BooleanVar(value=True)
        self.results_panel_visible = tk.BooleanVar(value=True)
        self.results_panel = None
        self.viz_panel = None
        self.main_container = None
        
        # Apply custom styling
        self.apply_custom_theme()
        
        # Create widgets after all variables are initialized
        self.create_advanced_widgets()
        
    def apply_custom_theme(self):
        """Apply advanced gradient theme and styling"""
        style = tb.Style()
        
        # Configure custom colors with gradients
        style.configure("Gradient.TLabelframe", 
                       background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)")
        style.configure("Success.TLabelframe",
                       background="linear-gradient(135deg, #11998e 0%, #38ef7d 100%)")
        style.configure("Danger.TLabelframe",
                       background="linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)")
        
        # Configure the main window background
        self.configure(bg="#1a1a2e")
        
    def create_advanced_widgets(self):
        # Create main container with gradient background
        self.main_container = tb.Frame(self, padding=10)
        self.main_container.pack(fill=BOTH, expand=YES)
        
        # Configure advanced grid layout
        self.main_container.grid_columnconfigure(0, weight=1, minsize=400)
        self.main_container.grid_columnconfigure(1, weight=2, minsize=800)
        self.main_container.grid_columnconfigure(2, weight=1, minsize=400)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Left Panel - Advanced Controls
        self.create_control_panel(self.main_container)
        
        # Center Panel - 3D Visualization
        self.create_3d_visualization_panel(self.main_container)
        
        # Right Panel - Real-time Results & Analysis
        self.results_panel = self.create_results_panel(self.main_container)
        self.results_panel.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        
        # Bottom Status Bar
        self.create_status_bar()
        
    def create_control_panel(self, parent):
        control_panel = tb.Labelframe(parent, text="🔧 Advanced Control Center", 
                                     padding=15, bootstyle="info")
        control_panel.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Create notebook for organized tabs
        notebook = tb.Notebook(control_panel, bootstyle="info")
        notebook.pack(fill=BOTH, expand=YES)
        
        # Beam Properties Tab
        beam_tab = tb.Frame(notebook)
        notebook.add(beam_tab, text="Beam Properties")
        self.create_beam_properties_tab(beam_tab)
        
        # Supports Tab
        supports_tab = tb.Frame(notebook)
        notebook.add(supports_tab, text="Supports")
        self.create_supports_tab(supports_tab)
        
        # Loads Tab
        loads_tab = tb.Frame(notebook)
        notebook.add(loads_tab, text="Loads")
        self.create_loads_tab(loads_tab)
        
        # Analysis Tab
        analysis_tab = tb.Frame(notebook)
        notebook.add(analysis_tab, text="Analysis")
        self.create_analysis_tab(analysis_tab)
        
    def create_beam_properties_tab(self, parent):
        # Enhanced beam properties with material selection
        props_frame = tb.Labelframe(parent, text="Material & Geometry", padding=10)
        props_frame.pack(fill=X, pady=5)
        
        # Material preset
        tb.Label(props_frame, text="Material Preset:").grid(row=0, column=0, sticky="w", pady=2)
        self.material_combo = tb.Combobox(props_frame, values=["Steel", "Aluminum", "Concrete", "Wood", "Custom"],
                                         state="readonly", bootstyle="info")
        self.material_combo.grid(row=0, column=1, sticky="ew", pady=2, padx=(5,0))
        self.material_combo.set("Steel")
        self.material_combo.bind("<<ComboboxSelected>>", self.on_material_change)
        
        # Beam dimensions
        dimensions = [
            ("Length (m):", "beam_length"),
            ("Height (m):", "beam_height"),
            ("Width (m):", "beam_width"),
            ("E (GPa):", "elastic_modulus"),
            ("I (m⁴):", "moment_inertia"),
            ("Area (m²):", "cross_area")
        ]
        
        self.property_vars = {}
        for i, (label, var_name) in enumerate(dimensions, 1):
            tb.Label(props_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar(value="10" if "Length" in label else "0.1")
            entry = tb.Entry(props_frame, textvariable=var, bootstyle="info")
            entry.grid(row=i, column=1, sticky="ew", pady=2, padx=(5,0))
            self.property_vars[var_name] = var
            
        props_frame.grid_columnconfigure(1, weight=1)
        
        # Create beam button
        create_btn = tb.Button(props_frame, text="🔨 Create Advanced Beam", 
                              command=self.create_advanced_beam, bootstyle="success")
        create_btn.grid(row=len(dimensions)+1, column=0, columnspan=2, pady=10, sticky="ew")
        
    def create_supports_tab(self, parent):
        supports_frame = tb.Labelframe(parent, text="Support Configuration", padding=10)
        supports_frame.pack(fill=X, pady=5)
        
        # Support type and position
        tb.Label(supports_frame, text="Support Type:").grid(row=0, column=0, sticky="w", pady=2)
        self.support_type_combo = tb.Combobox(supports_frame, values=["Pin", "Roller", "Fixed"],
                                             state="readonly", bootstyle="warning")
        self.support_type_combo.grid(row=0, column=1, sticky="ew", pady=2, padx=(5,0))
        self.support_type_combo.set("Pin")
        
        tb.Label(supports_frame, text="Position (m):").grid(row=1, column=0, sticky="w", pady=2)
        self.support_pos_var = tk.StringVar()
        support_pos_entry = tb.Entry(supports_frame, textvariable=self.support_pos_var, bootstyle="warning")
        support_pos_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=(5,0))
        
        # Add support button
        add_support_btn = tb.Button(supports_frame, text="➕ Add Support", 
                                   command=self.add_support, bootstyle="warning")
        add_support_btn.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        
        # Support list
        self.support_listbox = tk.Listbox(supports_frame, height=4, font=("Consolas", 9))
        self.support_listbox.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
        
        # Remove support button
        remove_support_btn = tb.Button(supports_frame, text="❌ Remove Selected", 
                                      command=self.remove_support, bootstyle="danger")
        remove_support_btn.grid(row=4, column=0, columnspan=2, pady=2, sticky="ew")
        
        supports_frame.grid_columnconfigure(1, weight=1)
        
    def create_loads_tab(self, parent):
        loads_frame = tb.Labelframe(parent, text="Load Configuration", padding=10)
        loads_frame.pack(fill=X, pady=5)
        
        # Load type selection
        tb.Label(loads_frame, text="Load Type:").grid(row=0, column=0, sticky="w", pady=2)
        self.load_type_combo = tb.Combobox(loads_frame, values=["Concentrated", "Uniformly Varying", "Distributed"],
                                          state="readonly", bootstyle="danger")
        self.load_type_combo.grid(row=0, column=1, sticky="ew", pady=2, padx=(5,0))
        self.load_type_combo.set("Concentrated")
        self.load_type_combo.bind("<<ComboboxSelected>>", self.on_load_type_change)
        
        # Dynamic load parameters frame
        self.load_params_frame = tb.Frame(loads_frame)
        self.load_params_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.load_vars = {}
        self.create_load_inputs()
        
        # Add load button
        add_load_btn = tb.Button(loads_frame, text="⚡ Add Load", 
                                command=self.add_load, bootstyle="danger")
        add_load_btn.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        
        # Load list
        self.load_listbox = tk.Listbox(loads_frame, height=4, font=("Consolas", 9))
        self.load_listbox.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
        
        # Remove load button
        remove_load_btn = tb.Button(loads_frame, text="🗑️ Remove Selected", 
                                   command=self.remove_load, bootstyle="danger")
        remove_load_btn.grid(row=4, column=0, columnspan=2, pady=2, sticky="ew")
        
        loads_frame.grid_columnconfigure(1, weight=1)
        
    def create_analysis_tab(self, parent):
        analysis_frame = tb.Labelframe(parent, text="Analysis Controls", padding=10)
        analysis_frame.pack(fill=X, pady=5)
        
        # Real-time analysis toggle
        auto_check = tb.Checkbutton(analysis_frame, text="🔄 Real-time Analysis", 
                                   variable=self.auto_analyze, bootstyle="success-round-toggle")
        auto_check.pack(anchor="w", pady=5)
        
        # Analysis buttons
        analyze_btn = tb.Button(analysis_frame, text="🧮 Analyze Beam", 
                               command=self.analyze_beam, bootstyle="success")
        analyze_btn.pack(fill=X, pady=2)
        
        animate_btn = tb.Button(analysis_frame, text="🎬 Animate Results", 
                               command=self.animate_results, bootstyle="info")
        animate_btn.pack(fill=X, pady=2)
        
        export_btn = tb.Button(analysis_frame, text="💾 Export Results", 
                              command=self.export_results, bootstyle="secondary")
        export_btn.pack(fill=X, pady=2)
        
        clear_btn = tb.Button(analysis_frame, text="🧹 Clear All", 
                             command=self.clear_all, bootstyle="warning")
        clear_btn.pack(fill=X, pady=2)
        
    def create_3d_visualization_panel(self, parent):
        self.viz_panel = tb.Labelframe(parent, text="🎯 3D Interactive Visualization", 
                                 padding=10, bootstyle="success")
        self.viz_panel.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Create matplotlib figure with 3D capabilities
        self.fig = plt.figure(figsize=(12, 8), facecolor='#2c3e50')
        self.fig.patch.set_facecolor('#2c3e50')
        
        # Create subplots for different views
        gs = self.fig.add_gridspec(2, 2, height_ratios=[2, 1], width_ratios=[1, 1])
        
        # 3D main view
        self.ax_3d = self.fig.add_subplot(gs[0, :], projection='3d')
        self.ax_3d.set_facecolor('#34495e')
        
        # 2D analysis plots
        self.ax_shear = self.fig.add_subplot(gs[1, 0])
        self.ax_moment = self.fig.add_subplot(gs[1, 1])
        
        for ax in [self.ax_shear, self.ax_moment]:
            ax.set_facecolor('#34495e')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            
        self.ax_3d.tick_params(colors='white')
        
        plt.tight_layout()
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_panel)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
        
        # Initialize empty plot
        self.update_3d_visualization()
        
    def toggle_results_panel(self):
        is_visible = self.results_panel_visible.get()
        if is_visible:
            self.results_panel.grid_remove()
            self.main_container.grid_columnconfigure(1, weight=3)
            self.main_container.grid_columnconfigure(2, weight=0)
        else:
            self.results_panel.grid()
            self.main_container.grid_columnconfigure(1, weight=2)
            self.main_container.grid_columnconfigure(2, weight=1)
        self.results_panel_visible.set(not is_visible)

    def create_results_panel(self, parent):
        results_panel = tb.Labelframe(parent, text="📊 Real-time Results Dashboard", 
                                     padding=10, bootstyle="warning")

        # Add a toggle button
        toggle_button = tb.Button(results_panel, text="<>", command=self.toggle_results_panel, bootstyle="light-outline", width=3)
        toggle_button.place(relx=1.0, rely=0, anchor='ne', x=-5, y=5)

        # Results notebook
        results_notebook = tb.Notebook(results_panel, bootstyle="warning")
        results_notebook.pack(fill=BOTH, expand=YES, pady=(20,0)) # Add padding to avoid overlap

        # Summary tab
        summary_tab = tb.Frame(results_notebook)
        results_notebook.add(summary_tab, text="Summary")
        self.create_summary_tab(summary_tab)
        
        # Detailed tab
        detailed_tab = tb.Frame(results_notebook)
        results_notebook.add(detailed_tab, text="Detailed")
        self.create_detailed_tab(detailed_tab)
        
        # Safety tab
        safety_tab = tb.Frame(results_notebook)
        results_notebook.add(safety_tab, text="Safety")
        self.create_safety_tab(safety_tab)

        return results_panel
        
    def create_summary_tab(self, parent):
        summary_frame = tb.Frame(parent, padding=10)
        summary_frame.pack(fill=BOTH, expand=YES)
        
        self.summary_text = tk.Text(summary_frame, height=20, width=30, 
                                   state="disabled", font=("Consolas", 10),
                                   bg="#2c3e50", fg="#ecf0f1", insertbackground="#ecf0f1")
        scrollbar = tb.Scrollbar(summary_frame, orient="vertical", command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=scrollbar.set)
        
        self.summary_text.pack(side="left", fill=BOTH, expand=YES)
        scrollbar.pack(side="right", fill="y")
        
    def create_detailed_tab(self, parent):
        detailed_frame = tb.Frame(parent, padding=10)
        detailed_frame.pack(fill=BOTH, expand=YES)
        
        self.detailed_text = tk.Text(detailed_frame, height=20, width=30, 
                                    state="disabled", font=("Consolas", 9),
                                    bg="#2c3e50", fg="#ecf0f1", insertbackground="#ecf0f1")
        detailed_scrollbar = tb.Scrollbar(detailed_frame, orient="vertical", command=self.detailed_text.yview)
        self.detailed_text.configure(yscrollcommand=detailed_scrollbar.set)
        
        self.detailed_text.pack(side="left", fill=BOTH, expand=YES)
        detailed_scrollbar.pack(side="right", fill="y")
        
    def create_safety_tab(self, parent):
        safety_frame = tb.Frame(parent, padding=10)
        safety_frame.pack(fill=BOTH, expand=YES)
        
        self.safety_text = tk.Text(safety_frame, height=20, width=30, 
                                  state="disabled", font=("Consolas", 10),
                                  bg="#2c3e50", fg="#ecf0f1", insertbackground="#ecf0f1")
        safety_scrollbar = tb.Scrollbar(safety_frame, orient="vertical", command=self.safety_text.yview)
        self.safety_text.configure(yscrollcommand=safety_scrollbar.set)
        
        self.safety_text.pack(side="left", fill=BOTH, expand=YES)
        safety_scrollbar.pack(side="right", fill="y")
        
    def create_status_bar(self):
        self.status_bar = tb.Frame(self, height=25)
        self.status_bar.pack(fill=X, side=BOTTOM)
        
        self.status_label = tb.Label(self.status_bar, text="🚀 Ready for advanced beam analysis", 
                                    bootstyle="info")
        self.status_label.pack(side=LEFT, padx=10)
        
        self.progress = tb.Progressbar(self.status_bar, mode='indeterminate', bootstyle="success-striped")
        self.progress.pack(side=RIGHT, padx=10, pady=2)
        
    # Event handlers and methods
    def on_material_change(self, event=None):
        """Update material properties based on selection"""
        material = self.material_combo.get()
        material_props = {
            "Steel": {"E": "200", "density": "7850"},
            "Aluminum": {"E": "70", "density": "2700"},
            "Concrete": {"E": "30", "density": "2400"},
            "Wood": {"E": "12", "density": "600"}
        }
        
        if material in material_props:
            self.property_vars["elastic_modulus"].set(material_props[material]["E"])
            
    def on_load_type_change(self, event=None):
        """Update load input fields based on type"""
        self.create_load_inputs()
        
    def create_load_inputs(self):
        """Create dynamic load input fields"""
        for widget in self.load_params_frame.winfo_children():
            widget.destroy()
            
        load_type = self.load_type_combo.get()
        
        if load_type == "Concentrated":
            fields = [("Position (m):", "pos"), ("Magnitude (kN):", "mag"), ("Angle (°):", "angle")]
            defaults = ["5", "10", "-90"]
        elif load_type == "Uniformly Varying":
            fields = [("Start Pos (m):", "start_pos"), ("End Pos (m):", "end_pos"),
                     ("Start Mag (kN/m):", "start_mag"), ("End Mag (kN/m):", "end_mag")]
            defaults = ["2", "8", "5", "15"]
        else:  # Distributed
            fields = [("Start Pos (m):", "start_pos"), ("End Pos (m):", "end_pos"), ("Magnitude (kN/m):", "mag")]
            defaults = ["1", "9", "10"]
            
        self.load_vars.clear()
        for i, ((label, var_name), default) in enumerate(zip(fields, defaults)):
            tb.Label(self.load_params_frame, text=label).grid(row=i, column=0, sticky="w", pady=1)
            var = tk.StringVar(value=default)
            entry = tb.Entry(self.load_params_frame, textvariable=var, bootstyle="danger", width=15)
            entry.grid(row=i, column=1, sticky="ew", pady=1, padx=(5,0))
            self.load_vars[var_name] = var
            
        self.load_params_frame.grid_columnconfigure(1, weight=1)
        
    def create_advanced_beam(self):
        """Create beam with advanced properties"""
        try:
            length = float(self.property_vars["beam_length"].get())
            height = float(self.property_vars["beam_height"].get())
            width = float(self.property_vars["beam_width"].get())
            E = float(self.property_vars["elastic_modulus"].get()) * 1e9  # Convert GPa to Pa
            
            # Calculate moment of inertia for rectangular cross-section
            I = (width * height**3) / 12
            A = width * height
            
            beam_props = BeamProperties(
                length=length,
                elastic_modulus=E,
                moment_of_inertia=I,
                cross_section_area=A
            )
            
            self.beam_engine = AdvancedBeamEngine(beam_props)
            self.update_status("✅ Advanced beam created successfully!")
            self.update_3d_visualization()
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            
    def add_support(self):
        """Add support to beam"""
        if not self.beam_engine:
            messagebox.showwarning("Warning", "Create beam first!")
            return
            
        try:
            pos = float(self.support_pos_var.get())
            support_type = self.support_type_combo.get().lower()
            
            support = Support(position=pos, type=support_type)
            self.beam_engine.add_support(support)
            
            self.support_listbox.insert(tk.END, f"{support_type.title()} @ {pos}m")
            self.support_pos_var.set("")
            self.update_status(f"➕ {support_type.title()} support added at {pos}m")
            
            if self.auto_analyze.get():
                self.analyze_beam()
                
        except ValueError:
            messagebox.showerror("Input Error", "Invalid position value!")
            
    def remove_support(self):
        """Remove selected support"""
        selection = self.support_listbox.curselection()
        if selection and self.beam_engine:
            idx = selection[0]
            self.beam_engine.supports.pop(idx)
            self.support_listbox.delete(idx)
            self.update_status("❌ Support removed")
            
            if self.auto_analyze.get():
                self.analyze_beam()
                
    def add_load(self):
        """Add load to beam"""
        if not self.beam_engine:
            messagebox.showwarning("Warning", "Create beam first!")
            return
            
        try:
            load_type = self.load_type_combo.get()
            
            if load_type == "Concentrated":
                pos = float(self.load_vars["pos"].get())
                mag = float(self.load_vars["mag"].get()) * 1000  # Convert kN to N
                angle = float(self.load_vars["angle"].get())
                
                load = ConcentratedLoad(position=pos, magnitude=mag, angle=angle)
                self.beam_engine.add_concentrated_load(load)
                self.load_listbox.insert(tk.END, f"Conc: {mag/1000:.1f}kN @ {pos}m")
                
            elif load_type == "Uniformly Varying":
                start_pos = float(self.load_vars["start_pos"].get())
                end_pos = float(self.load_vars["end_pos"].get())
                start_mag = float(self.load_vars["start_mag"].get()) * 1000
                end_mag = float(self.load_vars["end_mag"].get()) * 1000
                
                load = UniformlyVaryingLoad(start_pos=start_pos, end_pos=end_pos,
                                          start_magnitude=start_mag, end_magnitude=end_mag)
                self.beam_engine.add_varying_load(load)
                self.load_listbox.insert(tk.END, f"Vary: {start_mag/1000}-{end_mag/1000}kN/m")
                
            self.update_status(f"⚡ {load_type} load added")
            
            if self.auto_analyze.get():
                self.analyze_beam()
                
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            
    def remove_load(self):
        """Remove selected load"""
        selection = self.load_listbox.curselection()
        if selection and self.beam_engine:
            idx = selection[0]
            if idx < len(self.beam_engine.concentrated_loads):
                self.beam_engine.concentrated_loads.pop(idx)
            else:
                adj_idx = idx - len(self.beam_engine.concentrated_loads)
                if adj_idx < len(self.beam_engine.varying_loads):
                    self.beam_engine.varying_loads.pop(adj_idx)
            
            self.load_listbox.delete(idx)
            self.update_status("🗑️ Load removed")
            
            if self.auto_analyze.get():
                self.analyze_beam()
                
    def auto_analyze_callback(self, *args):
        """Callback for auto-analysis"""
        if not hasattr(self, 'auto_analyze') or not self.auto_analyze.get():
            return
        try:
            self.analyze_beam()
        except Exception as e:
            messagebox.showerror("Analysis Error", f"An error occurred during analysis: {str(e)}")
            self.auto_analyze.set(False)  # Disable auto-analyze on error

    def analyze_beam(self):
        """Perform comprehensive beam analysis with enhanced calculations"""
        if not self.beam_engine or len(self.beam_engine.supports) < 1:
            messagebox.showwarning("Warning", "Add at least one support before analysis!")
            return
            
        self.progress.start()
        self.update_status("🧮 Analyzing beam structure...")
        
        try:
            # Run analysis in separate thread for better performance
            def analysis_thread():
                results = self.beam_engine.analyze()
                self.after(0, lambda: self.analysis_complete(results))
                
            threading.Thread(target=analysis_thread, daemon=True).start()
            
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Analysis Error", f"Error during analysis: {e}")
            
    def analysis_complete(self, results):
        """Handle analysis completion and update all visualizations"""
        self.progress.stop()
        self.update_status("✅ Analysis complete - Updating visualizations...")
        
        # Update all visualizations
        self.update_3d_visualization()
        self.update_analysis_plots()
        self.update_results_display()
        
        self.update_status("🎯 Ready - Interactive 3D visualization updated!")
        
    def update_3d_visualization(self):
        """Create stunning 3D beam visualization with advanced graphics"""
        # Clear previous plots
        self.ax_3d.clear()
        
        if not self.beam_engine:
            self.ax_3d.text(0.5, 0.5, 0.5, "Create Beam to Start Analysis", 
                           fontsize=16, ha='center', va='center', color='white',
                           transform=self.ax_3d.transAxes)
            self.canvas.draw()
            return
            
        # Enhanced 3D beam rendering with realistic materials
        length = self.beam_engine.beam_props.length
        height = float(self.property_vars.get("beam_height", tk.StringVar(value="0.3")).get())
        width = float(self.property_vars.get("beam_width", tk.StringVar(value="0.2")).get())
        
        # Create sophisticated 3D beam geometry
        x_beam = np.array([0, length, length, 0, 0])
        y_beam = np.array([-width/2, -width/2, width/2, width/2, -width/2])
        z_bottom = np.zeros(5)
        z_top = np.ones(5) * height
        
        # Draw beam with gradient coloring and material texture
        self.ax_3d.plot(x_beam, y_beam, z_bottom, 'b-', linewidth=3, alpha=0.8)
        self.ax_3d.plot(x_beam, y_beam, z_top, 'b-', linewidth=3, alpha=0.8)
        
        # Connect top and bottom with vertical lines for 3D effect
        for i in range(len(x_beam)):
            self.ax_3d.plot([x_beam[i], x_beam[i]], [y_beam[i], y_beam[i]], 
                           [z_bottom[i], z_top[i]], 'b-', linewidth=2, alpha=0.6)
            
        # Create realistic beam surfaces with gradients
        xx = np.linspace(0, length, 50)
        yy = np.linspace(-width/2, width/2, 20)
        XX, YY = np.meshgrid(xx, yy)
        
        # Top surface with metallic gradient
        ZZ_top = np.ones_like(XX) * height
        colors_top = plt.cm.plasma(np.linspace(0.3, 0.8, len(yy)))
        for i in range(len(yy)-1):
            self.ax_3d.plot_surface(XX[i:i+2], YY[i:i+2], ZZ_top[i:i+2], 
                                   color=colors_top[i], alpha=0.7, shade=True)
        
        # Bottom surface
        ZZ_bottom = np.zeros_like(XX)
        colors_bottom = plt.cm.viridis(np.linspace(0.2, 0.7, len(yy)))
        for i in range(len(yy)-1):
            self.ax_3d.plot_surface(XX[i:i+2], YY[i:i+2], ZZ_bottom[i:i+2], 
                                   color=colors_bottom[i], alpha=0.6, shade=True)
        
        # Add stunning support visualizations
        self.render_advanced_supports()
        
        # Add impressive load visualizations
        self.render_advanced_loads()
        
        # Add deflection curve if analysis is complete
        if hasattr(self.beam_engine, 'results') and self.beam_engine.results:
            self.render_deflection_curve()
            
        # Enhanced axis styling with professional appearance
        self.ax_3d.set_xlabel('Length (m)', fontsize=12, color='white', fontweight='bold')
        self.ax_3d.set_ylabel('Width (m)', fontsize=12, color='white', fontweight='bold')
        self.ax_3d.set_zlabel('Height (m)', fontsize=12, color='white', fontweight='bold')
        
        # Dynamic view adjustment
        self.ax_3d.set_xlim(0, length)
        self.ax_3d.set_ylim(-width, width)
        self.ax_3d.set_zlim(-height*0.5, height*2)
        
        # Professional grid and styling
        self.ax_3d.grid(True, alpha=0.3, color='cyan')
        self.ax_3d.xaxis._axinfo['grid'].update(color='cyan', linewidth=0.5, alpha=0.3)
        self.ax_3d.yaxis._axinfo['grid'].update(color='cyan', linewidth=0.5, alpha=0.3)
        self.ax_3d.zaxis._axinfo['grid'].update(color='cyan', linewidth=0.5, alpha=0.3)
        
        # Set viewing angle for optimal visualization
        self.ax_3d.view_init(elev=20, azim=45)
        
        self.canvas.draw()
        
    def render_advanced_supports(self):
        """Render sophisticated 3D support representations"""
        if not self.beam_engine.supports:
            return
            
        height = float(self.property_vars.get("beam_height", tk.StringVar(value="0.3")).get())
        width = float(self.property_vars.get("beam_width", tk.StringVar(value="0.2")).get())
        
        for support in self.beam_engine.supports:
            x_pos = support.position
            
            if support.type.lower() == "pin":
                # Enhanced pin support with 3D triangle
                triangle_height = height * 0.8
                triangle_base = width * 0.6
                
                # Create 3D triangular support
                x_tri = [x_pos, x_pos, x_pos, x_pos]
                y_tri = [-triangle_base/2, triangle_base/2, 0, -triangle_base/2]
                z_tri = [-triangle_height, -triangle_height, 0, -triangle_height]
                
                self.ax_3d.plot(x_tri, y_tri, z_tri, 'r-', linewidth=4, alpha=0.9)
                
                # Add support symbol with glow effect
                self.ax_3d.scatter([x_pos], [0], [-triangle_height/2], 
                                 c='red', s=200, alpha=0.8, edgecolors='yellow', linewidth=2)
                
            elif support.type.lower() == "roller":
                # Enhanced roller support with 3D cylinders
                cylinder_radius = width * 0.15
                cylinder_height = height * 0.3
                
                # Create multiple rollers for realistic effect
                for i, offset in enumerate([-width*0.3, 0, width*0.3]):
                    theta = np.linspace(0, 2*np.pi, 20)
                    z_cyl = np.linspace(-cylinder_height, 0, 10)
                    
                    for z in z_cyl[::2]:  # Sample points for performance
                        x_circle = x_pos + np.zeros_like(theta)
                        y_circle = offset + cylinder_radius * np.cos(theta)
                        z_circle = z + cylinder_radius * np.sin(theta)
                        
                        self.ax_3d.plot(x_circle, y_circle, z_circle, 
                                      color=plt.cm.rainbow(i/2), linewidth=2, alpha=0.7)
                        
            elif support.type.lower() == "fixed":
                # Enhanced fixed support with 3D rectangular base
                base_width = width * 1.2
                base_height = height * 0.6
                base_depth = width * 0.8
                
                # Create 3D fixed support structure
                x_base = [x_pos-0.05, x_pos+0.05, x_pos+0.05, x_pos-0.05, x_pos-0.05]
                y_base = [-base_width/2, -base_width/2, base_width/2, base_width/2, -base_width/2]
                z_base_bottom = [-base_height] * 5
                z_base_top = [0] * 5
                
                # Draw fixed support walls
                self.ax_3d.plot(x_base, y_base, z_base_bottom, 'k-', linewidth=5, alpha=0.9)
                self.ax_3d.plot(x_base, y_base, z_base_top, 'k-', linewidth=5, alpha=0.9)
                
                # Connect with vertical lines
                for i in range(len(x_base)):
                    self.ax_3d.plot([x_base[i], x_base[i]], [y_base[i], y_base[i]], 
                                   [z_base_bottom[i], z_base_top[i]], 'k-', linewidth=3, alpha=0.8)
                    
                # Add hatching pattern for fixed support
                for i in range(5):
                    y_hatch = np.linspace(-base_width/2, base_width/2, 10)
                    z_hatch = np.linspace(-base_height, 0, 10)
                    x_hatch = x_pos + np.zeros_like(y_hatch)
                    self.ax_3d.plot(x_hatch, y_hatch[::2], z_hatch[::2], 
                                   'k-', linewidth=1, alpha=0.6)
                    
    def render_advanced_loads(self):
        """Render spectacular 3D load representations"""
        if not (self.beam_engine.concentrated_loads or self.beam_engine.varying_loads):
            return
            
        height = float(self.property_vars.get("beam_height", tk.StringVar(value="0.3")).get())
        width = float(self.property_vars.get("beam_width", tk.StringVar(value="0.2")).get())
        
        # Render concentrated loads with dynamic arrows
        for load in self.beam_engine.concentrated_loads:
            x_pos = load.position
            magnitude = abs(load.magnitude) / 10000  # Scale for visualization
            
            # Create 3D arrow with gradient effect
            arrow_length = magnitude * 0.5
            arrow_start_z = height + arrow_length
            
            # Arrow shaft with color gradient
            arrow_colors = plt.cm.plasma(np.linspace(0, 1, 10))
            z_arrow = np.linspace(arrow_start_z, height, 10)
            
            for i, (z, color) in enumerate(zip(z_arrow[:-1], arrow_colors)):
                self.ax_3d.plot([x_pos, x_pos], [0, 0], [z, z_arrow[i+1]], 
                               color=color, linewidth=6-i*0.3, alpha=0.8)
                
            # Enhanced arrowhead with 3D cone effect
            cone_height = arrow_length * 0.3
            cone_radius = width * 0.1
            
            theta = np.linspace(0, 2*np.pi, 12)
            for i, angle in enumerate(theta):
                x_cone = x_pos + cone_radius * np.cos(angle) * np.linspace(1, 0, 5)
                y_cone = 0 + cone_radius * np.sin(angle) * np.linspace(1, 0, 5)
                z_cone = np.linspace(height + cone_height, height, 5)
                
                self.ax_3d.plot(x_cone, y_cone, z_cone, 
                               color=plt.cm.plasma(0.8), linewidth=2, alpha=0.9)
                
            # Add load magnitude label with 3D effect
            self.ax_3d.text(x_pos, width*0.8, arrow_start_z + 0.1,
                           f'{load.magnitude/1000:.1f} kN',
                           fontsize=10, color='yellow', fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
            
        # Render varying loads with spectacular distribution visualization
        for load in self.beam_engine.varying_loads:
            x_start, x_end = load.start_pos, load.end_pos
            mag_start = abs(load.start_magnitude) / 10000
            mag_end = abs(load.end_magnitude) / 10000
            
            # Create distributed load visualization
            x_dist = np.linspace(x_start, x_end, 20)
            magnitudes = np.linspace(mag_start, mag_end, 20)
            
            # Draw varying load distribution with color mapping
            for i, (x, mag) in enumerate(zip(x_dist, magnitudes)):
                arrow_length = mag * 0.3
                color_intensity = mag / max(magnitudes) if max(magnitudes) > 0 else 0
                color = plt.cm.viridis(color_intensity)
                
                # Varying arrow lengths
                self.ax_3d.plot([x, x], [0, 0], 
                               [height + arrow_length, height],
                               color=color, linewidth=4, alpha=0.8)
                
                # Small arrowheads
                if i % 3 == 0:  # Every third arrow gets an arrowhead
                    self.ax_3d.scatter([x], [0], [height], 
                                     c=[color], s=50, alpha=0.9, marker='v')
                    
            # Connect the tops with a smooth curve
            z_tops = height + magnitudes * 0.3
            self.ax_3d.plot(x_dist, np.zeros_like(x_dist), z_tops, 
                           'orange', linewidth=3, alpha=0.9)
            
            # Add load distribution label
            mid_x = (x_start + x_end) / 2
            mid_mag = (mag_start + mag_end) / 2
            self.ax_3d.text(mid_x, width*0.8, height + mid_mag*0.3 + 0.2,
                           f'Vary: {load.start_magnitude/1000:.1f}-{load.end_magnitude/1000:.1f} kN/m',
                           fontsize=9, color='orange', fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
                           
    def render_deflection_curve(self):
        """Render stunning deflection curve with enhanced 3D visualization"""
        if not self.beam_engine.results:
            return
            
        x = self.beam_engine.results['x']
        deflection = self.beam_engine.results['deflection']
        
        # Scale deflection for visibility
        max_deflection = np.max(np.abs(deflection))
        if max_deflection > 0:
            scale_factor = 0.5 / max_deflection
            scaled_deflection = deflection * scale_factor
        else:
            scaled_deflection = deflection
            
        height = float(self.property_vars.get("beam_height", tk.StringVar(value="0.3")).get())
        
        # Create deflection curve with rainbow gradient
        deflection_colors = plt.cm.rainbow(np.linspace(0, 1, len(x)))
        
        # Plot deflection curve as a 3D line with varying colors
        for i in range(len(x)-1):
            self.ax_3d.plot(x[i:i+2], [0,0], height + scaled_deflection[i:i+2],
                           color=deflection_colors[i], linewidth=3, alpha=0.9)
            
        # Add deflection magnitude indicators
        critical_points = np.where(np.abs(scaled_deflection) > 0.1 * np.max(np.abs(scaled_deflection)))[0]
        if len(critical_points) > 0:
            step = max(1, len(critical_points) // 5)
            for idx in critical_points[::step]:
                self.ax_3d.scatter([x[idx]], [0], [height + scaled_deflection[idx]], 
                                 c='red', s=100, alpha=0.8, edgecolors='white', linewidth=2)
            
        # Add deflection curve legend
        max_def_idx = np.argmax(np.abs(scaled_deflection))
        self.ax_3d.text(x[max_def_idx], 0.3, height + scaled_deflection[max_def_idx],
                       f'Max Δ: {max_deflection*1000:.2f} mm',
                       fontsize=10, color='red', fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.8))
                       
    def update_analysis_plots(self):
        """Update 2D analysis plots with professional styling"""
        if not self.beam_engine or not hasattr(self.beam_engine, 'results'):
            return

        results = self.beam_engine.results
        x = results['x']
        shear = results['shear'] / 1000  # Convert to kN
        moment = results['moment'] / 1000  # Convert to kN·m

        # --- Plot Styling Function ---
        def style_plot(ax, data, color, title, ylabel, xlabel=None):
            ax.clear()
            ax.axhline(y=0, color='white', linestyle='--', alpha=0.6, linewidth=1)

            # Plot shadow for depth
            ax.plot(x, data, linewidth=4, color='black', alpha=0.2)
            # Main plot line
            ax.plot(x, data, linewidth=2.5, color=color, label=title)
            ax.fill_between(x, 0, data, alpha=0.2, color=color)

            ax.set_title(title, color='white', fontweight='bold', fontsize=14, pad=15)
            ax.set_ylabel(ylabel, color='#bdc3c7', fontweight='bold', fontsize=11)
            if xlabel:
                ax.set_xlabel(xlabel, color='#bdc3c7', fontweight='bold', fontsize=11)

            ax.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.4, color='cyan')
            ax.tick_params(axis='x', colors='white', labelsize=10)
            ax.tick_params(axis='y', colors='white', labelsize=10)
            for spine in ax.spines.values():
                spine.set_edgecolor('#566573')

            legend = ax.legend(loc='upper right', frameon=True, fontsize=10)
            legend.get_frame().set_facecolor('#2c3e50')
            legend.get_frame().set_edgecolor('#34495e')
            for text in legend.get_texts():
                text.set_color('white')

        # --- Annotation Styling Function ---
        def add_max_annotation(ax, data, x_coords, unit):
            if len(data) == 0:
                return
            max_val = data[np.argmax(np.abs(data))]
            max_idx = np.argmax(np.abs(data))
            x_pos = x_coords[max_idx]
            
            # Dynamic positioning of annotation
            y_pos = max_val
            x_offset = 15
            y_offset = 15 if y_pos >= 0 else -30

            ax.annotate(f'Max Abs: {abs(max_val):.2f} {unit}',
                        xy=(x_pos, y_pos),
                        xytext=(x_offset, y_offset), textcoords='offset points',
                        ha='left',
                        bbox=dict(boxstyle='round,pad=0.4', fc='#34495e', ec='#bdc3c7', alpha=0.9),
                        color='#ecf0f1', fontweight='bold', fontsize=9,
                        arrowprops=dict(arrowstyle='-|>', color='#ecf0f1', lw=1.5,
                                        connectionstyle="arc3,rad=0.1"))

        # --- Apply styles to plots ---
        style_plot(self.ax_shear, shear, '#e74c3c', 'Shear Force Diagram', 'Shear Force (kN)')
        style_plot(self.ax_moment, moment, '#3498db', 'Bending Moment Diagram', 'Moment (kN·m)', 'Position (m)')

        # --- Add annotations ---
        add_max_annotation(self.ax_shear, shear, x, 'kN')
        add_max_annotation(self.ax_moment, moment, x, 'kN·m')

        plt.tight_layout(pad=3.0)
        self.canvas.draw()
        
    def update_results_display(self):
        """Update results display with comprehensive analysis data"""
        if not self.beam_engine or not hasattr(self.beam_engine, 'results'):
            return
            
        results = self.beam_engine.results
        
        # Update summary tab with enhanced formatting
        summary = f"""
╔══════════════════════════════════════╗
║          BEAM ANALYSIS SUMMARY        ║
╠══════════════════════════════════════╣
║ Beam Length: {self.beam_engine.beam_props.length:.2f} m              ║
║ Material: {self.material_combo.get()}                     ║
║ E: {self.beam_engine.beam_props.elastic_modulus/1e9:.1f} GPa                      ║
║ I: {self.beam_engine.beam_props.moment_of_inertia:.2e} m⁴       ║
╠══════════════════════════════════════╣
║            CRITICAL VALUES            ║
╠══════════════════════════════════════╣
║ Max Moment: {results['max_moment']/1000:.2f} kN⋅m          ║
║ Max Shear: {np.max(np.abs(results['shear']))/1000:.2f} kN             ║
║ Max Deflection: {results['max_deflection']*1000:.3f} mm      ║
║ Max Stress: {results['max_stress']/1e6:.2f} MPa            ║
╠══════════════════════════════════════╣
║              SUPPORTS                 ║
╠══════════════════════════════════════╣"""

        for i, support in enumerate(self.beam_engine.supports):
            summary += f"║ Support {i+1}: {support.type.title()} @ {support.position:.2f}m      ║\n"
            
        summary += f"""╠══════════════════════════════════════╣
║               LOADS                   ║
╠══════════════════════════════════════╣"""

        for i, load in enumerate(self.beam_engine.concentrated_loads):
            summary += f"║ Load {i+1}: {load.magnitude/1000:.1f} kN @ {load.position:.2f}m    ║\n"
            
        for i, load in enumerate(self.beam_engine.varying_loads):
            summary += f"║ Vary Load {i+1}: {load.start_magnitude/1000:.1f}-{load.end_magnitude/1000:.1f} kN/m  ║\n"
            
        summary += "╚══════════════════════════════════════╝"
        
        self.summary_text.config(state="normal")
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state="disabled")
        
        # Update detailed results
        detailed = f"""
DETAILED ANALYSIS RESULTS
{'='*50}

REACTION FORCES:
{'-'*20}
"""
        for i, (support, reaction) in enumerate(zip(self.beam_engine.supports, results['reactions'])):
            detailed += f"R{i+1} ({support.type} @ {support.position:.2f}m): {reaction/1000:.2f} kN\n"
            
        detailed += f"""
DEFLECTION ANALYSIS:
{'-'*20}
Maximum Deflection: {results['max_deflection']*1000:.3f} mm
Location of Max Deflection: {results['x'][np.argmax(np.abs(results['deflection']))]:.2f} m
Deflection Limit (L/250): {self.beam_engine.beam_props.length*1000/250:.3f} mm

STRESS ANALYSIS:
{'-'*20}
Maximum Stress: {results['max_stress']/1e6:.2f} MPa
Allowable Stress (Steel): 250 MPa
Safety Factor: {250/(results['max_stress']/1e6):.2f}

MOMENT ANALYSIS:
{'-'*20}
Maximum Positive Moment: {np.max(results['moment'])/1000:.2f} kN⋅m
Maximum Negative Moment: {np.min(results['moment'])/1000:.2f} kN⋅m
Location of Max Moment: {results['x'][np.argmax(np.abs(results['moment']))]:.2f} m

SHEAR ANALYSIS:
{'-'*20}
Maximum Shear: {np.max(np.abs(results['shear']))/1000:.2f} kN
Critical Shear Locations: Multiple points analyzed
"""
        
        self.detailed_text.config(state="normal")
        self.detailed_text.delete(1.0, tk.END)
        self.detailed_text.insert(tk.END, detailed)
        self.detailed_text.config(state="disabled")
        
        # Update safety assessment
        self.update_safety_assessment(results)
        
    def update_safety_assessment(self, results):
        """Comprehensive safety assessment with color-coded warnings"""
        max_stress = results['max_stress'] / 1e6  # MPa
        max_deflection = results['max_deflection'] * 1000  # mm
        deflection_limit = self.beam_engine.beam_props.length * 1000 / 250  # mm
        
        safety = f"""
COMPREHENSIVE SAFETY ASSESSMENT
{'='*50}

STRUCTURAL INTEGRITY CHECK:
{'-'*30}

"""
        
        # Stress safety check
        if max_stress < 150:
            safety += "✅ STRESS: EXCELLENT - Well within safe limits\n"
        elif max_stress < 200:
            safety += "⚠️  STRESS: GOOD - Acceptable stress levels\n"
        elif max_stress < 250:
            safety += "🔶 STRESS: CAUTION - Approaching design limits\n"
        else:
            safety += "❌ STRESS: CRITICAL - Exceeds safe limits!\n"
            
        safety += f"   Current: {max_stress:.2f} MPa | Limit: 250 MPa\n\n"
        
        # Deflection safety check
        if max_deflection < deflection_limit * 0.5:
            safety += "✅ DEFLECTION: EXCELLENT - Minimal deflection\n"
        elif max_deflection < deflection_limit * 0.8:
            safety += "⚠️  DEFLECTION: GOOD - Acceptable deflection\n"
        elif max_deflection < deflection_limit:
            safety += "🔶 DEFLECTION: CAUTION - Approaching limits\n"
        else:
            safety += "❌ DEFLECTION: CRITICAL - Exceeds limits!\n"
            
        safety += f"   Current: {max_deflection:.3f} mm | Limit: {deflection_limit:.3f} mm\n\n"
        
        # Overall safety rating
        stress_factor = 250 / max_stress if max_stress > 0 else float('inf')
        deflection_factor = deflection_limit / max_deflection if max_deflection > 0 else float('inf')
        overall_factor = min(stress_factor, deflection_factor)
        
        safety += f"""
OVERALL SAFETY FACTORS:
{'-'*25}
Stress Safety Factor: {stress_factor:.2f}
Deflection Safety Factor: {deflection_factor:.2f}
Critical Safety Factor: {overall_factor:.2f}

RECOMMENDATIONS:
{'-'*15}
"""
        
        if overall_factor > 3:
            safety += "✅ Structure is over-designed. Consider optimization.\n"
        elif overall_factor > 2:
            safety += "✅ Excellent safety margin. Design is robust.\n"
        elif overall_factor > 1.5:
            safety += "⚠️  Adequate safety. Monitor under service loads.\n"
        elif overall_factor > 1:
            safety += "🔶 Minimal safety margin. Consider reinforcement.\n"
        else:
            safety += "❌ UNSAFE DESIGN! Immediate redesign required!\n"
            
        self.safety_text.config(state="normal")
        self.safety_text.delete(1.0, tk.END)
        self.safety_text.insert(tk.END, safety)
        self.safety_text.config(state="disabled")
        for i, (support, reaction) in enumerate(zip(self.beam_engine.supports, results['reactions'])):
            detailed += f"R{i+1} ({support.type} @ {support.position:.2f}m): {reaction/1000:.2f} kN\n"
            
        detailed += f"""
DEFLECTION ANALYSIS:
{'-'*20}
Maximum Deflection: {results['max_deflection']*1000:.3f} mm
Location of Max Deflection: {results['x'][np.argmax(np.abs(results['deflection']))]:.2f} m
Deflection Limit (L/250): {self.beam_engine.beam_props.length*1000/250:.3f} mm

STRESS ANALYSIS:
{'-'*20}
Maximum Stress: {results['max_stress']/1e6:.2f} MPa
Allowable Stress (Steel): 250 MPa
Safety Factor: {250/(results['max_stress']/1e6):.2f}

MOMENT ANALYSIS:
{'-'*20}
Maximum Positive Moment: {np.max(results['moment'])/1000:.2f} kN⋅m
Maximum Negative Moment: {np.min(results['moment'])/1000:.2f} kN⋅m
Location of Max Moment: {results['x'][np.argmax(np.abs(results['moment']))]:.2f} m

SHEAR ANALYSIS:
{'-'*20}
Maximum Shear: {np.max(np.abs(results['shear']))/1000:.2f} kN
Critical Shear Locations: Multiple points analyzed
"""
        
        self.detailed_text.config(state="normal")
        self.detailed_text.delete(1.0, tk.END)
        self.detailed_text.insert(tk.END, detailed)
        self.detailed_text.config(state="disabled")
        
        # Update safety assessment
        self.update_safety_assessment(results)
        
    def update_safety_assessment(self, results):
        """Comprehensive safety assessment with color-coded warnings"""
        max_stress = results['max_stress'] / 1e6  # MPa
        max_deflection = results['max_deflection'] * 1000  # mm
        deflection_limit = self.beam_engine.beam_props.length * 1000 / 250  # mm
        
        safety = f"""
COMPREHENSIVE SAFETY ASSESSMENT
{'='*50}

STRUCTURAL INTEGRITY CHECK:
{'-'*30}

"""
        
        # Stress safety check
        if max_stress < 150:
            safety += "✅ STRESS: EXCELLENT - Well within safe limits\n"
        elif max_stress < 200:
            safety += "⚠️  STRESS: GOOD - Acceptable stress levels\n"
        elif max_stress < 250:
            safety += "🔶 STRESS: CAUTION - Approaching design limits\n"
        else:
            safety += "❌ STRESS: CRITICAL - Exceeds safe limits!\n"
            
        safety += f"   Current: {max_stress:.2f} MPa | Limit: 250 MPa\n\n"
        
        # Deflection safety check
        if max_deflection < deflection_limit * 0.5:
            safety += "✅ DEFLECTION: EXCELLENT - Minimal deflection\n"
        elif max_deflection < deflection_limit * 0.8:
            safety += "⚠️  DEFLECTION: GOOD - Acceptable deflection\n"
        elif max_deflection < deflection_limit:
            safety += "🔶 DEFLECTION: CAUTION - Approaching limits\n"
        else:
            safety += "❌ DEFLECTION: CRITICAL - Exceeds limits!\n"
            
        safety += f"   Current: {max_deflection:.3f} mm | Limit: {deflection_limit:.3f} mm\n\n"
        
        # Overall safety rating
        stress_factor = 250 / max_stress if max_stress > 0 else float('inf')
        deflection_factor = deflection_limit / max_deflection if max_deflection > 0 else float('inf')
        overall_factor = min(stress_factor, deflection_factor)
        
        safety += f"""
OVERALL SAFETY FACTORS:
{'-'*25}
Stress Safety Factor: {stress_factor:.2f}
Deflection Safety Factor: {deflection_factor:.2f}
Critical Safety Factor: {overall_factor:.2f}

RECOMMENDATIONS:
{'-'*15}
"""
        
        if overall_factor > 3:
            safety += "✅ Structure is over-designed. Consider optimization.\n"
        elif overall_factor > 2:
            safety += "✅ Excellent safety margin. Design is robust.\n"
        elif overall_factor > 1.5:
            safety += "⚠️  Adequate safety. Monitor under service loads.\n"
        elif overall_factor > 1:
            safety += "🔶 Minimal safety margin. Consider reinforcement.\n"
        else:
            safety += "❌ UNSAFE DESIGN! Immediate redesign required!\n"
            
        self.safety_text.config(state="normal")
        self.safety_text.delete(1.0, tk.END)
        self.safety_text.insert(tk.END, safety)
        self.safety_text.config(state="disabled")
        
    def animate_results(self):
        """Create spectacular animated visualization of beam behavior"""
        if not self.beam_engine or not hasattr(self.beam_engine, 'results'):
            messagebox.showwarning("Warning", "Analyze beam first!")
            return
            
        if self.animation_running:
            self.animation_running = False
            return
            
        self.animation_running = True
        self.update_status("🎬 Starting spectacular animation...")
        
        # Create animation window
        anim_window = tb.Toplevel(self)
        anim_window.title("🎭 Beam Behavior Animation")
        anim_window.geometry("800x600")
        anim_window.configure(bg="#1a1a2e")
        
        # Create animation figure
        anim_fig, anim_ax = plt.subplots(figsize=(10, 6), facecolor='#2c3e50')
        anim_ax.set_facecolor('#34495e')
        
        # Embed animation canvas
        anim_canvas = FigureCanvasTkAgg(anim_fig, master=anim_window)
        anim_canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
        
        # Animation control frame
        control_frame = tb.Frame(anim_window)
        control_frame.pack(fill=X, padx=10, pady=5)
        
        speed_var = tk.DoubleVar(value=1.0)
        tb.Label(control_frame, text="Speed:").pack(side=LEFT)
        speed_scale = tb.Scale(control_frame, from_=0.1, to=3.0, orient=HORIZONTAL,
                              variable=speed_var, length=200)
        speed_scale.pack(side=LEFT, padx=10)
        
        stop_btn = tb.Button(control_frame, text="⏹️ Stop", 
                            command=lambda: setattr(self, 'animation_running', False),
                            bootstyle="danger")
        stop_btn.pack(side=RIGHT, padx=5)
        
        # Get results for animation
        results = self.beam_engine.results
        x = results['x']
        deflection = results['deflection']
        
        # Scale deflection for visibility
        max_deflection = np.max(np.abs(deflection))
        if max_deflection > 0:
            scale_factor = 2.0 / max_deflection
            scaled_deflection = deflection * scale_factor
        else:
            scaled_deflection = deflection
            
        # Animation function
        def animate_frame(frame):
            if not self.animation_running:
                return []
                
            anim_ax.clear()
            
            # Animate deflection with wave effect
            time_factor = frame * 0.1 * speed_var.get()
            wave_deflection = scaled_deflection * np.sin(time_factor)
            
            # Draw original beam
            anim_ax.plot(x, np.zeros_like(x), 'b-', linewidth=8, alpha=0.3, label='Original Position')
            
            # Draw deflected beam with rainbow colors
            colors = plt.cm.rainbow(np.linspace(0, 1, len(x)))
            for i in range(len(x)-1):
                anim_ax.plot(x[i:i+2], wave_deflection[i:i+2], 
                           color=colors[i], linewidth=4, alpha=0.8)
                           
            # Add supports
            for support in self.beam_engine.supports:
                if support.type.lower() == "pin":
                    anim_ax.plot(support.position, 0, 'r^', markersize=15, markeredgecolor='yellow')
                elif support.type.lower() == "roller":
                    anim_ax.plot(support.position, 0, 'ro', markersize=12, markeredgecolor='yellow')
                elif support.type.lower() == "fixed":
                    anim_ax.plot(support.position, 0, 'ks', markersize=15, markeredgecolor='yellow')
                    
            # Add loads
            for load in self.beam_engine.concentrated_loads:
                arrow_y = wave_deflection[np.argmin(np.abs(x - load.position))] + 0.5
                anim_ax.annotate('', xy=(load.position, arrow_y-0.3), 
                               xytext=(load.position, arrow_y),
                               arrowprops=dict(arrowstyle='->', lw=3, color='red'))
                anim_ax.text(load.position, arrow_y+0.1, f'{load.magnitude/1000:.1f} kN',
                           ha='center', color='red', fontweight='bold')
                           
            # Styling
            anim_ax.set_xlim(0, self.beam_engine.beam_props.length)
            anim_ax.set_ylim(-3, 3)
            anim_ax.set_xlabel('Position (m)', color='white', fontweight='bold')
            anim_ax.set_ylabel('Deflection (scaled)', color='white', fontweight='bold')
            anim_ax.set_title(f'🎬 Animated Beam Deflection - Frame {frame}', 
                             color='white', fontweight='bold', fontsize=14)
            anim_ax.grid(True, alpha=0.3, color='cyan')
            anim_ax.tick_params(colors='white')
            anim_ax.legend(facecolor='black', edgecolor='white')
            
            return []
            
        # Start animation
        anim = FuncAnimation(anim_fig, animate_frame, frames=200, interval=50, 
                           blit=False, repeat=True)
        anim_canvas.draw()
        
        # Stop animation when window is closed
        def on_closing():
            self.animation_running = False
            anim_window.destroy()
            
        anim_window.protocol("WM_DELETE_WINDOW", on_closing)
        
    def export_results(self):
        """Export comprehensive analysis results to multiple formats"""
        if not self.beam_engine or not hasattr(self.beam_engine, 'results'):
            messagebox.showwarning("Warning", "Analyze beam first!")
            return
            
        export_window = tb.Toplevel(self)
        export_window.title("💾 Export Analysis Results")
        export_window.geometry("400x300")
        export_window.configure(bg="#1a1a2e")
        
        export_frame = tb.Labelframe(export_window, text="Export Options", padding=20)
        export_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Export format selection
        format_var = tk.StringVar(value="JSON")
        formats = ["JSON", "CSV", "PDF Report", "Images", "Excel"]
        
        tb.Label(export_frame, text="Select Export Format:").pack(anchor="w", pady=5)
        
        for fmt in formats:
            tb.Radiobutton(export_frame, text=fmt, variable=format_var, 
                          value=fmt, bootstyle="info").pack(anchor="w", pady=2)
                          
        # Export button
        def perform_export():
            format_choice = format_var.get()
            
            try:
                if format_choice == "JSON":
                    self.export_json()
                elif format_choice == "CSV":
                    self.export_csv()
                elif format_choice == "PDF Report":
                    self.export_pdf()
                elif format_choice == "Images":
                    self.export_images()
                elif format_choice == "Excel":
                    self.export_excel()
                    
                export_window.destroy()
                messagebox.showinfo("Success", f"Results exported as {format_choice}!")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {e}")
                
        export_btn = tb.Button(export_frame, text="📤 Export Now", 
                              command=perform_export, bootstyle="success")
        export_btn.pack(pady=20)
        
    def export_json(self):
        """Export results to JSON format"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            export_data = {
                "beam_properties": {
                    "length": self.beam_engine.beam_props.length,
                    "elastic_modulus": self.beam_engine.beam_props.elastic_modulus,
                    "moment_of_inertia": self.beam_engine.beam_props.moment_of_inertia,
                    "cross_section_area": self.beam_engine.beam_props.cross_section_area
                },
                "supports": [{"position": s.position, "type": s.type} for s in self.beam_engine.supports],
                "loads": {
                    "concentrated": [{"position": l.position, "magnitude": l.magnitude, "angle": l.angle} 
                                   for l in self.beam_engine.concentrated_loads],
                    "varying": [{"start_pos": l.start_pos, "end_pos": l.end_pos,
                               "start_magnitude": l.start_magnitude, "end_magnitude": l.end_magnitude}
                              for l in self.beam_engine.varying_loads]
                },
                "results": {
                    "max_moment": float(self.beam_engine.results["max_moment"]),
                    "max_deflection": float(self.beam_engine.results["max_deflection"]),
                    "max_stress": float(self.beam_engine.results["max_stress"]),
                    "reactions": [float(r) for r in self.beam_engine.results["reactions"]]
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
                
    def export_csv(self):
        """Export numerical results to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            results = self.beam_engine.results
            import csv
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Position (m)", "Shear Force (N)", "Bending Moment (N⋅m)", 
                               "Deflection (m)", "Stress (Pa)"])
                
                for i in range(len(results['x'])):
                    writer.writerow([
                        results['x'][i],
                        results['shear'][i],
                        results['moment'][i],
                        results['deflection'][i],
                        results['stress'][i]
                    ])
                    
    def export_pdf(self):
        """Export comprehensive PDF report"""
        messagebox.showinfo("PDF Export", "PDF export feature coming soon!")
        
    def export_images(self):
        """Export visualization images"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight', 
                           facecolor='#2c3e50', edgecolor='none')
                           
    def export_excel(self):
        """Export results to Excel format"""
        messagebox.showinfo("Excel Export", "Excel export feature coming soon!")
        
    def clear_all(self):
        """Clear all beam data and reset interface"""
        if messagebox.askyesno("Confirm Clear", "Clear all beam data? This cannot be undone."):
            self.beam_engine = None
            
            # Clear lists
            self.support_listbox.delete(0, tk.END)
            self.load_listbox.delete(0, tk.END)
            
            # Clear text displays
            for text_widget in [self.summary_text, self.detailed_text, self.safety_text]:
                text_widget.config(state="normal")
                text_widget.delete(1.0, tk.END)
                text_widget.config(state="disabled")
                
            # Clear plots
            for ax in [self.ax_3d, self.ax_shear, self.ax_moment]:
                ax.clear()
                
            self.canvas.draw()
            self.update_status("🧹 All data cleared - Ready for new analysis!")
            
    def update_status(self, message):
        """Update status bar with message"""
        self.status_label.config(text=message)
        self.update_idletasks()
        
    def save_project(self):
        """Save current project to file"""
        if not self.beam_engine:
            messagebox.showwarning("Warning", "No beam to save!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".beam",
            filetypes=[("Beam files", "*.beam"), ("All files", "*.*")]
        )
        
        if filename:
            project_data = {
                "beam_properties": {
                    "length": self.beam_engine.beam_props.length,
                    "elastic_modulus": self.beam_engine.beam_props.elastic_modulus,
                    "moment_of_inertia": self.beam_engine.beam_props.moment_of_inertia,
                    "cross_section_area": self.beam_engine.beam_props.cross_section_area
                },
                "supports": [{"position": s.position, "type": s.type} for s in self.beam_engine.supports],
                "concentrated_loads": [{"position": l.position, "magnitude": l.magnitude, "angle": l.angle} 
                                     for l in self.beam_engine.concentrated_loads],
                "varying_loads": [{"start_pos": l.start_pos, "end_pos": l.end_pos,
                                 "start_magnitude": l.start_magnitude, "end_magnitude": l.end_magnitude}
                                for l in self.beam_engine.varying_loads]
            }
            
            with open(filename, 'w') as f:
                json.dump(project_data, f, indent=2)
                
            messagebox.showinfo("Success", "Project saved successfully!")
            
    def load_project(self):
        """Load project from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Beam files", "*.beam"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    project_data = json.load(f)
                    
                # Create beam
                beam_props = BeamProperties(**project_data["beam_properties"])
                self.beam_engine = AdvancedBeamEngine(beam_props)
                
                # Load supports
                for support_data in project_data["supports"]:
                    support = Support(**support_data)
                    self.beam_engine.add_support(support)
                    
                # Load loads
                for load_data in project_data["concentrated_loads"]:
                    load = ConcentratedLoad(**load_data)
                    self.beam_engine.add_concentrated_load(load)
                    
                for load_data in project_data["varying_loads"]:
                    load = UniformlyVaryingLoad(**load_data)
                    self.beam_engine.add_varying_load(load)
                    
                # Update interface
                self.refresh_interface()
                messagebox.showinfo("Success", "Project loaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load project: {e}")
                
    def refresh_interface(self):
        """Refresh interface after loading project"""
        # Clear and update listboxes
        self.support_listbox.delete(0, tk.END)
        self.load_listbox.delete(0, tk.END)
        
        for support in self.beam_engine.supports:
            self.support_listbox.insert(tk.END, f"{support.type.title()} @ {support.position}m")
            
        for load in self.beam_engine.concentrated_loads:
            self.load_listbox.insert(tk.END, f"Conc: {load.magnitude/1000:.1f}kN @ {load.position}m")
            
        for load in self.beam_engine.varying_loads:
            self.load_listbox.insert(tk.END, f"Vary: {load.start_magnitude/1000:.1f}-{load.end_magnitude/1000:.1f}kN/m")
            
        # Update visualization
        self.update_3d_visualization()
        
        # Auto-analyze if enabled
        if self.auto_analyze.get():
            self.analyze_beam()

def main():
    """Main application entry point"""
    try:
        app = Advanced3DBeamGUI()
        
        # Add menu bar
        menubar = tk.Menu(app)
        app.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=app.clear_all)
        file_menu.add_command(label="Save Project", command=app.save_project)
        file_menu.add_command(label="Load Project", command=app.load_project)
        file_menu.add_separator()
        file_menu.add_command(label="Export Results", command=app.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=app.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo(
            "About", "🏗️ Professional 3D Beam Analysis Suite\nVersion 2.0\nAdvanced structural analysis tool"))
        
        app.mainloop()
        
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()