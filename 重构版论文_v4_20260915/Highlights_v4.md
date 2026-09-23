# Highlights

- Weighting matches equal voting on capped data but loses 0.005533 on the full corpus.
- Across ten seeds on the primary population the sign splits five to five.
- 99.91% of test rows are provably immune to the gate; no row changes label.
- Feature-value corruption costs far more accuracy than corrupted labels.
- Protocol choices move Macro-F1 by 0.0725, against 0.0005 for the aggregation rule.

---

# 中文要点（供中文稿使用）

- 条件加权在截断总体上与等权持平，全语料上反而落后 0.005533。
- 主总体上十个种子的方向五正五负，没有优势。
- 99.91% 的测试行可被证明不受门控影响，实际改判 0 条。
- 特征值污染造成的精度损失远大于标签污染。
- 类别先验带来的差异为 0.0725，而聚合策略仅 0.0005。
