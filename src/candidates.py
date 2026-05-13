import networkx as nx
from itertools import islice

def generate_spatial_candidates(rid, data, G_base, G_penalty):
    """
    Generates topographically valid candidate paths for each bus route.
    Includes: Baseline, Anti-Overlap Detours, and Truncated Feeders.
    """
    base_path = data['full_path']
    base_stops = data['stop_pattern']
    O_node, D_node = base_path[0], base_path[-1]
    candidates = []

    # 1. Candidate 0: Baseline (Legacy Route)
    candidates.append({
        "cand_id": 0, "type": "Baseline", 
        "path": base_path, "stop_pattern": base_stops
    })

    # 2. Candidate 1: Anti-Overlap Detour
    # Uses G_penalty where rail-parallel edges have massive weights to force detours
    try:
        detour_path = nx.shortest_path(G_penalty, O_node, D_node, weight='weight')
        if detour_path != base_path:
            candidates.append({
                "cand_id": len(candidates), "type": "Detour", 
                "path": detour_path, "stop_pattern": [1.0] * len(detour_path)
            })
    except nx.NetworkXNoPath: pass

    # 3. Candidate 2: Truncated Feeder (Structural Mutation)
    # Cuts the route to convert long-haul routes into rail-feeders
    cut_idx = int(len(base_path) * 0.6)
    if cut_idx > 5:
        candidates.append({
            "cand_id": len(candidates), "type": "Truncation", 
            "path": base_path[:cut_idx], "stop_pattern": base_stops[:cut_idx]
        })

    # 4. Candidate 3: Structural Alternative (Yen's Algorithm)
    try:
        k_paths = islice(nx.shortest_simple_paths(G_base, O_node, D_node, weight='weight'), 1, 5)
        for alt_path in k_paths:
            # Ensure the alternative is structurally different from the baseline
            similarity = len(set(alt_path) & set(base_path)) / len(set(base_path))
            if similarity < 0.75:
                candidates.append({
                    "cand_id": len(candidates), "type": "Alternative", 
                    "path": alt_path, "stop_pattern": [1.0] * len(alt_path)
                })
                break
    except: pass
    
    return candidates