# 🚀 Advanced Beam Analysis & 3D Visualization Suite

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-black.svg)
![Three.js](https://img.shields.io/badge/Three.js-r135+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A state-of-the-art structural analysis tool that combines a powerful Python backend with a stunning, interactive 3D web interface. Designed for engineers, students, and educators, this suite transforms complex beam analysis into an intuitive and visually engaging experience.


---

## ✨ Core Features

-   **🔬 Accurate Engineering Engine:**
    -   Performs precise calculations for Shear Force, Bending Moment, and Deflection.
    -   Supports a wide variety of loads: concentrated, distributed, and linearly varying.
    -   Built on a robust Python foundation with NumPy for high performance.

-   **🖥️ Interactive 3D Web Visualizer:**
    -   **Real-time Rendering:** Watch your beam, supports, and loads come to life in a 3D environment powered by **Three.js**.
    -   **Dynamic Charting:** Instantly visualize results with interactive charts for Shear Force, Bending Moment, and Deflection, rendered with **Chart.js**.
    -   **Intuitive UI:** A modern, responsive interface makes designing and analyzing complex configurations effortless.

-   **🐍 Classic Python GUI:**
    -   Includes the original robust desktop application for detailed analysis and generating high-resolution plots for reports.

## 📂 Project Architecture

```
Beam-Analyzer/
├── 📁 Python/         # Core analysis engine & original Python GUI
│   ├── main_gui.py
│   └── ...
├── 🌐 Web/             # 3D Web Visualizer (Flask Backend + JS Frontend)
│   ├── server.py
│   ├── 3d_beam_designer.html
│   └── beam_analysis_engine.js
├── .gitignore
└── 📄 README.md
```

## 🛠️ Getting Started

### Prerequisites

-   Python 3.9+
-   `pip` for package management

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Aaditya1273/Beam-Analyzer.git
    cd Beam-Analyzer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r Python/requirements.txt
    ```

## ▶️ How to Run

### 1. The 3D Web Visualizer (Recommended)

1.  **Start the Backend Server:**
    ```bash
    cd Web
    python server.py
    ```

2.  **Open the Frontend:**
    Open your web browser and go to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### 2. The Original Python GUI

1.  **Run the GUI script:**
    ```bash
    cd Python
    python main_gui.py
    ```

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request for:
-   New features (e.g., additional load types, material properties)
-   Bug fixes
-   Documentation improvements

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

<p align="center">Made with ❤️ for Structural Engineers and Students</p>
