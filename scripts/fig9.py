import json
import pandas as pd
import networkx as nx
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# ==============================================================================
# 1. Academic Figure Parameter Settings (Times New Roman, DPI=500, 2x3 layout)
# ==============================================================================
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['mathtext.fontset'] = 'stix'  # For elegant LaTeX rendering

# Uniform academic color (Slate Blue)
MAIN_COLOR = '#2C3E50'


# ==============================================================================
# 2. Data Processing and Topological Metric Computation
# ==============================================================================
def calculate_hub_metrics(edges_path, nodes_path, scenarios_dict):
    print("Loading base network and establishing transfer mappings...")
    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)

    # Standardize types
    nodes_df['type'] = nodes_df['type'].astype(str).str.strip().str.upper()
    edges_df['type'] = edges_df['type'].astype(str).str.strip().str.upper()

    rail_nodes = set(nodes_df[nodes_df['type'] == 'RAIL_S']['nodeID'])
    bus_nodes = set(nodes_df[nodes_df['type'] == 'BUS_S']['nodeID'])

    # Build mapping: Gateway Bus Stop -> Parent Subway Hub
    bus_to_rail_map = {}
    transfer_edges = edges_df[edges_df['type'] == 'TRANSFER']
    for _, row in transfer_edges.iterrows():
        u, v = int(row['FromNode']), int(row['ToNode'])
        if u in rail_nodes and v in bus_nodes:
            bus_to_rail_map[v] = u
        elif v in rail_nodes and u in bus_nodes:
            bus_to_rail_map[u] = v

    results = []

    for scen_name, json_path in scenarios_dict.items():
        print(f"Computing topological fingerprints for Scenario: {scen_name}...")
        with open(json_path, 'r', encoding='utf-8') as f:
            lines_data = json.load(f)

        G = nx.Graph()
        # Ensure all rail nodes exist in the graph (even if isolated with degree 0)
        G.add_nodes_from(rail_nodes)

        for rid, data in lines_data.items():
            freq = float(data.get('frequency', 0))
            path = [int(i) for i in data.get('full_path', [])]
            stops = data.get('stop_pattern', [])

            if freq < 0.1 or not path: continue

            # Extract actual stopping nodes
            active_stops = [path[i] for i in range(len(path)) if int(stops[i]) == 1]

            # Map bus stops to their corresponding rail hubs
            mapped_stops = [bus_to_rail_map.get(s, s) for s in active_stops]

            # Build edges weighted by service frequency
            for i in range(len(mapped_stops) - 1):
                u, v = mapped_stops[i], mapped_stops[i + 1]
                if u == v: continue  # Skip self-loops

                if G.has_edge(u, v):
                    G[u][v]['frequency'] += freq
                else:
                    G.add_edge(u, v, frequency=freq)

        # Compute core indicators
        # 1. Hub Strength (Weighted degree)
        strength_dict = dict(G.degree(weight='frequency'))

        # 2. Weighted Clustering Coefficient (Weighted local clustering)
        clustering_dict = nx.clustering(G, nodes=rail_nodes, weight='frequency')

        for r_node in rail_nodes:
            s_i = strength_dict.get(r_node, 0.0)
            c_i = clustering_dict.get(r_node, 0.0)
            results.append({
                'Scenario': scen_name,
                'Rail_ID': r_node,
                'Strength': s_i,
                'Clustering': c_i
            })

    return pd.DataFrame(results)


