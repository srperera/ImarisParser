# ImarisParser

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)]()
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

**ImarisParser** is a Python-based tool designed to extract structured statistical data from Imaris `.ims` microscopy files. It enables seamless integration into downstream analysis workflows such as FlowJo or custom scientific pipelines.

  * Version 1 can be found at: https://github.com/srperera/nih_parsers (no longer supported will be archived shortly.)
  * Version 2 (this repo) is significantly faster than version 1 across all supported formats. 

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

- **Minimal Dependencies**
  Written in pure Python +few external libraries.

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

## Used In Following Published Journals/Conference Papers
```bibtex
Note: Version 1 was used in this paper. Version 2 (this repo) is an improved version of version 1.

@ARTICLE{Pessenda2025-jb,
  title     = "Kupffer cell and recruited macrophage heterogeneity orchestrate
               granuloma maturation and hepatic immunity in visceral
               leishmaniasis",
  author    = "Pessenda, Gabriela and Ferreira, Tiago R and Paun, Andrea and
               Kabat, Juraj and Amaral, Eduardo P and Kamenyeva, Olena and
               Gazzinelli-Guimaraes, Pedro Henrique and Perera, Shehan R and
               Ganesan, Sundar and Lee, Sang Hun and Sacks, David L",
  journal   = "Nature Communications.",
  publisher = "Springer Science and Business Media LLC",
  month     =  apr,
  year      =  2025,
}

----------------------------------------------------------------

@ARTICLE{10.4049/jimmunol.212.supp.0341.4528,
    author = {Pessenda, Gabriela and Ferreira, Tiago and Paun, Andrea and Amaral, Eduardo and Kabat, Juraj and Kamenyeva, Olena and Ganesan, Sundar and Lee, Sang and Perera, Shehan and Sacks, David},
    title = {Kupffer cell replacement by monocyte-derived cells and granuloma heterogeneity improve visceral leishmaniasis control},
    journal = {The Journal of Immunology},
    year = {2024},
    month = {05},
    doi = {10.4049/jimmunol.212.supp.0341.4528},
    url = {https://doi.org/10.4049/jimmunol.212.supp.0341.4528},
}

----------------------------------------------------------------

@ARTICLE{Foreman2022-nk,
  title     = "{CD4} {T} cells are rapidly depleted from tuberculosis
               granulomas following acute {SIV} co-infection",
  author    = "Foreman, Taylor W and Nelson, Christine E and Kauffman, Keith D
               and Lora, Nickiana E and Vinhaes, Caian L and Dorosky, Danielle
               E and Sakai, Shunsuke and Gomez, Felipe and Fleegle, Joel D and
               Parham, Melanie and Perera, Shehan R and Lindestam Arlehamn,
               Cecilia S and Sette, Alessandro and {Tuberculosis Imaging
               Program} and Brenchley, Jason M and Queiroz, Artur T L and
               Andrade, Bruno B and Kabat, Juraj and Via, Laura E and Barber,
               Daniel L",
  journal   = "Cell Reports",
  publisher = "Elsevier BV",
  month     =  may,
  year      =  2022,
}


```
