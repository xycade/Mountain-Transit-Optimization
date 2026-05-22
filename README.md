# Enhancing Bus-Rail Synergy in Mountainous Cities

This repository contains the official Python implementation for the paper: **"Enhancing Bus-Rail Synergy in Mountainous Cities: A Spatial Multi-Objective Optimization Framework for Transit Network Reconfiguration"**.

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
│   ├── Plot_Pareto_3D.py  # Generates the 3D Pareto Front (Figure 5)
│   ├── Plot_Multidimensional_Attribution.py  # Generates heatmaps and bar charts (Figure 6)
│   └── Plot_Hub_Topology_Evolution.py  # Generates topological fingerprints (Figure 9)
└── src/                   # Core computational modules
    ├── engine.py          # Super-network construction and topography logic
    ├── candidates.py      # Spatial search for detours and truncations
    ├── evaluator.py       # Multi-objective fitness calculations
    └── problem.py         # Chromosome encoding and decoding logic
