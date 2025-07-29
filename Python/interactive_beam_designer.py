#!/usr/bin/env python3
"""
3D Interactive Beam Designer
A comprehensive structural analysis tool for beam design and visualization
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import json
import os

class BeamDesigner:
    def __init__(self, root):
        self.root = root
        self.root.title("🏗️ 3D Interactive Beam Designer")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a1428')
        
        # Beam properties
        self.beam_length = 10.0
        self.supports = []
        self.loads = []
        self.analysis_results = None
        self.is_analyzing = False
        
        # Colors
        self.colors = {
            'bg': '#0a1428',
            'sidebar': '#001428',
            'accent': '#00ffaa',
            'secondary': '#66ccff',
            'text': '#ffffff',
            'button': '#00ffaa',
            'danger': '#ff4444'
        }
        
        self.setup_gui()
        self.create_beam()
        
    def setup_gui(self):
        """Initialize the GUI components"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.create_sidebar(main_frame)
        
        # Main content area
        self.create_main_content(main_frame)
        
    def create_sidebar(self, parent):
        """Create the control sidebar"""
        sidebar = tk.Frame(parent, bg=self.colors['sidebar'], width=350)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)
        sidebar.pack_propagate(False)
        
        # Title
        title_label = tk.Label(sidebar, text="🏗️ 3D Beam Designer", 
                              font=("Segoe UI", 18, "bold"),
                              fg=self.colors['accent'], bg=self.colors['sidebar'])
        title_label.pack(pady=20)
        
        # Beam Properties Section
        self.create_beam_properties_section(sidebar)
        
        # Support Section
        self.create_support_section(sidebar)
        
        # Load Section
        self.create_load_section(sidebar)
        
        # Analysis Section
        self.create_analysis_section(sidebar)
        
        # Configuration Display
        self.create_configuration_section(sidebar)
        
    def create_section_frame(self, parent, title):
        """Create a styled section frame"""
        frame = tk.LabelFrame(parent, text=title, font=("Segoe UI", 12, "bold"),
                             fg=self.colors['accent'], bg=self.colors['sidebar'],
                             bd=2, relief=tk.RAISED)
        frame.pack(fill=tk.X, padx=10, pady=5)
        return frame
        
    def create_beam_properties_section(self, parent):
        """Create beam properties controls"""
        frame = self.create_section_frame(parent, "📏 Beam Properties")
        
        tk.Label(frame, text="Length (m):", fg=self.colors['secondary'], 
                bg=self.colors['sidebar']).pack(anchor=tk.W, padx=5)
        
        self.length_var = tk.DoubleVar(value=10.0)
        length_entry = tk.Entry(frame, textvariable=self.length_var, width=15)
        length_entry.pack(padx=5, pady=2)
        
        create_btn = tk.Button(frame, text="Create Beam", bg=self.colors['button'],
                              fg='black', font=("Segoe UI", 10, "bold"),
                              command=self.create_beam)
        create_btn.pack(pady=5)
        
    def create_support_section(self, parent):
        """Create support controls"""
        frame = self.create_section_frame(parent, "🔧 Add Support")
        
        tk.Label(frame, text="Position (m):", fg=self.colors['secondary'], 
                bg=self.colors['sidebar']).pack(anchor=tk.W, padx=5)
        
        self.support_pos_var = tk.DoubleVar()
        pos_entry = tk.Entry(frame, textvariable=self.support_pos_var, width=15)
        pos_entry.pack(padx=5, pady=2)
        
        tk.Label(frame, text="Support Type:", fg=self.colors['secondary'], 
                bg=self.colors['sidebar']).pack(anchor=tk.W, padx=5)
        
        self.support_type_var = tk.StringVar(value="pin")
        support_combo = ttk.Combobox(frame, textvariable=self.support_type_var,
                                   values=["pin", "roller", "fixed"], width=12)
        support_combo.pack(padx=5, pady=2)
        
        add_support_btn = tk.Button(frame, text="Add Support", bg=self.colors['button'],
                                   fg='black', font=("Segoe UI", 10, "bold"),
                                   command=self.add_support)
        add_support_btn.pack(pady=5)
        
    def create_load_section(self, parent):
        """Create load controls"""
        frame = self.create_section_frame(parent, "⚡ Add Load")
        
        tk.Label(frame, text="Load Type:", fg=self.colors['secondary'], 
                bg=self.colors['sidebar']).pack(anchor=tk.W, padx=5)
        
        self.load_type_var = tk.StringVar(value="concentrated")
        load_combo = ttk.Combobox(frame, textvariable=self.load_type_var,
                                values=["concentrated", "distributed", "varying"], width=12)
        load_combo.pack(padx=5, pady=2)
        load_combo.bind('<<ComboboxSelected>>', self.update_load_inputs)
        
        # Load input frame
        self.load_input_frame = tk.Frame(frame, bg=self.colors['sidebar'])
        self.load_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.update_load_inputs()
        
        add_load_btn = tk.Button(frame, text="Add Load", bg=self.colors['button'],
                                fg='black', font=("Segoe UI", 10, "bold"),
                                command=self.add_load)
        add_load_btn.pack(pady=5)
        
    def update_load_inputs(self, event=None):
        """Update load input fields based on load type"""
        # Clear existing inputs
        for widget in self.load_input_frame.winfo_children():
            widget.destroy()
            
        load_type = self.load_type_var.get()
        
        if load_type == "concentrated":
            tk.Label(self.load_input_frame, text="Position (m):", 
                    fg=self.colors['secondary'], bg=self.colors['sidebar']).pack(anchor=tk.W)
            self.load_pos_var = tk.DoubleVar()
            tk.Entry(self.load_input_frame, textvariable=self.load_pos_var, width=15).pack(pady=2)
            
            tk.Label(self.load_input_frame, text="Magnitude (kN):", 
                    fg=self.colors['secondary'], bg=self.colors['sidebar']).pack(anchor=tk.W)
            self.load_mag_var = tk.DoubleVar()
            tk.Entry(self.load_input_frame, textvariable=self.load_mag_var, width=15).pack(pady=2)
            
        elif load_type == "distributed":
            tk.Label(self.load_input_frame, text="Start Position (m):", 
                    fg=self.colors['secondary'], bg=self.colors['sidebar']).pack(anchor=tk.W)
            self.load_start_var = tk.DoubleVar()
            tk.Entry(self.load_input_frame, textvariable=self.load_start_var, width=15).pack(pady=2)
            
            tk.Label(self.load_input_frame, text="End Position (m):", 
                    fg=self.colors['secondary'], bg=self.colors['sidebar']).pack(anchor=tk.W)
            self.load_end_var = tk.DoubleVar()
            tk.Entry(self.load_input_frame, textvariable=self.load_end_var, width=15).pack(pady=2)
            
            tk.Label(self.load_input_frame, text="Intensity (kN/m):", 
                    fg=self.colors['secondary'], bg=self.colors['sidebar']).pack(anchor=tk.W)
            self.load_intensity_var = tk.DoubleVar()
            tk.Entry(self.load_input_frame, textvariable=self.load_intensity_var, width=15).pack(pady=2)
            
        elif load_type == "varying":
            tk.Label(self.load_input_frame, text="Start Position (m):", 
                    fg=self.colors['secondary'], bg=self.colors['sidebar']).pack(anchor=tk.W)
            self.load_start_var = tk.DoubleVar()
            tk.Entry(self.load_input_frame, textvariable=self.load_start_var, width=15).pack(pady=2)
            
            tk.Label(self.load_input_frame, text="End Position (m):", 
                    fg=self.colors['secondary'], bg=self.colors['sidebar']).pack(anchor=tk.W)
            self.load_end_var = tk.DoubleVar()
            tk.Entry(self.load_input_frame, textvariable=self.load_end_var, width=15).pack(pady=2)
            
            tk.Label(self.load_input_frame, text="Start Intensity (kN/m):", 
                    fg=self.colors['secondary'], bg=self.colors['sidebar']).pack(anchor=tk.W)
            self.load_start_intensity_var = tk.DoubleVar()
            tk.Entry(self.load_input_frame, textvariable=self.load_start_intensity_var, width=15).pack(pady=2)
            
            tk.Label(self.load_input_frame, text="End Intensity (kN/m):", 
                    fg=self.colors['secondary'], bg=self.colors['sidebar']).pack(anchor=tk.W)
            self.load_end_intensity_var = tk.DoubleVar()
            tk.Entry(self.load_input_frame, textvariable=self.load_end_intensity_var, width=15).pack(pady=2)
    
    def create_analysis_section(self, parent):
        """Create analysis controls"""
        frame = self.create_section_frame(parent, "🔬 Analysis")
        
        analyze_btn = tk.Button(frame, text="Analyze Beam", bg=self.colors['button'],
                               fg='black', font=("Segoe UI", 10, "bold"),
                               command=self.analyze_beam)
        analyze_btn.pack(pady=5)
        
        clear_btn = tk.Button(frame, text="Clear All", bg=self.colors['danger'],
                             fg='white', font=("Segoe UI", 10, "bold"),
                             command=self.clear_all)
        clear_btn.pack(pady=2)
        
        # Results display
        self.results_text = tk.Text(frame, height=8, width=35, bg='#001122', 
                                   fg=self.colors['accent'], font=("Courier", 9))
        self.results_text.pack(padx=5, pady=5)
        
    def create_configuration_section(self, parent):
        """Create configuration display"""
        frame = self.create_section_frame(parent, "📋 Current Configuration")
        
        self.config_text = tk.Text(frame, height=6, width=35, bg='#001122', 
                                  fg=self.colors['secondary'], font=("Courier", 9))
        self.config_text.pack(padx=5, pady=5)
        
    def create_main_content(self, parent):
        """Create the main visualization area"""
        main_frame = tk.Frame(parent, bg=self.colors['bg'])
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(control_frame, text="🎮 Reset View", bg=self.colors['secondary'],
                 fg='black', command=self.reset_view).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="💾 Save Design", bg=self.colors['secondary'],
                 fg='black', command=self.save_design).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="📁 Load Design", bg=self.colors['secondary'],
                 fg='black', command=self.load_design).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="📈 Show Charts", bg=self.colors['button'],
                 fg='black', command=self.show_charts).pack(side=tk.RIGHT, padx=5)
        
        # Matplotlib figure for 3D visualization
        self.fig = Figure(figsize=(12, 8), facecolor='#0a1428')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#0a1428')
        
        self.canvas = FigureCanvasTkAgg(self.fig, main_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.setup_3d_plot()
        
    def setup_3d_plot(self):
        """Setup the 3D plot appearance"""
        self.ax.set_xlabel('Length (m)', color=self.colors['accent'])
        self.ax.set_ylabel('Width (m)', color=self.colors['accent'])
        self.ax.set_zlabel('Height (m)', color=self.colors['accent'])
        self.ax.tick_params(colors=self.colors['secondary'])
        
        # Set equal aspect ratio
        self.ax.set_box_aspect([3, 1, 1])
        
    def create_beam(self):
        """Create or update the beam visualization"""
        self.beam_length = self.length_var.get()
        self.update_visualization()
        self.update_config_display()
        
    def add_support(self):
        """Add a support to the beam"""
        position = self.support_pos_var.get()
        support_type = self.support_type_var.get()
        
        if position < 0 or position > self.beam_length:
            messagebox.showerror("Error", "Invalid support position!")
            return
            
        # Remove existing support at this position
        self.supports = [s for s in self.supports if abs(s['position'] - position) > 0.1]
        
        # Add new support
        self.supports.append({
            'position': position,
            'type': support_type
        })
        
        self.update_visualization()
        self.update_config_display()
        
    def add_load(self):
        """Add a load to the beam"""
        load_type = self.load_type_var.get()
        
        try:
            if load_type == "concentrated":
                position = self.load_pos_var.get()
                magnitude = self.load_mag_var.get()
                
                if position < 0 or position > self.beam_length:
                    raise ValueError("Invalid load position!")
                    
                self.loads.append({
                    'type': 'concentrated',
                    'position': position,
                    'magnitude': magnitude
                })
                
            elif load_type == "distributed":
                start_pos = self.load_start_var.get()
                end_pos = self.load_end_var.get()
                intensity = self.load_intensity_var.get()
                
                if start_pos >= end_pos or start_pos < 0 or end_pos > self.beam_length:
                    raise ValueError("Invalid load parameters!")
                    
                self.loads.append({
                    'type': 'distributed',
                    'start_pos': start_pos,
                    'end_pos': end_pos,
                    'intensity': intensity
                })
                
            elif load_type == "varying":
                start_pos = self.load_start_var.get()
                end_pos = self.load_end_var.get()
                start_intensity = self.load_start_intensity_var.get()
                end_intensity = self.load_end_intensity_var.get()
                
                if start_pos >= end_pos or start_pos < 0 or end_pos > self.beam_length:
                    raise ValueError("Invalid load parameters!")
                    
                self.loads.append({
                    'type': 'varying',
                    'start_pos': start_pos,
                    'end_pos': end_pos,
                    'start_intensity': start_intensity,
                    'end_intensity': end_intensity
                })
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        except tk.TclError:
            messagebox.showerror("Error", "Please enter valid numerical values!")
            return
            
        self.update_visualization()
        self.update_config_display()
        
    def analyze_beam(self):
        """Perform beam analysis"""
        if len(self.supports) < 2:
            messagebox.showerror("Error", "Please add at least 2 supports!")
            return
            
        if len(self.loads) == 0:
            messagebox.showerror("Error", "Please add at least one load!")
            return
            
        self.analysis_results = self.perform_analysis()
        self.display_results()
        
    def perform_analysis(self):
        """Simplified beam analysis"""
        # This is a simplified analysis - real structural analysis would be much more complex
        total_load = 0
        moment_sum = 0
        
        # Calculate total loads and moments
        for load in self.loads:
            if load['type'] == 'concentrated':
                total_load += load['magnitude']
                moment_sum += load['magnitude'] * load['position']
            elif load['type'] == 'distributed':
                length = load['end_pos'] - load['start_pos']
                load_magnitude = load['intensity'] * length
                total_load += load_magnitude
                center = (load['start_pos'] + load['end_pos']) / 2
                moment_sum += load_magnitude * center
            elif load['type'] == 'varying':
                length = load['end_pos'] - load['start_pos']
                avg_intensity = (load['start_intensity'] + load['end_intensity']) / 2
                load_magnitude = avg_intensity * length
                total_load += load_magnitude
                # For triangular/trapezoidal loads, centroid calculation is more complex
                center = (load['start_pos'] + load['end_pos']) / 2
                moment_sum += load_magnitude * center
        
        # Simple reaction calculation (assuming 2 supports for statically determinate beam)
        if len(self.supports) == 2:
            support_positions = [s['position'] for s in self.supports]
            L = abs(support_positions[1] - support_positions[0])
            
            # Reaction at second support
            R2 = moment_sum / L if L > 0 else 0
            # Reaction at first support
            R1 = total_load - R2
            
            reactions = [R1, R2]
        else:
            # For statically indeterminate beams, this is a simplified approach
            reactions = [total_load / len(self.supports)] * len(self.supports)
        
        # Calculate maximum moment (simplified)
        max_moment = abs(total_load * self.beam_length / 8)  # Approximation for uniformly loaded beam
        
        # Calculate maximum shear
        max_shear = abs(total_load / 2)
        
        # Calculate maximum deflection (simplified - assuming simply supported beam with UDL)
        E = 200e9  # Steel modulus of elasticity (Pa)
        I = 8.33e-6  # Second moment of area for a typical beam (m^4)
        
        if total_load > 0:
            max_deflection = (5 * total_load * 1000 * (self.beam_length ** 4)) / (384 * E * I)  # m
        else:
            max_deflection = 0
        
        return {
            'total_load': total_load,
            'reactions': reactions,
            'max_moment': max_moment,
            'max_shear': max_shear,
            'max_deflection': max_deflection * 1000,  # Convert to mm
            'support_positions': [s['position'] for s in self.supports]
        }
    
    def display_results(self):
        """Display analysis results"""
        if not self.analysis_results:
            return
            
        results = self.analysis_results
        
        result_text = f"""
📊 ANALYSIS RESULTS
=====================================
Total Load: {results['total_load']:.2f} kN
Max Moment: {results['max_moment']:.2f} kN⋅m
Max Shear: {results['max_shear']:.2f} kN
Max Deflection: {results['max_deflection']:.3f} mm

🔧 SUPPORT REACTIONS:
"""
        
        for i, (reaction, position) in enumerate(zip(results['reactions'], results['support_positions'])):
            result_text += f"Support {i+1} ({position:.1f}m): {reaction:.2f} kN\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, result_text)
        
    def update_visualization(self):
        """Update the 3D visualization"""
        self.ax.clear()
        self.setup_3d_plot()
        
        # Draw beam
        self.draw_beam()
        
        # Draw supports
        self.draw_supports()
        
        # Draw loads
        self.draw_loads()
        
        # Update plot limits
        margin = max(2, self.beam_length * 0.1)
        self.ax.set_xlim(-margin, self.beam_length + margin)
        self.ax.set_ylim(-2, 3)
        self.ax.set_zlim(-2, 3)
        
        self.canvas.draw()
        
    def draw_beam(self):
        """Draw the main beam"""
        # Beam dimensions
        width = 0.3
        height = 0.5
        
        # Define beam vertices
        vertices = [
            [0, -width/2, -height/2], [0, width/2, -height/2],
            [0, width/2, height/2], [0, -width/2, height/2],
            [self.beam_length, -width/2, -height/2], [self.beam_length, width/2, -height/2],
            [self.beam_length, width/2, height/2], [self.beam_length, -width/2, height/2]
        ]
        
        # Define faces
        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],  # Left face
            [vertices[4], vertices[5], vertices[6], vertices[7]],  # Right face
            [vertices[0], vertices[1], vertices[5], vertices[4]],  # Bottom face
            [vertices[2], vertices[3], vertices[7], vertices[6]],  # Top face
            [vertices[1], vertices[2], vertices[6], vertices[5]],  # Front face
            [vertices[4], vertices[7], vertices[3], vertices[0]]   # Back face
        ]
        
        # Create 3D polygon collection
        beam_collection = Poly3DCollection(faces, alpha=0.7, facecolor='lightgray', edgecolor='black')
        self.ax.add_collection3d(beam_collection)
        
    def draw_supports(self):
        """Draw support symbols"""
        for support in self.supports:
            x = support['position']
            support_type = support['type']
            
            if support_type == 'pin':
                # Draw pin support as a triangle
                triangle_x = [x-0.3, x+0.3, x, x-0.3]
                triangle_y = [0, 0, 0, 0]
                triangle_z = [-1, -1, -1.5, -1]
                self.ax.plot(triangle_x, triangle_y, triangle_z, 'g-', linewidth=3)
                self.ax.text(x, 0, -1.8, 'PIN', ha='center', color='green', fontweight='bold')
                
            elif support_type == 'roller':
                # Draw roller support as a triangle with circles
                triangle_x = [x-0.3, x+0.3, x, x-0.3]
                triangle_y = [0, 0, 0, 0]
                triangle_z = [-1, -1, -1.5, -1]
                self.ax.plot(triangle_x, triangle_y, triangle_z, 'b-', linewidth=3)
                
                # Draw rollers as small circles
                for i, roller_x in enumerate([x-0.2, x, x+0.2]):
                    circle_x = [roller_x] * 10
                    circle_y = np.linspace(-0.1, 0.1, 10)
                    circle_z = [-1.7] * 10
                    self.ax.plot(circle_x, circle_y, circle_z, 'ko', markersize=3)
                
                self.ax.text(x, 0, -2, 'ROLLER', ha='center', color='blue', fontweight='bold')
                
            elif support_type == 'fixed':
                # Draw fixed support as a rectangle
                rect_x = [x-0.2, x+0.2, x+0.2, x-0.2, x-0.2]
                rect_y = [0, 0, 0, 0, 0]
                rect_z = [-0.5, -0.5, -1.5, -1.5, -0.5]
                self.ax.plot(rect_x, rect_y, rect_z, 'r-', linewidth=4)
                
                # Fill the rectangle
                vertices = [[x-0.2, -0.1, -0.5], [x+0.2, -0.1, -0.5], 
                           [x+0.2, 0.1, -0.5], [x-0.2, 0.1, -0.5]]
                faces = [vertices]
                fixed_collection = Poly3DCollection(faces, alpha=0.7, facecolor='red')
                self.ax.add_collection3d(fixed_collection)
                
                self.ax.text(x, 0, -1.8, 'FIXED', ha='center', color='red', fontweight='bold')
    
    def draw_loads(self):
        """Draw load arrows"""
        for load in self.loads:
            if load['type'] == 'concentrated':
                x = load['position']
                magnitude = load['magnitude']
                
                # Draw arrow
                arrow_length = abs(magnitude) * 0.3
                if magnitude > 0:  # Downward load
                    self.ax.quiver(x, 0, 1, 0, 0, -arrow_length, 
                                  color='red', arrow_length_ratio=0.1, linewidth=3)
                    self.ax.text(x, 0, 1.5, f'{magnitude:.1f} kN', ha='center', color='red', fontweight='bold')
                else:  # Upward load
                    self.ax.quiver(x, 0, -1, 0, 0, arrow_length, 
                                  color='blue', arrow_length_ratio=0.1, linewidth=3)
                    self.ax.text(x, 0, -1.5, f'{magnitude:.1f} kN', ha='center', color='blue', fontweight='bold')
                    
            elif load['type'] in ['distributed', 'varying']:
                start_pos = load['start_pos']
                end_pos = load['end_pos']
                
                if load['type'] == 'distributed':
                    intensity = load['intensity']
                    start_intensity = end_intensity = intensity
                else:  # varying
                    start_intensity = load['start_intensity']
                    end_intensity = load['end_intensity']
                
                # Draw multiple arrows for distributed load
                num_arrows = max(5, int((end_pos - start_pos) * 2))
                for i in range(num_arrows + 1):
                    ratio = i / num_arrows if num_arrows > 0 else 0
                    x = start_pos + ratio * (end_pos - start_pos)
                    intensity = start_intensity + ratio * (end_intensity - start_intensity)
                    
                    arrow_length = abs(intensity) * 0.2
                    if intensity > 0:  # Downward load
                        self.ax.quiver(x, 0, 1, 0, 0, -arrow_length, 
                                      color='orange', arrow_length_ratio=0.2, linewidth=2)
                    else:  # Upward load
                        self.ax.quiver(x, 0, -1, 0, 0, arrow_length, 
                                      color='cyan', arrow_length_ratio=0.2, linewidth=2)
                
                # Add load label
                mid_x = (start_pos + end_pos) / 2
                avg_intensity = (start_intensity + end_intensity) / 2
                self.ax.text(mid_x, 0, 2, f'{avg_intensity:.1f} kN/m', ha='center', 
                           color='orange', fontweight='bold')
    
    def update_config_display(self):
        """Update the configuration display"""
        config_text = "CURRENT CONFIGURATION:\n"
        config_text += f"Beam Length: {self.beam_length:.1f} m\n\n"
        
        config_text += f"Supports ({len(self.supports)}):\n"
        for i, support in enumerate(self.supports):
            config_text += f"  {i+1}. {support['type'].upper()} at {support['position']:.1f}m\n"
        
        config_text += f"\nLoads ({len(self.loads)}):\n"
        for i, load in enumerate(self.loads):
            if load['type'] == 'concentrated':
                config_text += f"  {i+1}. Point: {load['magnitude']:.1f}kN at {load['position']:.1f}m\n"
            elif load['type'] == 'distributed':
                config_text += f"  {i+1}. Dist: {load['intensity']:.1f}kN/m from {load['start_pos']:.1f}m to {load['end_pos']:.1f}m\n"
            elif load['type'] == 'varying':
                config_text += f"  {i+1}. Vary: {load['start_intensity']:.1f}-{load['end_intensity']:.1f}kN/m from {load['start_pos']:.1f}m to {load['end_pos']:.1f}m\n"
        
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(1.0, config_text)
    
    def clear_all(self):
        """Clear all supports and loads"""
        self.supports = []
        self.loads = []
        self.analysis_results = None
        self.update_visualization()
        self.update_config_display()
        self.results_text.delete(1.0, tk.END)
        
    def reset_view(self):
        """Reset the 3D view to default"""
        self.ax.view_init(elev=20, azim=45)
        self.canvas.draw()
        
    def save_design(self):
        """Save the current beam design to a JSON file"""
        design_data = {
            'beam_length': self.beam_length,
            'supports': self.supports,
            'loads': self.loads
        }
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(design_data, f, indent=2)
                messagebox.showinfo("Success", "Design saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save design: {str(e)}")
    
    def load_design(self):
        """Load a beam design from a JSON file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    design_data = json.load(f)
                
                self.beam_length = design_data.get('beam_length', 10.0)
                self.supports = design_data.get('supports', [])
                self.loads = design_data.get('loads', [])
                
                # Update GUI
                self.length_var.set(self.beam_length)
                self.analysis_results = None
                self.update_visualization()
                self.update_config_display()
                self.results_text.delete(1.0, tk.END)
                
                messagebox.showinfo("Success", "Design loaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load design: {str(e)}")
    
    def show_charts(self):
        """Show 2D charts for analysis results"""
        if not self.analysis_results:
            messagebox.showwarning("Warning", "Please analyze the beam first!")
            return
        
        self.create_charts_window()
    
    def create_charts_window(self):
        """Create a new window with 2D charts"""
        chart_window = tk.Toplevel(self.root)
        chart_window.title("📈 Beam Analysis Charts")
        chart_window.geometry("900x700")
        chart_window.configure(bg=self.colors['bg'])
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8), facecolor='#0a1428')
        
        # Generate x coordinates for plotting
        x = np.linspace(0, self.beam_length, 100)
        
        # Plot 1: Load diagram
        ax1.set_facecolor('#001428')
        self.plot_load_diagram(ax1, x)
        ax1.set_title('Load Diagram', color=self.colors['accent'], fontweight='bold')
        ax1.set_xlabel('Position (m)', color=self.colors['secondary'])
        ax1.set_ylabel('Load (kN/m)', color=self.colors['secondary'])
        ax1.tick_params(colors=self.colors['secondary'])
        ax1.grid(True, alpha=0.3, color=self.colors['secondary'])
        
        # Plot 2: Shear force diagram (simplified)
        ax2.set_facecolor('#001428')
        self.plot_shear_diagram(ax2, x)
        ax2.set_title('Shear Force Diagram', color=self.colors['accent'], fontweight='bold')
        ax2.set_xlabel('Position (m)', color=self.colors['secondary'])
        ax2.set_ylabel('Shear Force (kN)', color=self.colors['secondary'])
        ax2.tick_params(colors=self.colors['secondary'])
        ax2.grid(True, alpha=0.3, color=self.colors['secondary'])
        
        # Plot 3: Bending moment diagram (simplified)
        ax3.set_facecolor('#001428')
        self.plot_moment_diagram(ax3, x)
        ax3.set_title('Bending Moment Diagram', color=self.colors['accent'], fontweight='bold')
        ax3.set_xlabel('Position (m)', color=self.colors['secondary'])
        ax3.set_ylabel('Moment (kN⋅m)', color=self.colors['secondary'])
        ax3.tick_params(colors=self.colors['secondary'])
        ax3.grid(True, alpha=0.3, color=self.colors['secondary'])
        
        # Plot 4: Deflection diagram (simplified)
        ax4.set_facecolor('#001428')
        self.plot_deflection_diagram(ax4, x)
        ax4.set_title('Deflection Diagram', color=self.colors['accent'], fontweight='bold')
        ax4.set_xlabel('Position (m)', color=self.colors['secondary'])
        ax4.set_ylabel('Deflection (mm)', color=self.colors['secondary'])
        ax4.tick_params(colors=self.colors['secondary'])
        ax4.grid(True, alpha=0.3, color=self.colors['secondary'])
        
        plt.tight_layout()
        
        # Embed the plots in the tkinter window
        canvas = FigureCanvasTkAgg(fig, chart_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add close button
        close_btn = tk.Button(chart_window, text="Close", bg=self.colors['danger'],
                             fg='white', font=("Segoe UI", 10, "bold"),
                             command=chart_window.destroy)
        close_btn.pack(pady=10)
    
    def plot_load_diagram(self, ax, x):
        """Plot the load diagram"""
        load_values = np.zeros_like(x)
        
        for load in self.loads:
            if load['type'] == 'concentrated':
                # Find closest point to load position
                idx = np.argmin(np.abs(x - load['position']))
                if idx < len(load_values):
                    # Show as impulse
                    ax.arrow(load['position'], 0, 0, load['magnitude'], 
                            head_width=self.beam_length*0.02, head_length=abs(load['magnitude'])*0.1,
                            fc='red', ec='red')
                    
            elif load['type'] == 'distributed':
                mask = (x >= load['start_pos']) & (x <= load['end_pos'])
                load_values[mask] = load['intensity']
                
            elif load['type'] == 'varying':
                mask = (x >= load['start_pos']) & (x <= load['end_pos'])
                length = load['end_pos'] - load['start_pos']
                if length > 0:
                    for i, pos in enumerate(x[mask]):
                        ratio = (pos - load['start_pos']) / length
                        intensity = load['start_intensity'] + ratio * (load['end_intensity'] - load['start_intensity'])
                        load_values[mask][i] = intensity
        
        ax.plot(x, load_values, 'orange', linewidth=2, label='Distributed Load')
        ax.fill_between(x, 0, load_values, alpha=0.3, color='orange')
        
        # Mark supports
        for support in self.supports:
            ax.axvline(x=support['position'], color='green', linestyle='--', alpha=0.7)
            ax.text(support['position'], max(load_values)*0.1, support['type'].upper(), 
                   rotation=90, ha='right', va='bottom', color='green', fontweight='bold')
    
    def plot_shear_diagram(self, ax, x):
        """Plot simplified shear force diagram"""
        if not self.analysis_results:
            return
            
        shear_values = np.zeros_like(x)
        
        # This is a simplified shear diagram
        # In reality, this would require more complex calculations
        total_load = self.analysis_results['total_load']
        
        # Simple approximation: linear variation between supports
        if len(self.supports) >= 2:
            support_positions = sorted([s['position'] for s in self.supports])
            reactions = self.analysis_results['reactions']
            
            current_shear = reactions[0] if len(reactions) > 0 else 0
            
            for i, pos in enumerate(x):
                if pos <= support_positions[0]:
                    shear_values[i] = 0
                elif len(support_positions) > 1 and pos <= support_positions[1]:
                    # Between first and second support
                    progress = (pos - support_positions[0]) / (support_positions[1] - support_positions[0])
                    shear_values[i] = current_shear * (1 - progress)
                else:
                    shear_values[i] = 0
        
        ax.plot(x, shear_values, 'blue', linewidth=2)
        ax.fill_between(x, 0, shear_values, alpha=0.3, color='blue')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Mark supports
        for support in self.supports:
            ax.axvline(x=support['position'], color='green', linestyle='--', alpha=0.7)
    
    def plot_moment_diagram(self, ax, x):
        """Plot simplified bending moment diagram"""
        if not self.analysis_results:
            return
            
        moment_values = np.zeros_like(x)
        
        # Simplified moment diagram - parabolic approximation
        max_moment = self.analysis_results['max_moment']
        
        if len(self.supports) >= 2:
            support_positions = sorted([s['position'] for s in self.supports])
            span = support_positions[1] - support_positions[0] if len(support_positions) > 1 else self.beam_length
            
            for i, pos in enumerate(x):
                if support_positions[0] <= pos <= support_positions[1] if len(support_positions) > 1 else 0 <= pos <= self.beam_length:
                    # Parabolic approximation
                    relative_pos = (pos - support_positions[0]) / span if span > 0 else 0
                    moment_values[i] = max_moment * 4 * relative_pos * (1 - relative_pos)
        
        ax.plot(x, moment_values, 'purple', linewidth=2)
        ax.fill_between(x, 0, moment_values, alpha=0.3, color='purple')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Mark supports
        for support in self.supports:
            ax.axvline(x=support['position'], color='green', linestyle='--', alpha=0.7)
    
    def plot_deflection_diagram(self, ax, x):
        """Plot simplified deflection diagram"""
        if not self.analysis_results:
            return
            
        deflection_values = np.zeros_like(x)
        max_deflection = self.analysis_results['max_deflection']  # in mm
        
        if len(self.supports) >= 2:
            support_positions = sorted([s['position'] for s in self.supports])
            span = support_positions[1] - support_positions[0] if len(support_positions) > 1 else self.beam_length
            
            for i, pos in enumerate(x):
                if support_positions[0] <= pos <= support_positions[1] if len(support_positions) > 1 else 0 <= pos <= self.beam_length:
                    # Simplified deflection curve
                    relative_pos = (pos - support_positions[0]) / span if span > 0 else 0
                    deflection_values[i] = -max_deflection * relative_pos * (1 - relative_pos) * (1 - 2*relative_pos + 2*relative_pos**2)
        
        ax.plot(x, deflection_values, 'red', linewidth=2)
        ax.fill_between(x, 0, deflection_values, alpha=0.3, color='red')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Mark supports
        for support in self.supports:
            ax.axvline(x=support['position'], color='green', linestyle='--', alpha=0.7)


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = BeamDesigner(root)
    
    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Set minimum window size
    root.minsize(1200, 800)
    
    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit the Beam Designer?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()