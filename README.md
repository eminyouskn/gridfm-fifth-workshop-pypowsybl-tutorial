# PyPowSyBl Tutorial — GridFM Workshop

Hands-on power system analysis with [PyPowSyBl](https://pypowsybl.readthedocs.io/).

## Contents

| File | Description |
|------|-------------|
| `01-load-grids.ipynb` | Load and explore five test grids of increasing complexity |
| `02-load-flow.ipynb` | Comprehensive AC/DC load flow tutorial (solvers, convergence, slack distribution, tap changers, HVDC, …) |
| `helpers.py` | Shared helper functions (network loaders, plotting utilities) |
| `data/` | Test grid data files (CGMES, Matpower) |

## Quick Start

### Google Colab

1. Upload this folder to your Google Drive
2. Open a notebook in Colab
3. Run the first cell to install dependencies (`!pip install pypowsybl …`)
4. Upload `helpers.py` and the `data/` folder to the Colab working directory

### Local

```bash
python -m venv venv && source venv/bin/activate
pip install pypowsybl pypowsybl-jupyter matplotlib pandas numpy
jupyter lab
```

## Requirements

- Python ≥ 3.10
- pypowsybl ≥ 1.9
- pypowsybl-jupyter
- matplotlib, pandas, numpy
