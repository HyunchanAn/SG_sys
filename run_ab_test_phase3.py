import os
import sys
import json
import time
import math
from typing import Dict

# Add SG_proj_001 to path to import engine directly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJ_001_DIR = os.path.join(BASE_DIR, "SG_proj_001")
sys.path.append(PROJ_001_DIR)

from sg_polysim.sg_polysim.engine import RecipeOptimizer

# Initialize optimizer
print("Loading RecipeOptimizer...")
optimizer = RecipeOptimizer()
print("Loaded!")

TEST_CASES = [
    {"target": {"측정_값": 850, "점도(cP)": 2000, "Tg": -15}, "finish": "Hairline", "diff": "Low"},
    {"target": {"측정_값": 1500, "점도(cP)": 4000, "Tg": -25}, "finish": "BA", "diff": "Med"},
    {"target": {"측정_값": 400, "점도(cP)": 1500, "Tg": -10}, "finish": "Mirror", "diff": "Low"},
    {"target": {"측정_값": 2500, "점도(cP)": 6000, "Tg": -35}, "finish": "BA", "diff": "High"},
    {"target": {"측정_값": 3000, "점도(cP)": 5000, "Tg": -40}, "finish": "Hairline", "diff": "High"},
    {"target": {"측정_값": 700, "점도(cP)": 2500, "Tg": -18}, "finish": "Mirror", "diff": "Low"},
    {"target": {"측정_값": 1800, "점도(cP)": 3500, "Tg": -22}, "finish": "Hairline", "diff": "Med"},
    {"target": {"측정_값": 2200, "점도(cP)": 4500, "Tg": -30}, "finish": "BA", "diff": "High"},
    {"target": {"측정_값": 900, "점도(cP)": 2200, "Tg": -20}, "finish": "BA", "diff": "Med"},
    {"target": {"측정_값": 1200, "점도(cP)": 3000, "Tg": -24}, "finish": "Mirror", "diff": "Med"}
]

GROUPS = {
    "A (Control)": {"weights": None, "bounds": False},
    "B1 (Weighted Only)": {"weights": {"측정_값": 0.5, "점도(cP)": 0.3, "Tg": 0.2}, "bounds": False},
    "B2 (Bounds Only)": {"weights": None, "bounds": True},
    "B3 (Final V3)": {"weights": {"측정_값": 0.45, "점도(cP)": 0.35, "Tg": 0.20}, "bounds": True} # using data_driven for B3
}

def calc_equal_l2(target, pred):
    scales = {"Tg": 80.0, "점도(cP)": 5000.0, "측정_값": 2000.0}
    err = 0.0
    for k in ["측정_값", "Tg", "점도(cP)"]:
        err += (abs(target[k] - pred.get(k, 0)) / scales[k]) ** 2
    return math.sqrt(err / 3.0)

def run_case(case: Dict, group_config: Dict) -> Dict:
    fixed_context = {
        "온도": 83,
        "반응시간": 5,
        "박리_각도": "180",
        "점착_기재": "BA",
        "금속_표면": case["finish"]
    }
    
    start_t = time.time()
    try:
        # optimize_nsga2_smart wrapper
        recipe, pred, source = optimizer.optimize_nsga2_smart(
            target_properties=case["target"],
            fixed_context=fixed_context,
            pop_size=30,
            n_gen=30,
            target_weights=group_config["weights"],
            use_property_bounds=group_config["bounds"]
        )
        latency = time.time() - start_t
        err = calc_equal_l2(case["target"], pred)
        return {"error": err, "latency": latency, "success": True, "pred": pred, "recipe": recipe, "source": source}
    except Exception as e:
        print(f"Error running case: {e}")
        latency = time.time() - start_t
        return {"error": 1.0, "latency": latency, "success": False, "pred": {}, "recipe": {}, "source": "error"}

def main():
    print("Starting A/B Benchmark (Phase 3)...")
    results = {g: {"errors": [], "latencies": [], "high_diff_wins": 0} for g in GROUPS}
    
    for i, case in enumerate(TEST_CASES):
        print(f"\\n--- Case {i+1} [Diff: {case['diff']}] Target: {case['target']} ---")
        
        case_results = {}
        for g_name, g_config in GROUPS.items():
            res = run_case(case, g_config)
            case_results[g_name] = res
            
            err = res["error"]
            lat = res["latency"]
            results[g_name]["errors"].append(err)
            results[g_name]["latencies"].append(lat)
            print(f"[{g_name}] Error: {err:.4f} | Latency: {lat:.2f}s | Source: {res.get('source')}")
            
        # Check high diff wins vs Control
        if case["diff"] == "High":
            control_err = case_results["A (Control)"]["error"]
            for g_name in ["B1 (Weighted Only)", "B2 (Bounds Only)", "B3 (Final V3)"]:
                if case_results[g_name]["error"] < control_err:
                    results[g_name]["high_diff_wins"] += 1
                    
    print("\\n================ SUMMARY ================")
    for g_name in GROUPS:
        avg_err = sum(results[g_name]["errors"]) / len(TEST_CASES)
        avg_lat = sum(results[g_name]["latencies"]) / len(TEST_CASES)
        high_wins = results[g_name]["high_diff_wins"]
        print(f"{g_name}:")
        print(f"  Avg Error (Equal L2): {avg_err:.4f}")
        print(f"  Avg Latency:          {avg_lat:.2f}s")
        print(f"  High-diff Wins:       {high_wins} / 3")

    with open("ab_test_phase3_report.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
