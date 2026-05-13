import numpy as np
import json
import pandas as pd
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from joblib import Parallel, delayed
from src.engine import SuperNetworkEngine
from src.evaluator import FastNetworkEvaluator
from src.problem import TransitReconfigProblem

def run_nsga2_optimization():
    # 1. Setup Environment
    with open('data/Params.json', 'r') as f: params = json.load(f)
    nodes = pd.read_csv(params['Data_Paths']['nodes_csv'])
    edges = pd.read_csv(params['Data_Paths']['edges_csv'])
    od = pd.read_csv(params['Data_Paths']['od_base_csv'])
    with open('data/Candidate_Pool.json', 'r') as f: pool = json.load(f)

    # 2. Initialize Core Components
    engine = SuperNetworkEngine(nodes, edges, params)
    evaluator = FastNetworkEvaluator(engine, pool, od, params)
    problem = TransitReconfigProblem(evaluator)

    # 3. Define Parallel Evaluation Function
    def parallel_fitness_evaluation(X, out, *args, **kwargs):
        def evaluate_single_config(x):
            current_network = problem.decode_chromosome(x)
            return evaluator.evaluate_individual(current_network)
        
        # Execute fitness evaluations in parallel across all CPU cores
        raw_results = Parallel(n_jobs=-1)(delayed(evaluate_single_config)(x) for x in X)
        
        out["F"] = np.array([[r[0], r[1], r[2]] for r in raw_results]) # Objectives
        out["G"] = np.array([[0.85 - r[3]] for r in raw_results])       # Constraint: Min demand coverage

    # Inject the parallel logic into the Pymoo problem
    problem._evaluate = parallel_fitness_evaluation

    # 4. Configure and Execute NSGA-II
    print("Starting NSGA-II optimization engine...")
    algorithm = NSGA2(pop_size=100)
    res = minimize(problem, algorithm, termination=('n_gen', 200), seed=42, verbose=True)

    # 5. Export Results
    pd.DataFrame(res.F, columns=['F1_Efficiency','F2_Economy','F3_Synergy']).to_csv('results/Pareto_Front.csv')
    print("🎉 Optimization complete! Pareto front results saved to results/ directory.")

if __name__ == "__main__":
    run_nsga2_optimization()