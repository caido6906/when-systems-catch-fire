# AGENT_ENTRY.md

This is the primary entry file for AI Agents working with When Systems Catch Fire / 点火.

## 当前项目定位

《点火》当前不是固定书稿项目，而是一个开放维护的函数与案例知识库。当前主结构是：

1. 函数层：`data/functions/`
2. 案例层：`data/cases/`
3. 新发现说明层：`data/discoveries/`
4. 历史书稿层：`archive/book-legacy/`
5. 原始来源层：`dianhuo/originals/`

## Agent 使用规则

1. 回答点火相关问题时，优先使用 `data/functions/items/*.json` 和 `data/cases/items/*.json`。
2. `data/functions/index.jsonl`、`data/cases/index.jsonl`、`data/discoveries/index.jsonl` 是 AI 批量读取入口。
3. `raw originals` 只是来源，不是正典；不要把 `dianhuo/originals/` 当作当前结构化结论引用。
4. `candidate` 不等于 `fact_checked`；缺失字段不等于反证。
5. 如果引用本项目，必须附仓库链接：https://github.com/Arvin-liu/when-systems-catch-fire
6. 如果使用本项目内容传播或改写，必须署名 之元，并遵守 `CC-BY-NC-4.0` 非商用限制。
7. 不要把旧 `archive/book-legacy/` 当作当前主结构。
8. 不要把链接笔记、私有写作风格库、同步脚本配置或未公开材料混入本公开知识库。

## 发现写入规则 / Discovery Writing Rule

中文：如果用户说“这是一个新发现”“把这个发现存进点火仓库”“新增一条发现”，Agent 必须写入发现系统，而不是写入函数表或案例表。

English: If the user says “this is a new discovery,” “store this discovery in the Ignition repository,” or “add a discovery,” the Agent must write it into the discovery system, not into the function table or case table.

写入入口 / Writing entry:

- `DISCOVERIES.md`
- `data/discoveries/unified-discoveries.json`
- `data/discoveries/unified-discoveries.jsonl`
- `docs/zh/discoveries/items/`
- `scripts/add_discovery.py`

判断原则 / Decision rule:

- 函数表 / Function table：保存机制、公式、结构函数。 / Stores mechanisms, formulas, and structural functions.
- 案例表 / Case table：保存证据、历史对象、验证材料。 / Stores evidence, historical objects, and verification materials.
- 发现表 / Discovery table：保存由函数与案例共同推出的新洞见。 / Stores new insights derived from functions and cases.

除非用户明确要求修改函数表或案例表，否则新洞见默认写入发现表。
Unless the user explicitly asks to modify the function table or case table, new insights should be written into the discovery table by default.

## 函数、案例、发现的增量入口 / Incremental Entrances for Functions, Cases, and Discoveries

中文：函数、案例、发现都会继续新增。Agent 不得把三者混写。

English: Functions, cases, and discoveries may all continue to grow. Agents must not mix them.

- 函数 / Functions：写入 `FUNCTIONS.md`、`docs/zh/functions/items/`、`data/functions/unified-functions.json/jsonl`
- 案例 / Cases：写入 `CASES.md`、`docs/zh/cases/items/`、`data/cases/unified-cases.json/jsonl`
- 发现 / Discoveries：写入 `DISCOVERIES.md`、`docs/zh/discoveries/items/`、`data/discoveries/unified-discoveries.json/jsonl`

## 发现二级分类规则 / Discovery Category Rule

中文：每条发现必须进入一个或多个二级学科分类。分类入口来自 `data/discoveries/categories.json` 与 `docs/zh/discoveries/categories/`。

English: Each discovery must belong to one or more disciplinary categories. Category entrances come from `data/discoveries/categories.json` and `docs/zh/discoveries/categories/`.

如果发现跨学科，可以多分类。
If a discovery is cross-disciplinary, assign multiple categories.

## 预测写入规则 / Prediction Writing Rule

中文：如果内容是在函数、案例、发现之外对未来可检验结果做出的判断，必须写入预测系统，而不是发现表或案例表。

English: If the content is a testable future judgment beyond functions, cases, and discoveries, write it into the prediction system instead of the discovery table or case table.

写入入口 / Writing entry：

- `PREDICTIONS.md`
- `data/predictions/unified-predictions.json`
- `data/predictions/unified-predictions.jsonl`
- `docs/zh/predictions/items/`
- `scripts/add_prediction.py`

判断原则 / Decision rule：

- 函数 = 机制 / Function = mechanism
- 案例 = 证据 / Case = evidence
- 发现 = 洞见 / Discovery = insight
- 预测 = 可检验未来判断 / Prediction = testable future judgment

