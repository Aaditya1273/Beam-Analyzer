import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.patches as mpatches
from dataclasses import dataclass
from typing import List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

@dataclass
class Support:
    """Represents a support at a specific position"""
    position: float
    type: str  # 'pin', 'roller', 'fixed'
    
@dataclass
class ConcentratedLoad:
    """Represents a concentrated load"""
    position: float
    magnitude: float  # Positive for downward loads
    
@dataclass
class UniformlyVaryingLoad:
    """Represents a uniformly varying load (triangular or trapezoidal)"""
    start_pos: float
    end_pos: float
    start_intensity: float  # Load intensity at start (positive for downward)
    end_intensity: float    # Load intensity at end (positive for downward)

class OverhangingBeam:
    """
    A comprehensive class for analyzing overhanging beams with various load types
    """
    
    def __init__(self, length: float, supports: List[Support]):
        """
        Initialize the beam
        
        Args:
            length: Total length of the beam
            supports: List of Support objects
        """
        self.length = length
        self.supports = sorted(supports, key=lambda x: x.position)
        self.concentrated_loads = []
        self.varying_loads = []
        self.reactions = {}
        
        # Analysis parameters
        self.num_points = 1000  # Number of points for analysis
        self.x_coords = np.linspace(0, length, self.num_points)
        self.shear_force = np.zeros(self.num_points)
        self.bending_moment = np.zeros(self.num_points)
        
    def add_concentrated_load(self, position: float, magnitude: float):
        """Add a concentrated load to the beam"""
        if 0 <= position <= self.length:
            self.concentrated_loads.append(ConcentratedLoad(position, magnitude))
        else:
            raise ValueError(f"Load position {position} is outside beam length {self.length}")
            
    def add_uniformly_varying_load(self, start_pos: float, end_pos: float, 
                                 start_intensity: float, end_intensity: float):
        """Add a uniformly varying load to the beam"""
        if not (0 <= start_pos <= self.length and 0 <= end_pos <= self.length):
            raise ValueError("Load positions must be within beam length")
        if start_pos >= end_pos:
            raise ValueError("Start position must be less than end position")
            
        self.varying_loads.append(UniformlyVaryingLoad(start_pos, end_pos, 
                                                      start_intensity, end_intensity))
    
    def _calculate_reactions(self):
        """Calculate support reactions using equilibrium equations"""
        if len(self.supports) < 2:
            raise ValueError("At least 2 supports are required for static determinacy")
        
        # Initialize reaction forces
        for support in self.supports:
            self.reactions[support.position] = 0
        
        # Calculate total load and moment from concentrated loads
        total_load = sum(load.magnitude for load in self.concentrated_loads)
        total_moment = sum(load.magnitude * load.position for load in self.concentrated_loads)
        
        # Add loads from uniformly varying loads
        for uvl in self.varying_loads:
            length = uvl.end_pos - uvl.start_pos
            # Total load = area of trapezoid
            area = 0.5 * length * (uvl.start_intensity + uvl.end_intensity)
            total_load += area
            
            # Centroid calculation for trapezoidal load
            if uvl.start_intensity == uvl.end_intensity:
                # Uniform load
                centroid = uvl.start_pos + length / 2
            else:
                # Trapezoidal load centroid
                a = uvl.start_intensity
                b = uvl.end_intensity
                centroid = uvl.start_pos + length * (a + 2*b) / (3*(a + b))
            
            total_moment += area * centroid
        
        # For simplicity, assume 2 supports (statically determinate)
        if len(self.supports) == 2:
            support1, support2 = self.supports[0], self.supports[1]
            pos1, pos2 = support1.position, support2.position
            
            # Moment equilibrium about first support
            self.reactions[pos2] = total_moment / (pos2 - pos1)
            
            # Force equilibrium
            self.reactions[pos1] = total_load - self.reactions[pos2]
        
        return self.reactions
