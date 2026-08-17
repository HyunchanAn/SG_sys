import sys
import os
import math
import numpy as np

# Add SG_proj_001 to path to import engine
sys.path.append(os.path.abspath("/Users/hyunchanan/Documents/GitHub/SG_proj_001"))
from sg_polysim.engine import RecipeOptimizer

def mock_013_feedback(target, pred, iteration):
    # dynamic damping from 013
    decay = 1.0 / math.sqrt(iteration)
    adjustments = {}
    
    # Adhesion
    diff_adhesion = target.get("측정_값", 1500) - pred.get("측정_값", 1500)
    delta_adhesion = diff_adhesion * 0.6 * decay
    delta_adhesion = max(-250, min(250, delta_adhesion))
    adjustments["측정_값"] = delta_adhesion
    
    # Tg
    diff_tg = target.get("Tg", -15) - pred.get("Tg", -15)
    delta_tg = diff_tg * 0.4 * decay
    delta_tg = max(-15, min(15, delta_tg))
    adjustments["Tg"] = delta_tg
    
    # Viscosity
    diff_visc = target.get("점도(cP)", 2000) - pred.get("점도(cP)", 2000)
    delta_visc = diff_visc * 0.5 * decay
    delta_visc = max(-1500, min(1500, delta_visc))
    adjustments["점도(cP)"] = delta_visc
    
    return adjustments

def calculate_residuals(target, pred):
    scale = {"측정_값": 2000.0, "점도(cP)": 5000.0, "Tg": 80.0}
    residuals = {}
    for k in scale.keys():
        residuals[k] = abs(pred[k] - target[k]) / scale[k]
    return residuals

def main():
    fixed_ctx = {'온도': 83.0, '반응시간': 5.0, '박리_각도': 180, '점착_기재': 'PET', '금속_표면': 'BA'}
    optimizer = RecipeOptimizer()
    
    # 10 test cases
    targets_list = [
        {"측정_값": 1500.0, "점도(cP)": 2000.0, "Tg": -15.0},
        {"측정_값": 1800.0, "점도(cP)": 3000.0, "Tg": -20.0},
        {"측정_값": 1200.0, "점도(cP)": 1500.0, "Tg": -10.0},
        {"측정_값": 2000.0, "점도(cP)": 4000.0, "Tg": -25.0},
        {"측정_값": 1000.0, "점도(cP)": 1000.0, "Tg": -5.0},
        {"측정_값": 1700.0, "점도(cP)": 2500.0, "Tg": -18.0},
        {"측정_값": 1400.0, "점도(cP)": 1800.0, "Tg": -12.0},
        {"측정_값": 2200.0, "점도(cP)": 5000.0, "Tg": -30.0},
        {"측정_값": 900.0, "점도(cP)": 800.0, "Tg": 0.0},
        {"측정_값": 1600.0, "점도(cP)": 2200.0, "Tg": -16.0},
    ]

    all_residuals = {"측정_값": [], "점도(cP)": [], "Tg": []}

    print("Running V3 Residual Analysis...")
    
    for case_idx, original_targets in enumerate(targets_list):
        np.random.seed(42 + case_idx)
        current_targets_B = original_targets.copy()
        
        best_err_B = float('inf')
        best_residuals = None
        initial_recipe = None
        
        for i in range(1, 6):
            if i == 1:
                recipe, pred, _ = optimizer.optimize_nsga2_smart(current_targets_B, fixed_ctx, pop_size=30, n_gen=30)
                initial_recipe = recipe
            else:
                recipe, pred = optimizer.optimize(current_targets_B, fixed_ctx, initial_recipe=initial_recipe, local_search_step=i-1)
                
            # calc error with standard L2 to find the best iteration
            residuals = calculate_residuals(original_targets, pred)
            err = math.sqrt(sum(v**2 for v in residuals.values()))
            
            if err < best_err_B:
                best_err_B = err
                best_residuals = residuals
                initial_recipe = recipe
                
            adj = mock_013_feedback(original_targets, pred, i)
            for k, v in adj.items():
                current_targets_B[k] += v
                
        # Record best residuals for this case
        for k in all_residuals.keys():
            all_residuals[k].append(best_residuals[k])
        print(f"Case {case_idx+1} Residuals: {best_residuals}")

    print("\n--- Summary Statistics ---")
    for k in all_residuals.keys():
        res_array = np.array(all_residuals[k])
        mean_val = np.mean(res_array)
        p75 = np.percentile(res_array, 75)
        p95 = np.percentile(res_array, 95)
        print(f"{k}: Mean={mean_val:.4f}, p75={p75:.4f}, p95={p95:.4f}")

    # Generate MD report
    import datetime
    date_str = datetime.datetime.now().strftime("%y%m%d_%H%M")
    report_path = f"/Users/hyunchanan/Documents/GitHub/SG_sys/{date_str}_residual_analysis.md"
    
    report = "# Milestone A - V3 Residual Analysis Report\n\n"
    report += "## 1. 개요\nMilestone B 가중치 결정을 위해 10개 테스트 케이스에 대한 물성별 잔차(오차/Scale) 분포를 분석합니다.\n\n"
    report += "## 2. 잔차 통계\n"
    report += "| 물성 | Mean | p75 | p95 |\n|---|---|---|---|\n"
    
    total_mean = sum(np.mean(np.array(all_residuals[k])) for k in all_residuals.keys())
    for k in all_residuals.keys():
        res_array = np.array(all_residuals[k])
        mean_val = np.mean(res_array)
        p75 = np.percentile(res_array, 75)
        p95 = np.percentile(res_array, 95)
        proportion = (mean_val / total_mean) * 100 if total_mean > 0 else 0
        report += f"| {k} | {mean_val:.4f} ({proportion:.1f}%) | {p75:.4f} | {p95:.4f} |\n"
        
    with open(report_path, "w") as f:
        f.write(report)
        
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    main()