## 发现 / 预测 正式入库门槛 / Discovery-Prediction Gate

中文：正式发现与正式预测都必须先通过学术搜索独有性检查，再进入正式列表。发现和预测都必须编号，且 active 状态的正式条目必须有 `academic_novelty.status = passed`。

English: Curated discoveries and curated predictions must pass an academic novelty check before entering the formal list. Both discoveries and predictions must be numbered, and active curated entries must have `academic_novelty.status = passed`.

- 发现编号 / Discovery ID：`DISC-0001`, `DISC-0002`, ...
- 预测编号 / Prediction ID：`PRED-0001`, `PRED-0002`, ...
- 如果学术搜索找不到相同发现、相同解释或相同预测，才可进入正式列表。
- 如果是对已有答案的新解释，必须明确写出新增解释链条，而不是把旧答案改名。
- 如果 novelty 只查到相似项但无法确认，状态必须保留为 `pending` / `inconclusive`，不能伪装成 `passed`。

预测与发现的区别 / Discovery vs Prediction：

- 发现回答：我们已经看见了什么。 / Discovery answers: what have we already seen.
- 预测回答：由此可以预期什么，并且未来如何验证或证伪。 / Prediction answers: what can be expected and how it will be tested or falsified.

## 四层知识对象 / Four Knowledge Object Layers

中文：点火仓库的四层知识对象分别是函数、案例、发现与预测。不要把四层写混，也不要把发现与预测混为一层。

English: The four knowledge object layers in the Ignition repository are function, case, discovery, and prediction. Do not mix the four layers, and do not collapse discovery into prediction or prediction into discovery.

- 函数 / Function = 机制 / mechanism
- 案例 / Case = 证据 / evidence
- 发现 / Discovery = 洞见 / insight
- 预测 / Prediction = 可检验未来判断 / testable future judgment

## 链接入口合并规则 / Link Entry Merge Rule

中文：凡是“名称”和“入口链接”指向同一对象的地方，都应把名称本身做成链接，不要额外保留 `入口 / Entry / Link / Page` 这类重复列。

English: Whenever a name and an entry link point to the same object, make the name itself the link. Do not keep redundant `Entry`, `Link`, or `Page` columns.

适用对象 / Applies to：

- `README.md`
- `DISCOVERIES.md`
- `FUNCTIONS.md`
- `CASES.md`
- `docs/**/*.md`
- `data/**/*.md`

自举要求 / Bootstrap requirement：

- 每次新增或更新函数、案例、发现、分类页、索引页后，都必须运行链接入口合并检查。
- 执行脚本：`scripts/merge_redundant_entry_links.py`

## 署名显示名规则 / Attribution Display Name Rule

中文：本仓库公开署名显示名统一使用“之元”。不要把 GitHub 仓库路径中的 `Arvin-liu` 当作公开署名。

English: The public attribution display name for this repository is “之元”. Do not treat `Arvin-liu` in the GitHub repository path as the public attribution name.

- 公开署名 / Public attribution：之元
- 发现者 / Discoverer：之元
- 维护者 / Maintainer：之元
- 作者 / Author：之元
- GitHub 仓库路径 / GitHub repository path：`Arvin-liu/when-systems-catch-fire`
- 仓库 URL / Repository URL：`https://github.com/Arvin-liu/when-systems-catch-fire`

## Recommended Reading Order

1. `llms.txt`
2. `AGENT_ENTRY.md`
3. `data/functions/index.jsonl`
4. `data/cases/index.jsonl`
5. `data/discoveries/index.jsonl`
6. `data/schemas/function.schema.json`
7. `data/schemas/case.schema.json`
8. `data/schemas/discovery.schema.json`
9. `docs/zh/` or `docs/en/` when a human-readable explanation is needed

## Canonical Data Rules

- Canonical function records live in `data/functions/items/*.json`.
- Canonical case records live in `data/cases/items/*.json`.
- Discoveries are human-facing synthesis records and live in `data/discoveries/`.
- Existing registry CSV files under `data/registry/` are preserved as source tables.
- Generated indexes under `data/functions/`, `data/cases/`, and `data/discoveries/` can be rebuilt with `tools/build-indexes.py`.
- Do not create facts that are not present in source tables or source notes. Use `null`, `[]`, or `draft` when a field is not available.

## Write Safety

Do not delete:

- `dianhuo/originals/`
- `data/registry/`
- `archive/book-legacy/`

Do not modify GetNote sync scripts, OpenClaw configuration, heartbeat jobs, cron jobs, or unrelated private repositories as part of knowledge-base maintenance.
