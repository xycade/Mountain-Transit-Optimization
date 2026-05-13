import json
import pandas as pd
import networkx as nx
from src.candidates import generate_spatial_candidates

def run_preprocessing():
    # 1. Load configuration and data
    with open('data/Params.json', 'r') as f: params = json.load(f)
    edges_df = pd.read_csv(params['Data_Paths']['edges_csv'])
    with open(params['Data_Paths']['lines_json'], 'r') as f: lines_raw = json.load(f)
        
    # 2. Build graphs for pathfinding
    G_base = nx.DiGraph()
    G_penalty = nx.DiGraph() # Topographic penalty graph
    for _, row in edges_df.iterrows():
        u, v, t, o = int(row['FromNode']), int(row['ToNode']), float(row['TravelTime']), int(row['Overlap'])
        G_base.add_edge(u, v, weight=t)
        # Apply geographic penalty to overlapping corridors
        G_penalty.add_edge(u, v, weight=t + o * 500.0) 

    # 3. Build candidate pool
    print("Generating clever candidate pool...")
    pool = {}
    for rid, data in lines_raw.items():
        pool[rid] = {
            "baseline_frequency": data['frequency'],
            "candidates": generate_spatial_candidates(rid, data, G_base, G_penalty)
        }
        
    with open('data/Candidate_Pool.json', 'w') as f: json.dump(pool, f, indent=4)
    print("✅ Pre-processing complete: Candidate_Pool.json saved.")

if __name__ == "__main__":
    run_preprocessing()