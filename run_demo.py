#!/usr/bin/env python3
"""
Quick Demo Runner for Beam Analysis Program
Tests installation and runs a simple example
"""

import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['numpy', 'matplotlib']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please run: pip install numpy matplotlib")
            return False
    
    return True

def run_simple_demo():
    """Run a simple beam analysis demo"""
    print("\n🏗️  RUNNING BEAM ANALYSIS DEMO")
    print("=" * 50)
    
    try:
        from beam_analysis import OverhangingBeam, Support
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Create a simple overhanging beam
        print("📐 Creating beam: 8m length with supports at 2m and 6m")
        beam = OverhangingBeam(
            length=8.0,
            supports=[
                Support(position=2.0, type='pin'),
                Support(position=6.0, type='roller')
            ]
        )
        
        # Add loads
        print("⚡ Adding loads:")
        print("   - 40kN concentrated load at 1m (left overhang)")
        print("   - 60kN concentrated load at 4m (between supports)")
        print("   - 30kN concentrated load at 7m (right overhang)")
        
        beam.add_concentrated_load(position=1.0, magnitude=40.0)
        beam.add_concentrated_load(position=4.0, magnitude=60.0)
        beam.add_concentrated_load(position=7.0, magnitude=30.0)
        
        # Add a triangular load
        print("   - Triangular load: 0 to 15 kN/m from 3m to 5m")
        beam.add_uniformly_varying_load(
            start_pos=3.0, end_pos=5.0,
            start_intensity=0.0, end_intensity=15.0
        )
        
        # Analyze
        print("\n🔬 Analyzing beam...")
        beam.analyze()
        
        # Get results
        summary = beam.get_summary()
        print("\n📊 ANALYSIS RESULTS:")
        print("-" * 30)
        print("Support Reactions:")
        for pos, reaction in summary['reactions'].items():
            print(f"  At {pos}m: {reaction:.2f} kN")
        
        print(f"\nMaximum Shear Force: {summary['max_shear_force']:.2f} kN")
        print(f"  Location: {summary['max_shear_position']:.2f} m")
        
        print(f"\nMaximum Bending Moment: {summary['max_bending_moment']:.2f} kN⋅m")
        print(f"  Location: {summary['max_moment_position']:.2f} m")
        
        # Create plots
        print("\n📈 Generating plots...")
        fig, axes = beam.plot_complete_analysis(figsize=(12, 8))
        
        # Save plot
        filename = 'c:/Users/Aditya/OneDrive/Desktop/project/demo_results.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📁 Plot saved as: demo_results.png")
        
        # Show plot
        plt.show()
        
        print("\n✅ Demo completed successfully!")
        print("🎯 The beam analysis program is working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 BEAM ANALYSIS PROGRAM - QUICK DEMO")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Run demo
    if run_simple_demo():
        print("\n🎉 Ready to run full examples!")
        print("💡 Next steps:")
        print("   - Run 'python example_usage.py' for comprehensive examples")
        print("   - Run 'python interactive_beam_designer.py' for custom designs")
    else:
        print("\n❌ Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
