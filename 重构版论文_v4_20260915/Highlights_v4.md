# Highlights

- Conditional ensemble weighting matches equal voting within a 0.01 Macro-F1 margin.
- 99.91% of test rows are provably immune to the gate, and no row changes label.
- All 108 gate hyper-parameter settings yield only six distinct validation scores.
- Gain is governed by expert diversity: low-diversity expert sets gain exactly zero.
- Protocol choices move Macro-F1 by 0.072, against 0.001 for the aggregation rule.

---

# 中文要点（供中文稿使用）

- 条件集成加权与等权投票的差异落在 0.01 Macro-F1 等价边界内。
- 99.91% 的测试行可被证明不受门控影响，实际改判 0 条。
- 门控全部 108 种超参数配置只产生 6 个不同的验证集取值。
- 增益受专家多样性支配：低分歧专家集合的增益恰为零。
- 类别先验带来的差异为 0.072，而聚合策略仅 0.001。
