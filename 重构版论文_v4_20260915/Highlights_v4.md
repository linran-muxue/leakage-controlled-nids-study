# Highlights

- Conditional ensemble weighting is equivalent to equal voting within 0.005 Macro-F1.
- Across ten seeds the per-seed sign splits five to five, with no advantage.
- 99.91% of test rows are provably immune to the gate; no row changes label.
- Feature-value corruption costs far more accuracy than corrupted labels.
- Protocol choices move Macro-F1 by 0.0725, against 0.0005 for the aggregation rule.

---

# 中文要点（供中文稿使用）

- 条件集成加权与等权投票在 0.005 Macro-F1 边界内等价。
- 十个种子上逐种子方向五正五负，无优势。
- 99.91% 的测试行可被证明不受门控影响，实际改判 0 条。
- 特征值污染造成的精度损失远大于标签污染。
- 类别先验带来的差异为 0.0725，而聚合策略仅 0.0005。
