import networkx as nx
import pandas as pd
import pickle
import os

class SuperNetworkEngine:
    """
    Core engine to build the multi-layer directed hypernetwork.
    Handles topographic impedance and integrates pre-processed graph objects.
    """
    def __init__(self, nodes_df, edges_df, params):
        self.params = params
        self.nodes_df = nodes_df
        self.edges_df = edges_df
        self.G = nx.DiGraph()
        
        # Define paths
        self.pkl_path = os.path.join('data', 'guiyang_road_network_with_nodes.pkl')
        
        # Fast lookup dictionaries for edge attributes
        # These are used during the 'add_bus_line_layer' phase
        self.edge_time_lookup = edges_df.set_index(['FromNode', 'ToNode'])['TravelTime'].to_dict()
        self.edge_len_lookup = edges_df.set_index(['FromNode', 'ToNode'])['Length'].to_dict()
        self.edge_overlap_lookup = edges_df.set_index(['FromNode', 'ToNode'])['Overlap'].to_dict()

    def build_base_infrastructure(self):
        """
        Initializes the static layers (Rail, TAZ, Transfer).
        Priority is given to loading a pre-processed pickle file for speed.
        """
        if os.path.exists(self.pkl_path):
            try:
                with open(self.pkl_path, 'rb') as f:
                    self.G = pickle.load(f)
                print(f"[*] Performance Boost: Successfully loaded pre-processed network from {self.pkl_path}")
                return self.G
            except Exception as e:
                print(f"[!] Warning: Failed to load .pkl file ({e}). Falling back to CSV construction.")

        # Fallback logic: Build from CSV if .pkl is missing or corrupted
        self.G.clear()
        print("[*] Building infrastructure from CSV files...")
        
        # Add physical nodes
        for _, row in self.nodes_df.iterrows():
            self.G.add_node(int(row['nodeID']), type=row['type'])

        # Add bidirectional infrastructure edges
        for _, row in self.edges_df.iterrows():
            if row['type'] in ['rail', 'transfer', 'access']:
                u, v, t = int(row['FromNode']), int(row['ToNode']), float(row['TravelTime'])
                self.G.add_edge(u, v, weight=t, type=row['type'])
                self.G.add_edge(v, u, weight=t, type=row['type'])
        
        return self.G

    def add_bus_line_layer(self, G, rid_dir, path, stops, freq):
        """
        Injects a specific bus route layer into the super-network.
        Incorporates topography-aware travel times and dwell penalties.
        """
        # Boarding wait time based on frequency (30 / frequency)
        wait_time = 30.0 / freq if freq > 0.1 else 9999
        
        for i in range(len(path)):
            u = int(path[i])
            v_node = f"{rid_dir}_{u}" 
            
            if i > 0:
                prev_u = int(path[i-1])
                # Retrieve travel time (GIS-calculated including slope penalties)
                t = self.edge_time_lookup.get((prev_u, u), 9.0)
                # Dwell penalty (0.5 min) applied only to active stops
                dwell = 0.5 if stops[i] == 1 else 0
                G.add_edge(f"{rid_dir}_{prev_u}", v_node, weight=t + dwell)

            if stops[i] == 1:
                # Intermodal boarding and alighting links
                G.add_edge(u, v_node, weight=wait_time, type='boarding')
                G.add_edge(v_node, u, weight=0, type='alighting')