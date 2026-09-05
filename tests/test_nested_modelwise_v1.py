from src.nested_evaluation import filter_candidate_specs


def test_filter_candidate_specs_keeps_one_model_family_and_all_modes():
    specs = filter_candidate_specs("random_forest", seed=42, n_classes=2, k_values=[20, 40])
    assert specs
    assert {row["model"] for row in specs} == {"random_forest"}
    assert {row["mode"] for row in specs} == {"all", "chi2"}
