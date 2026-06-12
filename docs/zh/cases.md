# 案例层

案例层是《点火》知识库的第二主入口。每条案例都有一个 canonical JSON 文件，保存案例 ID、中文标题、摘要、案例类型、相关函数、来源笔记和证据等级。

主要入口：

- `data/cases/index.jsonl`
- `data/cases/index.csv`
- `data/cases/index.md`
- `data/cases/items/*.json`

案例 JSON 由 `data/registry/统一案例总表.csv` 生成。已有稳定 ID 会保留；临时 ID 不自动重编号。
