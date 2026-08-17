import sys
import os
import copy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../SG_proj_001')))

from sg_polysim.engine import RecipeOptimizer, calc_weighted_l2

def mock_013_verify(recipe, target_properties, predicted_properties, current_iteration):
    # Dummy verification: just return the error rates and a feedback signal
    # In reality, 013 might adjust targets
    error = calc_weighted_l2(target_properties, predicted_properties)
    is_passed = error < 0.1
    return {
        "is_passed": is_passed,
        "error": error,
        # Fake a target adjustment for iteration 2+ if not passed
        "feedback_signal": {"target_adjustments": {k: v * 1.01 for k, v in target_properties.items()}} if not is_passed else None
    }

def run_full_loop(optimizer, targets, use_property_bounds, target_weights):
    current_targets = copy.deepcopy(targets)
    fixed_ctx = {"AA": 1.0, "2-HEMA": 1.0}
    
    best_recipe_so_far = None
    min_error_so_far = float('inf')
    best_preds_so_far = None
    
    initial_recipe = None
    
    for iteration in range(1, 6): # 5 iterations
        if iteration == 1:
            recipe, preds, _ = optimizer.optimize_nsga2_smart(
                target_properties=current_targets,
                fixed_context=fixed_ctx,
                target_weights=target_weights,
                use_property_bounds=use_property_bounds
            )
        else:
            local_search_step = iteration - 1
            recipe, preds = optimizer.optimize(
                target_properties=current_targets,
                fixed_context=fixed_ctx,
                initial_recipe=initial_recipe,
                local_search_step=local_search_step,
                target_weights=target_weights,
                use_property_bounds=use_property_bounds
            )[:2]
            
        initial_recipe = recipe
        
        # calculate true error against original targets (not adjusted)
        error = calc_weighted_l2(targets, preds, weights=target_weights)
        if error < min_error_so_far:
            min_error_so_far = error
            best_recipe_so_far = recipe
            best_preds_so_far = preds
            
        verify_res = mock_013_verify(recipe, current_targets, preds, iteration)
        if verify_res["is_passed"]:
            break
            
        if verify_res["feedback_signal"] and "target_adjustments" in verify_res["feedback_signal"]:
            current_targets = verify_res["feedback_signal"]["target_adjustments"]
            
    return min_error_so_far, best_recipe_so_far

def run_smoke_ab():
    optimizer = RecipeOptimizer()
    
    test_cases = [
        {"Tg": -20.0, "점도(cP)": 2000.0, "측정_값": 1000.0},
        {"Tg": -10.0, "점도(cP)": 4000.0, "측정_값": 2000.0},
        {"Tg": -30.0, "점도(cP)": 1500.0, "측정_값": 500.0},
    ]
    
    print("Running Full Loop Smoke A/B Test (5 iter + best-so-far)")
    
    # Control: Bounds OFF, Equal weights
    control_errors = []
    for t in test_cases:
        e, _ = run_full_loop(optimizer, t, use_property_bounds=False, target_weights={"Tg": 0.333, "점도(cP)": 0.333, "측정_값": 0.333})
        control_errors.append(e)
        
    # B3: Bounds ON, Data-driven weights
    data_driven_weights = {"측정_값": 0.45, "점도(cP)": 0.35, "Tg": 0.20}
    b3_errors = []
    for t in test_cases:
        e, _ = run_full_loop(optimizer, t, use_property_bounds=True, target_weights=data_driven_weights)
        b3_errors.append(e)
        
    print("\nResults:")
    for i, t in enumerate(test_cases):
        print(f"Case {i+1} - Control: {control_errors[i]:.4f} | B3: {b3_errors[i]:.4f}")
        
    avg_control = sum(control_errors)/len(control_errors)
    avg_b3 = sum(b3_errors)/len(b3_errors)
    improvement = (avg_control - avg_b3) / avg_control * 100
    
    print(f"\nAvg Control: {avg_control:.4f}")
    print(f"Avg B3 (V3): {avg_b3:.4f}")
    print(f"Improvement: {improvement:.2f}%")

if __name__ == "__main__":
    run_smoke_ab()
