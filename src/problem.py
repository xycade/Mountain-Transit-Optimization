import numpy as np
from pymoo.core.problem import Problem

class TransitReconfigProblem(Problem):
    """
    Defines the multi-objective optimization problem for Pymoo.
    Implements the 'Tripartite Chromosome' to handle variable-length paths.
    """
    def __init__(self, evaluator):
        self.ev = evaluator
        self.line_keys = evaluator.line_keys
        
        # Determine gene offsets for Dummy Gene Padding
        self.stop_gene_offsets = {}
        total_stop_genes = 0
        route_upper_bounds = []
        
        for rid in self.line_keys:
            cands = evaluator.lines_pool[rid]['candidates']
            route_upper_bounds.append(len(cands) - 0.01)
            # Find max stops possible for this route across all candidates (Padding)
            max_len = max(len(c['stop_pattern']) for c in cands)
            self.stop_gene_offsets[rid] = (total_stop_genes, max_len)
            total_stop_genes += max_len
            
        self.n_freq = len(self.line_keys)
        self.n_route = len(self.line_keys)
        self.n_stops = total_stop_genes
        
        # Lower and Upper bounds for the mixed-integer chromosome
        xl = [2.0] * self.n_freq + [0.0] * self.n_route + [0.0] * self.n_stops
        xu = [15.0] * self.n_freq + route_upper_bounds + [1.0] * self.n_stops
        
        super().__init__(n_var=len(xl), n_obj=3, n_ieq_constr=1, xl=xl, xu=xu)

    def decode_chromosome(self, x):
        """
        Splits the flat array into Frequency, Route Choice, and Stop Pattern segments.
        Implements Dummy Gene Padding: Reads only active genes for the selected path.
        """
        freq_genes = x[:self.n_freq]
        route_genes = x[self.n_freq : self.n_freq + self.n_route]
        stop_genes = x[self.n_freq + self.n_route:]
        
        network_manifest = {}
        for i, rid in enumerate(self.line_keys):
            r_idx = int(route_genes[i])
            chosen_cand = self.ev.lines_pool[rid]['candidates'][r_idx]
            
            offset, max_len = self.stop_gene_offsets[rid]
            # Padding Logic: Read only the relevant portion of the stop genes
            relevant_genes = stop_genes[offset : offset + len(chosen_cand['stop_pattern'])]
            
            actual_stops = []
            for j, is_stoppable in enumerate(chosen_cand['stop_pattern']):
                if is_stoppable == 1:
                    actual_stops.append(1 if relevant_genes[j] > 0.5 else 0)
                else:
                    actual_stops.append(0)
            
            network_manifest[rid] = {
                'freq': freq_genes[i], 'path': chosen_cand['path'], 'stops': actual_stops
            }
        return network_manifest