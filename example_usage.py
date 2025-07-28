#!/usr/bin/env python3
"""
Example usage of the Overhanging Beam Analysis Program
This file demonstrates various beam configurations with different load types
"""

from beam_analysis import OverhangingBeam, Support, ConcentratedLoad, UniformlyVaryingLoad
import matplotlib.pyplot as plt
import numpy as np

def example_1_simple_overhanging_beam():
    """
    Example 1: Simple overhanging beam with concentrated loads
    Beam: 10m total length, supports at 2m and 8m
    Loads: 50kN at 1m, 30kN at 6m, 40kN at 9m
    """
    print("=" * 60)
    print("EXAMPLE 1: Simple Overhanging Beam with Concentrated Loads")
    print("=" * 60)
    
    # Create beam with supports
    beam = OverhangingBeam(
        length=10.0,
        supports=[
            Support(position=2.0, type='pin'),
            Support(position=8.0, type='roller')
        ]
    )
    
    # Add concentrated loads
    beam.add_concentrated_load(position=1.0, magnitude=50.0)  # Left overhang
    beam.add_concentrated_load(position=6.0, magnitude=30.0)  # Between supports
    beam.add_concentrated_load(position=9.0, magnitude=40.0)  # Right overhang
    
    # Analyze the beam
    beam.analyze()
    
    # Get summary
    summary = beam.get_summary()
    print(f"Support Reactions: {summary['reactions']}")
    print(f"Maximum Shear Force: {summary['max_shear_force']:.2f} kN at {summary['max_shear_position']:.2f} m")
    print(f"Maximum Bending Moment: {summary['max_bending_moment']:.2f} kN⋅m at {summary['max_moment_position']:.2f} m")
    
    # Plot results
    fig, axes = beam.plot_complete_analysis(figsize=(15, 10))
    plt.savefig('c:/Users/Aditya/OneDrive/Desktop/project/example_1_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return beam

def example_2_beam_with_varying_loads():
    """
    Example 2: Beam with uniformly varying loads (triangular and trapezoidal)
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Beam with Uniformly Varying Loads")
    print("=" * 60)
    
    # Create beam
    beam = OverhangingBeam(
        length=12.0,
        supports=[
            Support(position=3.0, type='pin'),
            Support(position=9.0, type='roller')
        ]
    )
    
    # Add concentrated load
    beam.add_concentrated_load(position=1.5, magnitude=25.0)
    
    # Add uniformly varying loads
    # Triangular load (0 to 20 kN/m) from 4m to 7m
    beam.add_uniformly_varying_load(start_pos=4.0, end_pos=7.0, 
                                   start_intensity=0.0, end_intensity=20.0)
    
    # Trapezoidal load (15 to 5 kN/m) from 10m to 12m
    beam.add_uniformly_varying_load(start_pos=10.0, end_pos=12.0, 
                                   start_intensity=15.0, end_intensity=5.0)
    
    # Analyze the beam
    beam.analyze()
    
    # Get summary
    summary = beam.get_summary()
    print(f"Support Reactions: {summary['reactions']}")
    print(f"Maximum Shear Force: {summary['max_shear_force']:.2f} kN at {summary['max_shear_position']:.2f} m")
    print(f"Maximum Bending Moment: {summary['max_bending_moment']:.2f} kN⋅m at {summary['max_moment_position']:.2f} m")
    
    # Plot results
    fig, axes = beam.plot_complete_analysis(figsize=(15, 10))
    plt.savefig('c:/Users/Aditya/OneDrive/Desktop/project/example_2_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return beam

def example_3_complex_loading():
    """
    Example 3: Complex loading with multiple load types
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Complex Loading Scenario")
    print("=" * 60)
    
    # Create beam
    beam = OverhangingBeam(
        length=15.0,
        supports=[
            Support(position=4.0, type='pin'),
            Support(position=11.0, type='roller')
        ]
    )
    
    # Add multiple concentrated loads
    beam.add_concentrated_load(position=2.0, magnitude=35.0)
    beam.add_concentrated_load(position=6.5, magnitude=45.0)
    beam.add_concentrated_load(position=13.0, magnitude=28.0)
    
    # Add multiple varying loads
    # Uniform load from 0 to 3m
    beam.add_uniformly_varying_load(start_pos=0.0, end_pos=3.0, 
                                   start_intensity=12.0, end_intensity=12.0)
    
    # Triangular load from 8m to 10m
    beam.add_uniformly_varying_load(start_pos=8.0, end_pos=10.0, 
                                   start_intensity=0.0, end_intensity=25.0)
    
    # Trapezoidal load from 12m to 15m
    beam.add_uniformly_varying_load(start_pos=12.0, end_pos=15.0, 
                                   start_intensity=18.0, end_intensity=8.0)
    
    # Analyze the beam
    beam.analyze()
    
    # Get summary
    summary = beam.get_summary()
    print(f"Support Reactions: {summary['reactions']}")
    print(f"Maximum Shear Force: {summary['max_shear_force']:.2f} kN at {summary['max_shear_position']:.2f} m")
    print(f"Maximum Bending Moment: {summary['max_bending_moment']:.2f} kN⋅m at {summary['max_moment_position']:.2f} m")
    
    # Plot results
    fig, axes = beam.plot_complete_analysis(figsize=(15, 10))
    plt.savefig('c:/Users/Aditya/OneDrive/Desktop/project/example_3_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return beam

def compare_beams(beams, titles):
    """
    Compare multiple beam analyses in a single plot
    """
    fig, axes = plt.subplots(2, len(beams), figsize=(5*len(beams), 8))
    fig.suptitle('Beam Analysis Comparison', fontsize=16, fontweight='bold')
    
    for i, (beam, title) in enumerate(zip(beams, titles)):
        if len(beams) == 1:
            sf_ax, bm_ax = axes[0], axes[1]
        else:
            sf_ax, bm_ax = axes[0, i], axes[1, i]
        
        # Plot shear force
        sf_ax.plot(beam.x_coords, beam.shear_force, 'b-', linewidth=2)
        sf_ax.fill_between(beam.x_coords, 0, beam.shear_force, alpha=0.3, color='blue')
        sf_ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
        sf_ax.grid(True, alpha=0.3)
        sf_ax.set_title(f'{title}\nShear Force', fontsize=10, fontweight='bold')
        sf_ax.set_ylabel('S.F. (kN)', fontsize=9)
        
        # Plot bending moment
        bm_ax.plot(beam.x_coords, beam.bending_moment, 'r-', linewidth=2)
        bm_ax.fill_between(beam.x_coords, 0, beam.bending_moment, alpha=0.3, color='red')
        bm_ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
        bm_ax.grid(True, alpha=0.3)
        bm_ax.set_title('Bending Moment', fontsize=10, fontweight='bold')
        bm_ax.set_xlabel('Distance (m)', fontsize=9)
        bm_ax.set_ylabel('B.M. (kN⋅m)', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('c:/Users/Aditya/OneDrive/Desktop/project/beam_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """
    Main function to run all examples
    """
    print("🏗️  OVERHANGING BEAM ANALYSIS PROGRAM")
    print("📊  Calculating S.F. and B.M. Diagrams")
    print("🎯  With Concentrated and Uniformly Varying Loads\n")
    
    # Run examples
    beam1 = example_1_simple_overhanging_beam()
    beam2 = example_2_beam_with_varying_loads()
    beam3 = example_3_complex_loading()
    
    # Compare all beams
    print("\n" + "=" * 60)
    print("COMPARISON OF ALL BEAM ANALYSES")
    print("=" * 60)
    
    compare_beams(
        beams=[beam1, beam2, beam3],
        titles=['Simple Loads', 'Varying Loads', 'Complex Loading']
    )
    
    print("\n✅ Analysis Complete! Check the generated PNG files for detailed diagrams.")
    print("📁 Files saved in: c:/Users/Aditya/OneDrive/Desktop/project/")

if __name__ == "__main__":
    main()
