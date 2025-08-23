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
  abstract  = "In murine models of visceral leishmaniasis (VL), the
               parasitization of resident Kupffer cells (resKCs) drives early
               Leishmania infantum growth in the liver, leading to granuloma
               formation and subsequent parasite control. Using the chronic VL
               model, we demonstrate that polyclonal resKCs redistributed to
               form granulomas outside the sinusoids, creating an open
               sinusoidal niche that was gradually repopulated by
               monocyte-derived KCs (moKCs) acquiring a tissue specific,
               homeostatic profile. Early-stage granulomas predominantly
               consisted of CLEC4F+KCs. In contrast, late-stage granulomas led
               to remodeling of the sinusoidal network and contained
               monocyte-derived macrophages (momacs) along with KCs that
               downregulated CLEC4F, with both populations expressing iNOS and
               pro-inflammatory chemokines. During late-stage infection,
               parasites were largely confined to CLEC4F-KCs. Reduced monocyte
               recruitment and increased resKCs proliferation in infected
               Ccr2-/- mice impaired parasite control. These findings show that
               the ontogenic heterogeneity of granuloma macrophages is closely
               linked to granuloma maturation and the development of hepatic
               immunity in VL.",
  journal   = "Nat. Commun.",
  publisher = "Springer Science and Business Media LLC",
  volume    =  16,
  number    =  1,
  pages     = "3125",
  month     =  apr,
  year      =  2025,
  copyright = "https://creativecommons.org/licenses/by/4.0",
  language  = "en"
}
```
