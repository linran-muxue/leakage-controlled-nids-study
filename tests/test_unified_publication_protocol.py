from scripts.run_unified_final import build_model_specs


def test_unified_protocol_includes_controlled_full_feature_rf_ablation():
    specs = build_model_specs(n_estimators=100, min_samples_leaf=2, seed=42, selected_count=60, total_features=78)
    names = [name for name, _, _ in specs]
    assert names == [
        "decision_tree_chi2",
        "svm_all",
        "extra_trees_chi2",
        "random_forest_all",
        "random_forest_chi2",
    ]
    modes = {name: mode for name, _, mode in specs}
    assert modes["random_forest_all"] == "all"
    assert modes["random_forest_chi2"] == "chi2"
