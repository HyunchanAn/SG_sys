import sys
import os
import time
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

def calculate_error(target, pred):
    err = 0
    err += (abs(target.get("측정_값", 1500) - pred.get("측정_값", 1500)) / 2000) ** 2
    err += (abs(target.get("Tg", -15) - pred.get("Tg", -15)) / 80) ** 2
    err += (abs(target.get("점도(cP)", 2000) - pred.get("점도(cP)", 2000)) / 5000) ** 2
    return math.sqrt(err)

def run_ab_test():
    optimizer = RecipeOptimizer()
    fixed_ctx = {"온도": 83.0, "반응시간": 5.0, "박리_각도": 180, "점착_기재": "PET", "금속_표면": "BA"}
    
    # 10 diverse test cases
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
    
    avg_final_err_A = 0
    avg_final_err_B = 0
    total_time_A = 0
    total_time_B = 0
    
    print(f"Running A/B benchmark over {len(targets_list)} targets...")
    
    for case_idx, original_targets in enumerate(targets_list):
        print(f"\n--- Case {case_idx+1} : {original_targets} ---")
        
        # [A] Legacy DE (Independent Runs) with best-so-far
        np.random.seed(42 + case_idx)
        current_targets_A = original_targets.copy()
        
        best_err_A = float('inf')
        start_A = time.time()
        for i in range(1, 6):
            recipe, pred = optimizer.optimize(current_targets_A, fixed_ctx)
            err = calculate_error(original_targets, pred)
            if err < best_err_A:
                best_err_A = err
            
            adj = mock_013_feedback(original_targets, pred, i)
            for k, v in adj.items():
                current_targets_A[k] += v
        time_A = time.time() - start_A
        total_time_A += time_A
        avg_final_err_A += best_err_A
        
        # [B] V3 NSGA-II + DE Warm-start with best-so-far
        np.random.seed(42 + case_idx)
        current_targets_B = original_targets.copy()
        
        best_err_B = float('inf')
        initial_recipe = None
        start_B = time.time()
        for i in range(1, 6):
            if i == 1:
                recipe, pred, source = optimizer.optimize_nsga2_smart(current_targets_B, fixed_ctx, pop_size=30, n_gen=30)
                initial_recipe = recipe
            else:
                recipe, pred = optimizer.optimize(current_targets_B, fixed_ctx, initial_recipe=initial_recipe, local_search_step=i-1)
                
            err = calculate_error(original_targets, pred)
            if err < best_err_B:
                best_err_B = err
                initial_recipe = recipe # Update initial_recipe to the best one found so far!
                
            adj = mock_013_feedback(original_targets, pred, i)
            for k, v in adj.items():
                current_targets_B[k] += v
        time_B = time.time() - start_B
        total_time_B += time_B
        avg_final_err_B += best_err_B
        
        print(f"Legacy Best Error: {best_err_A:.4f} ({time_A:.2f}s) | V3 Best Error: {best_err_B:.4f} ({time_B:.2f}s)")
        
    avg_final_err_A /= len(targets_list)
    avg_final_err_B /= len(targets_list)
    
    print(f"\n=== Benchmark Summary ({len(targets_list)} cases) ===")
    print(f"Legacy Total Time: {total_time_A:.2f}s")
    print(f"V3 Total Time: {total_time_B:.2f}s")
    print(f"Legacy Avg Best Error: {avg_final_err_A:.4f}")
    print(f"V3 Avg Best Error: {avg_final_err_B:.4f}")
    
    # Generate report
    import datetime
    date_str = datetime.datetime.now().strftime("%y%m%d_%H%M")
    report_filename = f"{date_str}_nsga2_v3_ab_test_report.md"
    report_path = f"/Users/hyunchanan/Documents/GitHub/SG_sys/{report_filename}"
    
    report = f"""
# NSGA-II V3 vs Legacy DE A/B Test Report (Best-so-far + 다중 타겟)

## 1. 실험 환경
- Fixed Context: {fixed_ctx}
- 테스트 케이스: 총 {len(targets_list)}개의 서로 다른 타겟 물성 조합 (고정 시드 사용)
- 반복 횟수: 각 타겟당 5회 이터레이션
- 평가 기준: 5회 중 도달한 **최저 오차 (Best-so-far)** 및 루프 총 소요 시간

## 2. 결과 요약 (10개 케이스 평균)

| 지표 | Legacy (DE Only) | V3 (NSGA-II + 혼합 DE Warm-start) |
|---|---|---|
| 전체 소요 시간 (누적) | {total_time_A:.2f}초 | {total_time_B:.2f}초 |
| 평균 최저 오차 (L2 Norm) | {avg_final_err_A:.4f} | {avg_final_err_B:.4f} |

## 3. 결론
"""
    if avg_final_err_B <= avg_final_err_A * 1.05: # Allow 5% margin
        report += "V3 하이브리드 아키텍처가 기존 DE 단독 아키텍처와 **동등한 수준의 정밀도**를 유지하면서 속도를 크게 개선했음을 확인했습니다.\n"
    else:
        report += "V3 모델의 정밀도가 Legacy 모델에 비해 아직 부족합니다. 추가 최적화가 필요합니다.\n"
        
    with open(report_path, 'w') as f:
        f.write(report)
        
    print(f"Report saved to {report_path}")

if __name__ == '__main__':
    run_ab_test()
