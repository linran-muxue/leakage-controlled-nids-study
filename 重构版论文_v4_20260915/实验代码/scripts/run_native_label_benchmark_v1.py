"""Native-label benchmark with the same-members equal-fusion control.

``run_seeds10_v5.py`` is tied to the five CIC-IDS2017 classes; the new corpora
have their own label sets, so this runner derives the classes from the data.  It
trains conditional weighting, the unweighted mean of *the same four experts*,
and two single-view equal-weight forests, and writes per-seed predictions for
each arm.
"""
from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from src.feature_selection import chi2_top_k
import src.rccf_forest as rccf
from src.rccf_forest import RCCFForest

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    frame = pd.read_csv(path, low_memory=False)
    return (frame.drop(columns=["target"]).apply(pd.to_numeric).to_numpy(float),
            frame["target"].to_numpy())


def metrics(y_true, y_pred, probability, classes, labels) -> dict:
    order = [list(classes).index(label) for label in labels]
    index = np.array([list(labels).index(value) for value in y_true])
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", labels=labels,
                                   zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "log_loss": float(log_loss(index, probability[:, order],
                                   labels=np.arange(len(labels)))),
    }


def write_predictions(path: Path, y_true, prediction, probability, classes):
    frame = pd.DataFrame({
        "row_id": np.arange(len(y_true)), "true_label": y_true,
        "predicted_label": prediction,
        **{f"prob_{label}": probability[:, i] for i, label in enumerate(classes)},
    })
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def split_with_minimum(y, test_size: float, seed: int, minimum: int = 2):
    """Stratified split that guarantees at least ``minimum`` rows per class on
    the calibration side; rare classes are moved across rather than dropped."""
    train_idx, cal_idx = train_test_split(np.arange(len(y)), test_size=test_size,
                                          stratify=y, random_state=seed)
    cal_counts = pd.Series(y[cal_idx]).value_counts()
    for label in pd.unique(y):
        held = int(cal_counts.get(label, 0))
        if held >= minimum:
            continue
        needed = minimum - held
        pool = train_idx[y[train_idx] == label]
        if len(pool) < needed:
            raise SystemExit(f"class {label!r} has fewer than {minimum} rows")
        moved = pool[:needed]
        train_idx = np.setdiff1d(train_idx, moved)
        cal_idx = np.concatenate([cal_idx, moved])
    return train_idx, cal_idx


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--seeds", nargs="+", type=int, default=[42, 2024, 3407])
    ap.add_argument("--n-estimators", type=int, default=100)
    ap.add_argument("--feature-k", type=int, default=60)
    ap.add_argument("--experts", nargs="+",
                    default=["full", "chi2", "mutual_info", "anova"],
                    help="expert views; the recent-corpus extension uses three "
                         "deterministic views and records the deviation")
    ap.add_argument("--resume", action="store_true",
                    help="skip a seed whose four prediction files already exist and "
                         "recompute its metrics from them (identically, because every "
                         "reported metric is a function of those files)")
    ap.add_argument("--n-jobs", type=int, default=-1,
                    help="threads per forest; every worker holds its own bootstrap "
                         "index and label-encoding buffer, so lowering this lowers "
                         "peak memory without changing any reported number")
    args = ap.parse_args()

    data = ROOT / args.processed_dir
    out = ROOT / args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    X_train, y_train = load(data / "train.csv")
    X_val, y_val = load(data / "validation.csv")
    X_test, y_test = load(data / "test.csv")
    labels = np.unique(y_train)
    rccf.RCCFForest.expert_names = tuple(args.experts)
    min_count = int(pd.Series(y_train).value_counts().min())
    counts = pd.Series(y_train).value_counts()
    # every class must survive a five-fold stratified split inside the training
    # partition, otherwise RCCFForest's out-of-fold buffer cannot be filled
    rare = [label for label, count in counts.items() if count < 5]
    if rare:
        keep = ~np.isin(y_train, rare)
        X_train, y_train = X_train[keep], y_train[keep]
        keep = ~np.isin(y_test, rare)
        X_test, y_test = X_test[keep], y_test[keep]
        labels = np.unique(y_train)
        min_count = int(pd.Series(y_train).value_counts().min())
        print(f"pruned classes with fewer than five training rows: {rare}", flush=True)
    print(f"train {X_train.shape} test {X_test.shape} classes {len(labels)}: "
          f"{list(labels)}", flush=True)
    rows = []
    previous = {}
    metrics_path = out / "metrics_by_seed.csv"
    if args.resume and metrics_path.exists():
        for row in pd.read_csv(metrics_path).to_dict("records"):
            previous[(row["model"], int(row["seed"]))] = row.get("train_seconds")
    for seed in args.seeds:
        saved = {name: out / f"predictions_{name}_seed{seed}.csv"
                 for name in ("rccf", "equal_fusion", "equal_rf_chi2", "equal_rf_all")}
        if args.resume and all(path.exists() for path in saved.values()):
            # The gate and the fusion arms are deterministic given (seed, data), and
            # every reported metric is a function of the saved rows, so a resumed
            # seed reproduces the same numbers without retraining.
            frames = {name: pd.read_csv(path) for name, path in saved.items()}
            for name, model in (("rccf", "rccf"), ("equal_fusion", "equal_fusion"),
                                ("equal_rf_chi2", "equal_rf_chi2"),
                                ("equal_rf_all", "equal_rf_all")):
                frame = frames[name]
                prob_columns = [c for c in frame.columns if c.startswith("prob_")]
                classes = np.array([c[len("prob_"):] for c in prob_columns])
                rows.append({"model": model, "seed": seed,
                             "train_seconds": previous.get((model, int(seed)), np.nan),
                             **metrics(frame["true_label"].to_numpy(),
                                       frame["predicted_label"].to_numpy(),
                                       frame[prob_columns].to_numpy(dtype=float),
                                       classes, labels)})
            rccf_f1 = next(r["macro_f1"] for r in rows
                           if r["model"] == "rccf" and r["seed"] == seed)
            equal_f1 = next(r["macro_f1"] for r in rows
                            if r["model"] == "equal_fusion" and r["seed"] == seed)
            print(f"seed {seed}: resumed from saved predictions "
                  f"(rccf {rccf_f1:.6f} vs equal {equal_f1:.6f})", flush=True)
            continue
        model = RCCFForest(n_estimators=args.n_estimators, feature_k=args.feature_k,
                           cv=5, random_state=seed, n_jobs=args.n_jobs)
        start = time.perf_counter()
        train_idx, cal_idx = split_with_minimum(y_train, 0.15, seed)
        model.fit(X_train[train_idx], y_train[train_idx],
                  X_train[cal_idx], y_train[cal_idx])
        train_seconds = time.perf_counter() - start
        probability = model.predict_proba(X_test)
        prediction = model.classes_[probability.argmax(axis=1)]
        write_predictions(out / f"predictions_rccf_seed{seed}.csv", y_test, prediction,
                          probability, model.classes_)
        rows.append({"model": "rccf", "seed": seed,
                     "train_seconds": train_seconds,
                     **metrics(y_test, prediction, probability, model.classes_, labels)})

        classes = model.classes_
        # Accumulate the unweighted mean rather than materialising one
        # 7.19 M x 18 float64 array per expert (four of them is 4 GB on the
        # uncapped Gotham corpus, and the host has to fit the run in ~10 GB).
        # Adding in the same order and dividing by the same count is
        # bit-identical to np.mean over the stacked list, so no reported number
        # moves.
        equal = None
        for expert in model.experts_:
            member = model._expert_proba(expert, X_test)
            equal = member if equal is None else equal + member
            del member
        equal = equal / len(model.experts_)
        equal_pred = classes[equal.argmax(axis=1)]
        write_predictions(out / f"predictions_equal_fusion_seed{seed}.csv", y_test,
                          equal_pred, equal, classes)
        rows.append({"model": "equal_fusion", "seed": seed, "train_seconds": np.nan,
                     **metrics(y_test, equal_pred, equal, classes, labels)})
        disagreements = int((equal_pred != prediction).sum())

        # The gate's four fitted expert forests are this run's memory peak on the
        # 14.25 M-row Gotham corpus.  They are no longer needed once the gate's
        # own predictions are on disk, and releasing them before the single-view
        # controls are fitted keeps the run inside the host's memory ceiling
        # (two attempts died in the fit below with a 109 MiB allocation error).
        # Dropping the reference cannot change a reported number: every metric
        # is a function of the prediction files that are already written.
        del equal, equal_pred, model
        gc.collect()

        scaler = MinMaxScaler().fit(X_train)
        X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)
        selection = chi2_top_k(X_train_s, y_train, args.feature_k)
        views = {
            "equal_rf_chi2": (selection.select(X_train_s), selection.select(X_test_s)),
            "equal_rf_all": (X_train_s, X_test_s),
        }
        for name in list(views):
            Xa, Xb = views.pop(name)
            forest = RandomForestClassifier(n_estimators=args.n_estimators,
                                            min_samples_leaf=2, n_jobs=args.n_jobs,
                                            class_weight="balanced_subsample",
                                            random_state=seed).fit(Xa, y_train)
            probability = forest.predict_proba(Xb)
            prediction = forest.classes_[probability.argmax(axis=1)]
            write_predictions(out / f"predictions_{name}_seed{seed}.csv", y_test,
                              prediction, probability, forest.classes_)
            rows.append({"model": name, "seed": seed, "train_seconds": np.nan,
                         **metrics(y_test, prediction, probability, forest.classes_,
                                   labels)})
            del forest, probability, prediction, Xa, Xb
            gc.collect()
        del X_train_s, X_test_s, scaler, selection
        gc.collect()
        rccf_f1 = next(r["macro_f1"] for r in rows
                       if r["model"] == "rccf" and r["seed"] == seed)
        equal_f1 = next(r["macro_f1"] for r in rows
                        if r["model"] == "equal_fusion" and r["seed"] == seed)
        print(f"seed {seed}: rccf {rccf_f1:.6f} vs same-members equal {equal_f1:.6f} "
              f"(diff {rccf_f1 - equal_f1:+.6f}, {disagreements} labels differ)",
              flush=True)

    frame = pd.DataFrame(rows)
    frame.to_csv(out / "metrics_by_seed.csv", index=False, encoding="utf-8-sig")
    aggregate = frame.groupby("model").agg(
        macro_f1_mean=("macro_f1", "mean"), macro_f1_std=("macro_f1", "std"),
        accuracy_mean=("accuracy", "mean"), balanced_accuracy_mean=("balanced_accuracy", "mean"),
        log_loss_mean=("log_loss", "mean"), train_seconds_mean=("train_seconds", "mean"),
        test_samples_mean=("macro_f1", "size")).reset_index()
    aggregate.to_csv(out / "metrics_aggregate.csv", index=False, encoding="utf-8-sig")
    summary = {
        "population": args.processed_dir, "seeds": [int(seed) for seed in args.seeds],
        "classes": [str(label) for label in labels],
        "test_rows": int(len(y_test)),
        "rccf_mean_macro_f1": float(aggregate.set_index("model").loc["rccf", "macro_f1_mean"]),
        "equal_fusion_mean_macro_f1": float(
            aggregate.set_index("model").loc["equal_fusion", "macro_f1_mean"]),
        "same_members_difference": float(
            aggregate.set_index("model").loc["rccf", "macro_f1_mean"]
            - aggregate.set_index("model").loc["equal_fusion", "macro_f1_mean"]),
    }
    (out / "benchmark_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
