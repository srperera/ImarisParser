# ImarisParser

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)]()
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

**ImarisParser** is a Python-based tool designed to extract structured statistical data from Imaris `.ims` microscopy files. It enables seamless integration into downstream analysis workflows such as FlowJo or custom scientific pipelines.

  * Version 1 can be found at: https://github.com/srperera/nih_parsers (no longer supported will be archived shortly.)
  * Version 2 (this repo) is 2x to 5x faster than Version 1

---

## ✨ Features
- **Metadata & Statistics Extraction**  
  Retrieve per-object and aggregate statistics from `.ims` files without recalculation.
  
- **Multiple Parser Modules**  
  Supports different types of exports:
  - Surface statistics
  - Tracking metrics
  - Time-step summaries
  - All tracks combined
  
- **Notebook-Driven Workflow**  
  Includes ready-to-use Jupyter notebooks for modular parsing and visualization.

---

## 🚀 Quick Start

### ✅ Prerequisites
- Python **3.10+**
- [Jupyter Notebook](https://jupyter.org/)
- Dependencies (managed via `pyproject.toml` or `requirements.txt`)

### 📥 Installation
```bash
# Clone the repository
git clone https://github.com/srperera/ImarisParser.git
cd ImarisParser

# Install dependencies
# Option 1: Install UV
wget -qO- https://astral.sh/uv/install.sh | sh

# Option 2: Using pip
pip install uv

# Install dependencices with (after you have installed uv)
uv sync 

# Activate provided virtual environment
source .venv/bin/activate
```


### 📥 Project Structure
```bash
ImarisParser/
├── LICENSE                # GPL-3.0 License
├── README.md              # Project documentation
├── pyproject.toml         # uv/Poetry dependency management
├── uv.lock                # uv lockfile for reproducible environments
├── parsers/
│   ├── parser.py          # Core parsing logic
│   └── config/
│       └── config.yaml    # Config file template
├── notebooks/
│   ├── surface_stats.ipynb
│   ├── track_stats.ipynb
│   └── time_step_parser.ipynb
└── tests/
    └── test_parser.py     # Unit tests
└── example/
    └── sample_output.csv     # An example of an output csv
```

## Citation
``` bibtex
@misc{ImarisParser2025,
  author       = {Shehan Perera, Juraj Kabat},
  title        = {ImarisParser: A Python tool for parsing Imaris .ims microscopy files},
  year         = {2025},
  publisher    = {GitHub},
  journal      = {GitHub repository},
  howpublished = {\url{https://github.com/srperera/ImarisParser}},
  note         = {Version 2.0},
}
```
