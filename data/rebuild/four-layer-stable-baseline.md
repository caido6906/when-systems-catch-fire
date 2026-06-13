# 四层稳定基线封版报告 / Four-Layer Stable Baseline Report

- 生成时间 / Generated at: 2026-06-13T09:29:17+00:00
- 基线名称 / Baseline name: `four-layer-knowledge-base-baseline`
- 基线 commit / Baseline commit: `5cee45d`
- 仓库 / Repository: `Arvin-liu/when-systems-catch-fire`
- 仓库 URL / Repository URL: `https://github.com/Arvin-liu/when-systems-catch-fire`

## 四个主入口

- `DISCOVERIES.md`
- `PREDICTIONS.md`
- `FUNCTIONS.md`
- `CASES.md`

## 当前稳定态

- 正式预测数量：8
- 公开署名显示名：之元
- 当前四层结构已完成稳定封版

## 链接图文件

- `data/graph/ignition-link-graph.json`
- `data/graph/ignition-link-graph.jsonl`
- `data/graph/dangling-links.md`

## 最终验收报告

- `data/rebuild/four-layer-final-audit-report.md`
- `data/rebuild/four-layer-final-audit-report.json`

## 已通过检查

- `normalize_attribution_display_name.py --check`
- `render_discovery_index.py --check`
- `render_prediction_index.py --check`
- `build_predictions_from_bootstrap.py --check`
- `merge_redundant_entry_links.py --check`

## 后续维护规则

后续所有新增、改写、废弃、删除都必须进入四层自举循环维护，且不得把预测层混回发现层。

## 稳定标签

- `four-layer-baseline-2026-06-13`：已创建，指向 `5cee45d`
