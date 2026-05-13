import networkx as nx
import math

class FastNetworkEvaluator:
    """
    Computes fitness for three objectives: 
    F1 (Efficiency), F2 (Economy), F3 (Synergy/Redundancy)
    """
    def __init__(self, engine, lines_pool, od_df, params):
        self.engine = engine
        self.lines_pool = lines_pool
        self.od_df = od_df
        self.params = params
        self.line_keys = list(lines_pool.keys())

    def evaluate_individual(self, current_network):
        # 1. Reconstruct Super-network snapshot for this individual
        G_eval = self.engine.build_base_infrastructure()
        
        total_mileage, total_overlap_mileage, total_buses = 0, 0, 0
        
        for rid, data in current_network.items():
            f, path, stops = data['freq'], data['path'], data['stops']
            self.engine.add_bus_line_layer(G_eval, rid + "_F", path, stops, f)
            
            # Calculate F3 (Frequency-Weighted Spatial Redundancy)
            route_len = sum(self.engine.edge_len_lookup.get((path[i-1], path[i]), 500) for i in range(1, len(path)))
            overlap_len = sum(self.engine.edge_len_lookup.get((path[i-1], path[i]), 0) 
                              for i in range(1, len(path)) 
                              if self.engine.edge_overlap_lookup.get((path[i-1], path[i]), 0) == 1)
            
            total_mileage += (route_len * 2 * f)
            total_overlap_mileage += (overlap_len * 2 * f)
            
            # Calculate F2 (Operator Cost via fleet size estimation)
            total_buses += math.ceil((route_len / 20 * 60 * 2.2) * (f / 60.0))

        # 2. Calculate F1 (Generalized Travel Time) using Dijkstra shortest path
        total_travel_time, satisfied_demand = 0, 0
        for origin in self.od_df['OriginID'].unique():
            lengths = nx.single_source_dijkstra_path_length(G_eval, int(origin), weight='weight', cutoff=120)
            sub_od = self.od_df[self.od_df['OriginID'] == origin]
            for _, row in sub_od.iterrows():
                dest, demand = int(row['DestinationID']), float(row['Demand_B'])
                if dest in lengths:
                    total_travel_time += lengths[dest] * demand
                    satisfied_demand += demand

        f1_efficiency = total_travel_time / satisfied_demand if satisfied_demand > 0 else 9999
        f2_cost = total_buses * 120 + (total_mileage / 1000.0) * 0.18
        f3_overlap = total_overlap_mileage / total_mileage if total_mileage > 0 else 1.0
        coverage = satisfied_demand / self.od_df['Demand_B'].sum()
        
        return f1_efficiency, f2_cost, f3_overlap, coverage