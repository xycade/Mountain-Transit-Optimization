# Enhancing Bus-Rail Synergy in Mountainous Cities

![Optimization Framework](https://via.placeholder.com/1000x400?text=Please+Upload+Your+Figure+4+Here+And+Replace+This+Link)

This repository contains the official Python implementation for the paper: **"Enhancing Bus–Rail Synergy in Mountainous Cities: A Geography-Aware Multi-Objective Optimization Framework for Transit Network Reconfiguration"** *(Currently under review in Computers, Environment and Urban Systems)*.

The repository provides a spatially explicit multi-objective optimization model designed to structurally reconfigure legacy surface bus networks under severe topographical constraints, promoting synergy with high-capacity rail transit.

## 🌟 Key Innovations
- **Frequency-Weighted Spatial Redundancy (FWSR) Index**: An active design constraint that transitions intermodal overlap from a passive metric into a driver of spatial network evolution.
- **Tripartite Mixed-Integer Chromosome**: A novel encoding strategy utilizing *dummy gene padding* to mathematically represent variable-length physical paths under restricted topographies.
- **The "Price of Synergy" Formalization**: Quantifies the non-linear relationship between strict intermodal separation and topographical friction (circuity/costs).

## 📂 Project Structure
```text
/
├── main_init.py           # Module 1: Pre-processing & Candidate Path Pool Generation
├── main_optimize.py       # Module 3: Parallelized NSGA-II Optimization Engine
├── requirements.txt       # Environment dependencies
├── LICENSE                # MIT License
├── data/                  # Input datasets
│   ├── Edges.csv          # Road/Rail network links with overlap tags
│   ├── Nodes.csv          # Stop/Station coordinates and types
│   ├── OD_Matrix.csv      # Synthesized Origin-Destination demand
│   ├── Params.json        # Global hyper-parameters and cost weights
│   ├── Baseline_Lines_With_Freq.json  # Pre-processed baseline network
│   └── guiyang_road_network_with_nodes.pkl  # Pickled graph for performance boost
├── results/               # Optimization outputs & scenario blueprints
│   ├── Pareto_Front_Solutions.csv  # Objective values of the Pareto set
│   ├── Optimized_Lines_Balanced_BD.json
│   ├── Optimized_Lines_Cost_Austerity_CA.json
│   ├── Optimized_Lines_High_Synergy_HS.json
│   └── Optimized_Lines_Service_Priority_SP.json
├── scripts/               # Publication figure replication scripts
│   ├── fig5.py  # Generates the 3D Pareto Front (Figure 5)
│   ├── fig6.py  # Generates heatmaps and bar charts (Figure 6)
│   └── fig9.py  # Generates topological fingerprints (Figure 9)
└── src/                   # Core computational modules
    ├── engine.py          # Super-network construction and topography logic
    ├── candidates.py      # Spatial search for detours and truncations
    ├── evaluator.py       # Multi-objective fitness calculations
    └── problem.py         # Chromosome encoding and decoding logic
```

## 🚀 Getting Started

1. Installation
Clone this repository and install the required dependencies (Python 3.8+ recommended):
git clone https://github.com/xycade/Mountain-Transit-Optimization.git
cd Mountain-Transit-Optimization
pip install -r requirements.txt

2. Pre-processing & Path Generation
Run the spatial candidate generator to produce the topography-aware candidate route pool:
python main_init.py
This script reads the raw GIS network from the data/ directory and outputs data/Candidate_Pool.json.

3. Optimization
Execute the parallelized evolutionary engine to search the spatiotemporal decision space:
python main_optimize.py
This script utilizes joblib for parallel evaluations across multiple CPU cores. The complete Pareto set and the four isolated policy scenarios (SP, CA, HS, BD) will be saved in the results/ folder.

4. Reproducing Paper Figures
You can directly replicate the core visualization plots in our paper using the pre-computed results provided in this repository:
To plot the 3D Pareto-optimal Front (Figure 5):
python scripts/fig5.py
To plot the Multidimensional Performance Heatmap & Strategy Attribution (Figure 6):
python scripts/fig6.py
To plot the Hub Topological Fingerprints (Figure 9):
python scripts/fgi9.py

## 📝 Citation

If you find this research or codebase useful, please cite our paper:
@article{MountainTransit2026,
  title={Enhancing Bus--Rail Synergy in Mountainous Cities: A Geography-Aware Multi-Objective Optimization Framework for Transit Network Reconfiguration},
  author={[Yucheng Xu], [Hang Zhao], [Lingya Zhang] and [Yixuan Feng]},
  journal={Computers, Environment and Urban Systems},
  note={Under review},
  year={2026}}

## ⚖️ License

This project is licensed under the MIT License - see the LICENSE file for details.