# ==============================================================================
# 3. Plot 2x3 Advanced Figure (High DPI, Enhanced Contrasts)
# ==============================================================================
def plot_topology_evolution(df, output_path):
    # Global Font Size Enlargement for supreme readability
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    plt.rcParams['xtick.labelsize'] = 15
    plt.rcParams['ytick.labelsize'] = 15

    scen_order = ['Base', 'SP', 'CA', 'HS', 'BD']

    # Auto-adjust axes limits
    x_max = df['Strength'].max() * 1.05
    y_max = df['Clustering'].max() * 1.15

    # Determine 75th percentile baselines based on the Base scenario
    base_df = df[df['Scenario'] == 'Base']
    base_s_thresh = base_df['Strength'].quantile(0.75)
    base_c_thresh = base_df['Clustering'].quantile(0.75)
    if base_c_thresh == 0: base_c_thresh = 0.01

    # Create 2x3 canvas
    fig, axes = plt.subplots(2, 3, figsize=(18, 11), dpi=500)
    axes = axes.flatten()
    axes[5].axis('off')  # Hide the empty 6th panel

    for i, scen in enumerate(scen_order):
        ax = axes[i]
        scen_df = df[df['Scenario'] == scen]

        x_data = scen_df['Strength']
        y_data = scen_df['Clustering']

        # A. Plot Darker & Smoother KDE Density Shadows (FIXED: alpha=0.35, levels=8)
        sns.kdeplot(x=x_data, y=y_data, ax=ax,
                    color=MAIN_COLOR, fill=True, alpha=0.35,  # Darker alpha for perfect visibility
                    levels=8, thresh=0.05, cut=0, clip=((0, None), (0, None)),
                    warn_singular=False, zorder=1)

        # B. Plot scatter points with highlighted white outline (edge width = 1.2)
        ax.scatter(x_data, y_data, color=MAIN_COLOR, edgecolor='white',
                   linewidth=1.2, s=95, alpha=0.90, zorder=3)

        # C. Plot 75th percentile baseline indicators
        ax.axvline(base_s_thresh, color='#7F8C8D', linestyle='--', linewidth=1.5, alpha=0.7, zorder=2)
        ax.axhline(base_c_thresh, color='#7F8C8D', linestyle='--', linewidth=1.5, alpha=0.7, zorder=2)

        # D. Sub-plot Title (Font Size = 22)
        ax.set_title(scen, fontweight='bold', fontsize=22, pad=15)

        ax.set_xlim(-5, x_max)
        ax.set_ylim(-0.005, y_max)

        # Aesthetics
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#333333')
        ax.spines['bottom'].set_color('#333333')
        ax.spines['left'].set_linewidth(1.5)
        ax.spines['bottom'].set_linewidth(1.5)

        ax.grid(True, linestyle=':', color='#E0E0E0', alpha=0.8, zorder=0)

        # E. Axis Labels (Font Size = 18)
        ax.set_ylabel('Weighted Clustering', fontweight='bold', fontsize=18)
        ax.set_xlabel('Hub Strength', fontweight='bold', fontsize=18)

        # F. Quadrant Annotations (Font Size = 15)
        ax.text(x_max * 0.95, y_max * 0.92, "Synergistic\nHub-and-Spoke",
                ha='right', va='top', fontsize=15, color='#2C3E50', fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=3))

        ax.text(base_s_thresh * 0.5, base_c_thresh * 0.5, "Isolated /\nBypass",
                ha='center', va='center', fontsize=14, color='#7F8C8D',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=3))

    # Clean layout wrapping
    plt.tight_layout(pad=2.0, w_pad=3.0, h_pad=3.0)

    # Save to relative path
    os.makedirs('results', exist_ok=True)
    plt.savefig(output_path, format='png', dpi=600, bbox_inches='tight')
    print(f"\n✅ High-contrast topological evolution figure successfully saved to: {output_path}")


# ==============================================================================
# 4. Execution Area (Using Relative Paths)
# ==============================================================================
if __name__ == '__main__':
    EDGES_CSV = 'data/Edges.csv'
    NODES_CSV = 'data/Nodes.csv'

    SCENARIOS_JSON = {
        'Base': 'data/Baseline_Lines_With_Freq.json',
        'SP': 'results/Optimized_Lines_Service_Priority_SP.json',
        'CA': 'results/Optimized_Lines_Cost_Austerity_CA.json',
        'HS': 'results/Optimized_Lines_High_Synergy_HS.json',
        'BD': 'results/Optimized_Lines_Balanced_BD.json'
    }

    OUTPUT_IMG = 'results/Figure_9_Topology_Evolution.png'

    # Compute & Plot
    df_metrics = calculate_hub_metrics(EDGES_CSV, NODES_CSV, SCENARIOS_JSON)
    plot_topology_evolution(df_metrics, OUTPUT_IMG)