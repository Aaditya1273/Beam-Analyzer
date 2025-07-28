# 🏗️ Overhanging Beam Analysis Program

A comprehensive Python program for calculating and plotting **Shear Force (S.F.)** and **Bending Moment (B.M.)** diagrams for overhanging beams subjected to various load combinations.

## ✨ Features

- **Multiple Load Types Support:**
  - Concentrated loads (point loads)
  - Uniformly varying loads (triangular and trapezoidal distributions)
  - Combination of different load types

- **Advanced Beam Analysis:**
  - Automatic reaction calculation using equilibrium equations
  - High-precision S.F. and B.M. calculations at 1000+ points
  - Support for multiple support types (pin, roller)

- **Professional Visualization:**
  - Detailed beam loading diagrams with scaled load arrows
  - Color-coded shear force diagrams with annotations
  - Bending moment diagrams with maximum value highlighting
  - High-resolution plot exports (300 DPI)

- **Interactive Design Interface:**
  - User-friendly command-line interface
  - Step-by-step beam configuration
  - Real-time input validation
  - Comprehensive analysis summaries

## 📁 Project Structure

```
project/
├── beam_analysis.py              # Core beam analysis engine
├── example_usage.py              # Pre-configured examples
├── interactive_beam_designer.py  # Interactive user interface
├── requirements.txt              # Python dependencies
└── README.md                     # This documentation
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Pre-configured Examples

```bash
python example_usage.py
```

This will run three comprehensive examples:
- **Example 1:** Simple overhanging beam with concentrated loads
- **Example 2:** Beam with uniformly varying loads
- **Example 3:** Complex loading scenario with mixed load types

### 3. Use Interactive Designer

```bash
python interactive_beam_designer.py
```

Create your own custom beam configurations with the guided interface.

## 📊 Example Results

### Example 1: Simple Overhanging Beam
- **Beam:** 10m length with supports at 2m and 8m
- **Loads:** 50kN at 1m, 30kN at 6m, 40kN at 9m
- **Results:** Complete S.F. and B.M. diagrams with reaction calculations

### Example 2: Varying Loads
- **Beam:** 12m length with supports at 3m and 9m
- **Loads:** Triangular load (0-20 kN/m) and trapezoidal load (15-5 kN/m)
- **Results:** Smooth S.F. and B.M. curves accounting for distributed loads

### Example 3: Complex Loading
- **Beam:** 15m length with multiple concentrated and varying loads
- **Results:** Comprehensive analysis with maximum moment and shear identification

## 🔧 API Usage

### Basic Usage

```python
from beam_analysis import OverhangingBeam, Support

# Create beam
beam = OverhangingBeam(
    length=10.0,
    supports=[
        Support(position=2.0, type='pin'),
        Support(position=8.0, type='roller')
    ]
)

# Add loads
beam.add_concentrated_load(position=5.0, magnitude=100.0)
beam.add_uniformly_varying_load(
    start_pos=0.0, end_pos=3.0,
    start_intensity=0.0, end_intensity=20.0
)

# Analyze and plot
beam.analyze()
fig, axes = beam.plot_complete_analysis()
```

### Advanced Features

```python
# Get detailed analysis summary
summary = beam.get_summary()
print(f"Max Shear Force: {summary['max_shear_force']:.2f} kN")
print(f"Max Bending Moment: {summary['max_bending_moment']:.2f} kN⋅m")

# Access raw data
shear_values = beam.shear_force
moment_values = beam.bending_moment
x_coordinates = beam.x_coords
```

## 📈 Visualization Features

### Beam Loading Diagram
- Scaled load arrows showing magnitude and direction
- Support symbols (triangular for pin/roller)
- Reaction force values displayed
- Load intensity labels for varying loads

### Shear Force Diagram
- Blue line plot with filled area
- Critical point annotations
- Zero-crossing identification
- Grid lines for easy reading

### Bending Moment Diagram
- Red line plot with filled area
- Maximum/minimum moment highlighting
- Automatic scaling and labeling
- Professional engineering format

## 🎯 Load Types Explained

### Concentrated Loads
Point loads applied at specific positions:
```python
beam.add_concentrated_load(position=5.0, magnitude=100.0)
```

### Uniformly Varying Loads
Distributed loads with linear intensity variation:

**Uniform Load (Rectangle):**
```python
beam.add_uniformly_varying_load(
    start_pos=2.0, end_pos=6.0,
    start_intensity=15.0, end_intensity=15.0
)
```

**Triangular Load:**
```python
beam.add_uniformly_varying_load(
    start_pos=0.0, end_pos=4.0,
    start_intensity=0.0, end_intensity=20.0
)
```

**Trapezoidal Load:**
```python
beam.add_uniformly_varying_load(
    start_pos=3.0, end_pos=8.0,
    start_intensity=10.0, end_intensity=25.0
)
```

## ⚙️ Technical Details

### Analysis Method
- **Equilibrium Equations:** ΣF = 0, ΣM = 0
- **Sign Convention:** Positive shear causes clockwise rotation, positive moment causes compression in top fiber
- **Numerical Integration:** High-resolution point-by-point calculation
- **Load Centroids:** Accurate centroid calculation for trapezoidal loads

### Accuracy
- **Resolution:** 1000 calculation points along beam length
- **Precision:** Double-precision floating-point arithmetic
- **Validation:** Equilibrium check for all calculations

### Performance
- **Speed:** Sub-second analysis for typical beam configurations
- **Memory:** Efficient numpy array operations
- **Scalability:** Handles beams up to 100m+ length

## 🛠️ Customization

### Adding New Load Types
Extend the `OverhangingBeam` class to support additional load patterns:

```python
def add_parabolic_load(self, start_pos, end_pos, peak_intensity):
    # Implementation for parabolic load distribution
    pass
```

### Custom Visualization
Modify plotting methods for specific requirements:

```python
def plot_custom_diagram(self, ax, custom_parameters):
    # Custom plotting implementation
    pass
```

## 📝 Input Validation

The program includes comprehensive input validation:
- **Position Bounds:** All positions must be within beam length
- **Load Magnitudes:** Accepts positive (downward) and negative (upward) loads
- **Support Requirements:** Minimum 2 supports for static determinacy
- **Geometric Constraints:** Start position < End position for varying loads

## 🔍 Error Handling

Robust error handling for common issues:
- Invalid beam configurations
- Insufficient support conditions
- Overlapping load definitions
- Numerical computation errors

## 📊 Output Files

Generated files include:
- `example_1_results.png` - Simple beam analysis
- `example_2_results.png` - Varying loads analysis
- `example_3_results.png` - Complex loading analysis
- `beam_comparison.png` - Side-by-side comparison
- `custom_beam_analysis.png` - Interactive designer output

## 🤝 Contributing

Feel free to contribute by:
1. Adding new load types
2. Improving visualization features
3. Enhancing the interactive interface
4. Adding validation checks
5. Optimizing performance

## 📚 References

- **Structural Analysis:** Hibbeler, R.C. "Structural Analysis"
- **Beam Theory:** Timoshenko, S.P. "Strength of Materials"
- **Numerical Methods:** Chapra, S.C. "Numerical Methods for Engineers"

## 📄 License

This project is open-source and available for educational and commercial use.

---

**Made with ❤️ for Structural Engineers and Students**

*For questions or support, please refer to the code documentation or create an issue.*
