# 函数层

函数层是《点火》知识库的第一主入口。每条函数都有一个 canonical JSON 文件，保存原始 ID、标准化 ID、中文标题、来源笔记、状态、关系链接和缺失字段占位。

主要入口：

- `data/functions/index.jsonl`
- `data/functions/index.csv`
- `data/functions/index.md`
- `data/functions/items/*.json`

函数 JSON 由 `data/registry/统一函数总表.csv` 生成。没有来源字段的数据保持 `null` 或 `[]`，不补写未验证解释。
