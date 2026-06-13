# 预测模板 / Prediction Template

```json
{
  "id": "PRED-0001",
  "title": {"zh": "预测标题", "en": "Prediction Title"},
  "statement": {"zh": "预测判断内容", "en": "Prediction statement"},
  "basis": {"zh": "推出依据", "en": "Basis"},
  "test_condition": {"zh": "可验证条件", "en": "Test condition"},
  "falsification_condition": {"zh": "可证伪条件", "en": "Falsification condition"},
  "time_window": {"zh": "观察窗口或触发条件", "en": "Observation window or trigger condition"},
  "categories": [],
  "related_functions": [],
  "related_cases": [],
  "related_discoveries": [],
  "source_refs": [],
  "confidence": "low / medium / high",
  "status": "draft / active / verified / falsified / deprecated",
  "created_at": "YYYY-MM-DD",
  "updated_at": "YYYY-MM-DD",
  "page": "docs/zh/predictions/items/PRED-0001.md"
}
```

每条正式预测必须有可验证条件、可证伪条件、时间窗口、来源回指、相关对象、分类、状态与置信度。
