#!/usr/bin/env python3
"""
Interactive Beam Designer
Allows users to create custom beam configurations and analyze them
"""

from beam_analysis import OverhangingBeam, Support
import matplotlib.pyplot as plt
import numpy as np

class InteractiveBeamDesigner:
    """Interactive interface for designing and analyzing beams"""
    
    def __init__(self):
        self.beam = None
        
    def get_user_input(self, prompt, input_type=float, validation_func=None):
        """Get validated user input"""
        while True:
            try:
                user_input = input(prompt)
                if user_input.lower() in ['quit', 'exit', 'q']:
                    return None
                
                value = input_type(user_input)
                
                if validation_func and not validation_func(value):
                    print("❌ Invalid input. Please try again.")
                    continue
                    
                return value
            except ValueError:
                print(f"❌ Please enter a valid {input_type.__name__}")
                continue
    
    def create_beam(self):
        """Create a new beam with user specifications"""
        print("\n🏗️  BEAM CREATION")
        print("=" * 40)
        
        # Get beam length
        length = self.get_user_input(
            "Enter beam length (m): ",
            float,
            lambda x: x > 0
        )
        if length is None:
            return False
        
        # Get number of supports
        num_supports = self.get_user_input(
            "Enter number of supports (minimum 2): ",
            int,
            lambda x: x >= 2
        )
        if num_supports is None:
            return False
        
        # Get support positions and types
        supports = []
        for i in range(num_supports):
            print(f"\n📍 Support {i+1}:")
            
            position = self.get_user_input(
                f"  Position (0 to {length}m): ",
                float,
                lambda x: 0 <= x <= length
            )
            if position is None:
                return False
            
            print("  Support types: 1=Pin, 2=Roller")
            support_type_num = self.get_user_input(
                "  Type (1 or 2): ",
                int,
                lambda x: x in [1, 2]
            )
            if support_type_num is None:
                return False
            
            support_type = 'pin' if support_type_num == 1 else 'roller'
            supports.append(Support(position=position, type=support_type))
        
        # Create beam
        self.beam = OverhangingBeam(length=length, supports=supports)
        print(f"\n✅ Beam created successfully! Length: {length}m, Supports: {len(supports)}")
        return True
    
    def add_loads(self):
        """Add loads to the beam"""
        if not self.beam:
            print("❌ Please create a beam first!")
            return
        
        print("\n⚡ LOAD ADDITION")
        print("=" * 40)
        
        while True:
            print("\nLoad types:")
            print("1. Concentrated Load")
            print("2. Uniformly Varying Load")
            print("3. Finish adding loads")
            
            choice = self.get_user_input(
                "Choose load type (1-3): ",
                int,
                lambda x: x in [1, 2, 3]
            )
            if choice is None or choice == 3:
                break
            
            if choice == 1:
                self.add_concentrated_load()
            elif choice == 2:
                self.add_varying_load()
    
    def add_concentrated_load(self):
        """Add a concentrated load"""
        print("\n🎯 Concentrated Load:")
        
        position = self.get_user_input(
            f"  Position (0 to {self.beam.length}m): ",
            float,
            lambda x: 0 <= x <= self.beam.length
        )
        if position is None:
            return
        
        magnitude = self.get_user_input(
            "  Magnitude (kN, positive=downward): ",
            float
        )
        if magnitude is None:
            return
        
        self.beam.add_concentrated_load(position, magnitude)
        print(f"✅ Added {magnitude}kN load at {position}m")
    
    def add_varying_load(self):
        """Add a uniformly varying load"""
        print("\n📈 Uniformly Varying Load:")
        
        start_pos = self.get_user_input(
            f"  Start position (0 to {self.beam.length}m): ",
            float,
            lambda x: 0 <= x <= self.beam.length
        )
        if start_pos is None:
            return
        
        end_pos = self.get_user_input(
            f"  End position ({start_pos} to {self.beam.length}m): ",
            float,
            lambda x: start_pos < x <= self.beam.length
        )
        if end_pos is None:
            return
        
        start_intensity = self.get_user_input(
            "  Start intensity (kN/m, positive=downward): ",
            float
        )
        if start_intensity is None:
            return
        
        end_intensity = self.get_user_input(
            "  End intensity (kN/m, positive=downward): ",
            float
        )
        if end_intensity is None:
            return
        
        self.beam.add_uniformly_varying_load(start_pos, end_pos, start_intensity, end_intensity)
        print(f"✅ Added varying load from {start_pos}m to {end_pos}m")
        print(f"   Intensity: {start_intensity} to {end_intensity} kN/m")
    
    def analyze_beam(self):
        """Analyze the beam and display results"""
        if not self.beam:
            print("❌ Please create a beam first!")
            return
        
        if not self.beam.concentrated_loads and not self.beam.varying_loads:
            print("❌ Please add some loads first!")
            return
        
        print("\n🔬 ANALYZING BEAM...")
        print("=" * 40)
        
        try:
            # Perform analysis
            self.beam.analyze()
            
            # Display results
            summary = self.beam.get_summary()
            
            print("\n📊 ANALYSIS RESULTS:")
            print("-" * 30)
            print("Support Reactions:")
            for pos, reaction in summary['reactions'].items():
                print(f"  At {pos}m: {reaction:.2f} kN")
            
            print(f"\nMaximum Shear Force: {summary['max_shear_force']:.2f} kN")
            print(f"  Location: {summary['max_shear_position']:.2f} m")
            
            print(f"\nMaximum Bending Moment: {summary['max_bending_moment']:.2f} kN⋅m")
            print(f"  Location: {summary['max_moment_position']:.2f} m")
            
            # Plot results
            print("\n📈 Generating plots...")
            fig, axes = self.beam.plot_complete_analysis(figsize=(15, 10))
            
            # Save plot
            filename = 'c:/Users/Aditya/OneDrive/Desktop/project/custom_beam_analysis.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"📁 Plot saved as: {filename}")
            
            plt.show()
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
    
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "="*50)
        print("🏗️  INTERACTIVE BEAM DESIGNER")
        print("="*50)
        print("1. Create New Beam")
        print("2. Add Loads")
        print("3. Analyze Beam")
        print("4. Show Current Beam Info")
        print("5. Exit")
        print("="*50)
    
    def show_beam_info(self):
        """Display current beam information"""
        if not self.beam:
            print("❌ No beam created yet!")
            return
        
        print("\n📋 CURRENT BEAM INFORMATION")
        print("=" * 40)
        print(f"Length: {self.beam.length} m")
        
        print(f"\nSupports ({len(self.beam.supports)}):")
        for support in self.beam.supports:
            print(f"  {support.type.title()} at {support.position}m")
        
        print(f"\nConcentrated Loads ({len(self.beam.concentrated_loads)}):")
        for load in self.beam.concentrated_loads:
            print(f"  {load.magnitude}kN at {load.position}m")
        
        print(f"\nUniformly Varying Loads ({len(self.beam.varying_loads)}):")
        for uvl in self.beam.varying_loads:
            print(f"  From {uvl.start_pos}m to {uvl.end_pos}m")
            print(f"    Intensity: {uvl.start_intensity} to {uvl.end_intensity} kN/m")
    
    def run(self):
        """Run the interactive designer"""
        print("🎉 Welcome to the Interactive Beam Designer!")
        print("💡 Type 'quit', 'exit', or 'q' at any input to return to menu")
        
        while True:
            self.display_menu()
            
            choice = self.get_user_input(
                "Choose an option (1-5): ",
                int,
                lambda x: 1 <= x <= 5
            )
            
            if choice is None or choice == 5:
                print("\n👋 Thank you for using the Interactive Beam Designer!")
                break
            elif choice == 1:
                self.create_beam()
            elif choice == 2:
                self.add_loads()
            elif choice == 3:
                self.analyze_beam()
            elif choice == 4:
                self.show_beam_info()

def main():
    """Main function to run the interactive designer"""
    designer = InteractiveBeamDesigner()
    designer.run()

if __name__ == "__main__":
    main()
