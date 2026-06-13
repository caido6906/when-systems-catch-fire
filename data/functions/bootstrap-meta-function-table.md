# 第 0 节正反双通道自举元函数表 / Section 0 Forward-Reverse Bootstrap Meta-Function Table

本表展开 MF-0000 的正反双通道内部结构。MF-0000 仍是第 0 节总入口，不计入普通函数 470 条。
This table expands the internal forward-reverse structure of MF-0000. MF-0000 remains the Section 0 root entry and is not counted among the 470 ordinary functions.

| 编号 / ID | 名称 / Title | 数学表达 / Expression | 作用 / Role | 状态 / Status |
| --- | --- | --- | --- | --- |
| [MF-0000](../../docs/zh/functions/meta/MF-0000.md) | 自举元函数 / Bootstrap Meta-Function | M_boot = ε_sense × P_track × d(ΔK)/dt | 第 0 节总入口 / Section 0 root entry | active |
| [MF-0001](../../docs/zh/functions/meta/items/MF-0001.md) | 正向自举通道 / Forward Bootstrap Channel | M_boot⁺(x) = M_boot(x⁺) | 论证 x 成立 / Argues that x holds | active |
| [MF-0002](../../docs/zh/functions/meta/items/MF-0002.md) | 反向自举通道 / Reverse Bootstrap Channel | M_boot⁻(x) = M_boot(x⁻) | 论证 x 不成立 / Argues that x does not hold | active |
| [MF-0003](../../docs/zh/functions/meta/items/MF-0003.md) | 正反互斥判定器 / Forward-Reverse Exclusivity Judge | ¬(J⁺(x)=1 ∧ J⁻(x)=1) | 检查正反是否同时通过 / Rejects simultaneous pass | active |
| [MF-0004](../../docs/zh/functions/meta/items/MF-0004.md) | 自举嵌套判定器 / Nested Bootstrap Judge | M_boot^(k+1) = M_boot(M_boot^(k)) | 检查自举元函数自身 / Tests bootstrap self-nesting | active |
| [MF-0005](../../docs/zh/functions/meta/items/MF-0005.md) | 自举收敛判定器 / Bootstrap Convergence Judge | Converged(B_n) ⇔ \|\|ΔB_n\|\| = 0 ∧ \|\|ΔB_(n+1)\|\| = 0 ∧ LinkGraphStable(B_n) ∧ DynamicCountsStable(B_n) ∧ NoDuplicateLabels(B_n) ∧ AcademicNoveltyGate(B_n) | 检查整个系统是否收敛 / Tests convergence of the full system | active |

## 规则 / Rule

- MF-0000 是总入口，不计入普通函数。
- MF-0001 至 MF-0005 是内部子项，不计入 ordinary functions。
- 正向通过且反向不通过，命题成立。
- 反向通过且正向不通过，命题不成立。
- 正反同时通过，判定为 contradiction / bootstrap_failed。
- 正反都不通过，判定为 underdetermined / pending。
