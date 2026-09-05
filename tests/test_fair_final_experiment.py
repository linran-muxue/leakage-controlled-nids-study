from src.fair_final_experiment import build_model_specs


def test_weighted_report_is_a_documented_output_name():
    assert "weighted_rf_chi2" in "classification_report_weighted_rf_chi2_seed42.csv"


def test_build_model_specs_contains_fair_feature_and_model_combinations():
    specs = build_model_specs(n_estimators=10, seed=42, selected_count=60)
    names = [item[0] for item in specs]
    assert names == [
        "decision_tree_all",
        "decision_tree_chi2",
        "svm_all",
        "svm_chi2",
        "random_forest_all",
        "random_forest_chi2",
        "extra_trees_chi2",
    ]
    assert specs[0][3]["feature_mode"] == "all"
    assert specs[1][3]["feature_count"] == 60
