# Simulating-TCP-Congestion-Control-Streamlit-python-
# 🚦 TCP Congestion Control Visual Simulator

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.22.0-%23FF4B4B)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-streamlit-app-url.streamlit.app/)

A hands-on educational tool for comparing TCP Tahoe and Reno congestion control algorithms through interactive simulation.

![Demo Animation](docs/demo.gif)

## 📌 Key Features

- **Interactive Network Simulation**
  - Adjustable packet loss (1-30%)
  - Configurable RTT and window sizes
  - Real-time parameter tuning

- **Visual Comparison Tools**
  - Side-by-side algorithm performance
  - Animated congestion window growth
  - Packet loss event markers

- **Educational Resources**
  - Built-in algorithm explanations
  - RFC reference links
  - Exportable simulation data

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/tcp-congestion-simulator.git
cd tcp-congestion-simulator

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
