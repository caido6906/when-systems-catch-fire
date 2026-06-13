# 自举分类报告 / Bootstrap Category Report

中文：本报告记录函数—案例—发现自举循环对学科入口的扫描结果。分类不是空壳，而是基于当前函数与案例表的可见覆盖生成。

English: This report records the bootstrap scan of the function-case-discovery cycle over disciplinary entrances. The categories are not empty shells; they are generated from the visible coverage in the current function and case tables.

## 汇总 / Summary

- 分类总数 / Total categories：18
- 函数总数 / Total functions：470
- 案例总数 / Total cases：578

| 分类 / Category | 相关函数 / Related functions | 相关案例 / Related cases | 待整理线索 / Leads |
| --- | --- | --- | --- |
| 物理学 / Physics | 133 | 71 | 5 |
| 心理学 / Psychology | 61 | 72 | 5 |
| 化学 / Chemistry | 21 | 105 | 5 |
| 生物学 / Biology | 12 | 20 | 5 |
| 神经科学与意识 / Neuroscience and Consciousness | 46 | 67 | 5 |
| 医学与健康 / Medicine and Health | 15 | 13 | 5 |
| 哲学 / Philosophy | 33 | 9 | 5 |
| 历史与文明 / History and Civilization | 67 | 501 | 5 |
| 文学与叙事 / Literature and Narrative | 2 | 0 | 2 |
| 艺术与摄影 / Art and Photography | 0 | 1 | 1 |
| 经济与财富 / Economics and Wealth | 60 | 70 | 5 |
| 法律与制度 / Law and Institutions | 6 | 11 | 5 |
| 社会学与政治 / Sociology and Politics | 32 | 42 | 5 |
| AI 与系统 / AI and Systems | 135 | 111 | 5 |
| 技术与工程 / Technology and Engineering | 28 | 31 | 5 |
| 教育与学习 / Education and Learning | 14 | 18 | 5 |
| 生态与环境 / Ecology and Environment | 31 | 27 | 5 |

## 说明 / Notes

1. 第 1 轮：按关键词和标题粗分学科。
2. 第 2 轮：通过 related_functions / related_cases 传播分类。
3. 第 3 轮：合并低置信分类，生成每个学科的问题域地图。
