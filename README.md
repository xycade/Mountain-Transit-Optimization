# Enhancing Bus-Rail Synergy in Mountainous Cities

This repository contains the source code for the paper: **"Enhancing Bus-Rail Synergy in Mountainous Cities: A Spatial Multi-Objective Optimization Framework for Transit Network Reconfiguration"**.

The framework addresses the Transit Network Design Problem (TNDP) in topographically constrained environments (e.g., karst topography) using a geography-aware Spatial Decision-Support System (SDSS).

## 🌟 Key Innovations
- **Frequency-Weighted Spatial Redundancy (FWSR) Index**: An active design constraint that transitions intermodal overlap from a passive metric into a driver of network evolution.
- **Tripartite Mixed-Integer Chromosome**: A novel encoding strategy utilizing **Dummy Gene Padding** to resolve the challenge of variable-length physical paths.
- **Multi-Scenario Decision Support**: Explicitly identifies the "Price of Synergy" and provides a blueprint for Balanced Development (BD).

## 📂 Project Structure
```text
/
├── main_init.py           # Module 1: Pre-processing & Candidate Path Generation
├── main_optimize.py       # Module 3: NSGA-II Optimization Engine
├── requirements.txt       # Environment dependencies
├── data/                  # Input data files
│   ├── Edges.csv          # Road/Rail network links with overlap tags
│   ├── Nodes.csv          # Stop/Station coordinates and types
│   ├── OD_Matrix.csv      # Synthesized Origin-Destination demand
│   ├──Params.json        # Global hyper-parameters and cost weights
│   └── guiyang_road_network_with_nodes.pkl  # Pre-processed graph object for performance
├── results/               # Output directory for Pareto Front solutions
└── src/                   # Core computational modules
    ├── engine.py          # Super-network construction and topography logic
    ├── candidates.py      # Spatial search for detours and truncations
    ├── evaluator.py       # Multi-objective fitness calculations
    └── problem.py         # Chromosome encoding and decoding logic
