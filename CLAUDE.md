# CLAUDE.md - 论文工作流多智能体配置

> Paper Agent Pipeline: 基于 Claude Code 的 9 阶段学术论文自动写作系统

---

## 外部依赖安装

本工作流依赖以下外部 Skill，使用前必须先安装：

### 1. nature-skills（MIT 许可证）

```bash
git clone https://github.com/Yuan1z0825/nature-skills ~/.claude/skills/nature-skills
```

安装后将以下命令桥接文件复制到 `~/.claude/commands/`：
- `nature-citation.md` — 引用管理
- `nature-data.md` — 数据可用性声明
- `nature-figure.md` — 科研图表生成
- `nature-polishing.md` — 学术润色
- `nature-response.md` — 审稿回复
- `nature-paper2ppt.md` — 论文转PPT

### 2. word-document-processor（Anthropic 专有）

通过 Claude Code 的 Skill 市场安装，或手动安装到 `~/.claude/skills/word-document-processor/`。

> ⚠️ 此 Skill 为 Anthropic 专有许可证，不可重新分发。请从官方渠道获取。

### 3. literature-search（已内置）

本仓库已包含此 Skill（`skills/literature-search/`），安装时会自动复制到 `~/.claude/skills/`。

---

## 快速使用

```
帮我写一篇论文，主题是：[你的主题]
```

## 完整调用

```
帮我写一篇论文，主题是：大语言模型在教育中的应用
- 类型：实证研究
- 语言：英文
- 目标期刊：Computers & Education
- 篇幅：标准（8-12页）
```

## 智能体角色（10个）

| 阶段 | 角色 | 职责 | 配置文件 | 使用的 Skill |
|------|------|------|----------|--------------|
| 1 | 需求分析师 | 理解需求，确认论文类型、语言、审稿模式等 | `paper_requirement_analyst.md` | — |
| 2 | 文献搜索智能体 | 搜索文献、追踪引用、评估影响力 | `paper_literature_searcher.md` | `literature-search` |
| 3 | 文献综述智能体 | 整理文献、撰写综述、生成 BibTeX | `paper_literature_reviewer.md` | `nature-citation` |
| 4 | 架构设计师 | 设计大纲、章节结构、论证逻辑 | `paper_framework_designer.md` | — |
| 5 | 内容写作智能体 | 逐章节撰写正文 | `paper_content_writer.md` | `word-document-processor` |
| 5a | 图表智能体 | 生成科研图表、数据可视化 | `paper_figure_agent.md` | `nature-figure` + `nature-data` |
| 6 | 学术润色智能体 | 全文语言润色、格式规范检查 | `paper_polishing.md` | `nature-polishing` |
| 7 | 审稿回复智能体 | 模拟审稿或回复真实审稿意见 | `paper_review_response.md` | `nature-response` |
| 8 | PPT生成智能体 | 论文核心内容转为演示PPT | `paper_ppt_generator.md` | `nature-paper2ppt` |
| 9 | 终审交付智能体 | 最终检查、PDF转换、打包交付 | `paper_delivery.md` | `word-document-processor` |

## 工作流程

```
阶段1: 需求分析 (5分钟)
  → 需求分析师 → requirements.md
  → 询问：论文类型、语言、目标期刊、是否有真实审稿意见、是否需要PPT

阶段2: 文献搜索 (20分钟)
  → 文献搜索智能体 → research/references_raw.json + research/top_papers.md

阶段3: 文献综述 (20分钟)
  → 文献综述智能体 → research/literature_review.md + research/references.bib

阶段4: 结构设计 (15分钟)
  → 架构设计师 → outline.md + chapter_plan.md

阶段5: 逐章写作 (每章10-15分钟):
  对每一章:
    内容写作智能体(新) → chapters/chapter_{N}.docx
    图表智能体(新)     → figures/chapter_{N}/
    └─ 审核不通过 → 重写（注入修改意见，最多2轮）

阶段6: 学术润色 (20分钟)
  → 润色智能体 → polished_paper.docx + polishing_report.md

阶段7: 审稿回复 (15分钟)
  有真实审稿意见 → 回复真实意见 → review_response/response_to_reviewers.md
  无真实审稿意见 → 模拟审稿+回复 → review_response/simulated_review.md

阶段8: PPT生成 (20分钟，可选)
  → PPT生成智能体 → presentation.pptx

阶段9: 终审交付 (10分钟)
  → 终审交付智能体 → Paper_Delivery_[日期]_[主题]/
```

## 需求确认时询问的问题

在阶段1，需求分析师必须询问以下问题：

| 问题 | 选项 | 默认值 |
|------|------|--------|
| 论文类型 | 实证研究 / 综述 / 理论分析 | 实证研究 |
| 论文语言 | 中文 / 英文 / 双语 | 英文 |
| 目标期刊 | 用户指定或"不指定" | 不指定 |
| 是否有真实审稿意见 | 有 / 无 | 无 |
| 是否需要生成演示PPT | 是 / 否 | 否 |
| 预期篇幅 | 短文(4-6页) / 标准(8-12页) / 长文(15-20页) | 标准 |

## 调用模板

### 调用需求分析师（阶段1）
```
请调用 Agent 工具生成一个新的 paper_requirement_analyst 子智能体，执行以下任务：

用户需求：[用户输入]
输出文件：requirements.md

只返回生成的文件路径，不要返回其他信息。
```

### 调用文献搜索智能体（阶段2）
```
请调用 Agent 工具生成一个新的 paper_literature_searcher 子智能体，执行以下任务：

需求文件：requirements.md
输出目录：research/

只返回生成的目录路径，不要返回其他信息。
```

### 调用文献综述智能体（阶段3）
```
请调用 Agent 工具生成一个新的 paper_literature_reviewer 子智能体，执行以下任务：

需求文件：requirements.md
文献数据：research/references_raw.json
高影响力论文：research/top_papers.md
输出目录：research/

只返回生成的文件路径，不要返回其他信息。
```

### 调用架构设计师（阶段4）
```
请调用 Agent 工具生成一个新的 paper_framework_designer 子智能体，执行以下任务：

需求文件：requirements.md
文献综述：research/literature_review.md
引用文件：research/references.bib
输出文件：outline.md

只返回生成的文件路径，不要返回其他信息。
```

### 调用内容写作智能体（阶段5 - 每章调用）
```
请调用 Agent 工具生成一个新的 paper_content_writer 子智能体，执行以下任务：

需求文件：requirements.md
大纲文件：outline.md
写作计划：chapter_plan.md
文献综述：research/literature_review.md
引用文件：research/references.bib
当前章节：第N章
输出文件：chapters/chapter_{N}.docx

只返回生成的文件路径，不要返回其他信息。
```

### 调用图表智能体（阶段5a - 每章调用）
```
请调用 Agent 工具生成一个新的 paper_figure_agent 子智能体，执行以下任务：

章节文档：chapters/chapter_{N}.docx
文献数据：research/references_raw.json
需求文件：requirements.md
输出目录：figures/chapter_{N}/

只返回生成的目录路径，不要返回其他信息。
```

### 调用学术润色智能体（阶段6）
```
请调用 Agent 工具生成一个新的 paper_polishing 子智能体，执行以下任务：

需求文件：requirements.md
章节目录：chapters/
引用文件：research/references.bib
输出文件：polished_paper.docx

只返回生成的文件路径，不要返回其他信息。
```

### 调用审稿回复智能体（阶段7）
```
请调用 Agent 工具生成一个新的 paper_review_response 子智能体，执行以下任务：

需求文件：requirements.md
论文文件：polished_paper.docx
审稿意见目录：review_comments/（如有）
输出目录：review_response/

只返回生成的目录路径，不要返回其他信息。
```

### 调用PPT生成智能体（阶段8 - 可选）
```
请调用 Agent 工具生成一个新的 paper_ppt_generator 子智能体，执行以下任务：

论文文件：polished_paper.docx
大纲文件：outline.md
需求文件：requirements.md
图表目录：figures/
输出文件：presentation.pptx

只返回生成的文件路径，不要返回其他信息。
```

### 调用终审交付智能体（阶段9）
```
请调用 Agent 工具生成一个新的 paper_delivery 子智能体，执行以下任务：

论文文件：polished_paper.docx
审稿回复：review_response/
图表目录：figures/
PPT文件：presentation.pptx（如有）
需求文件：requirements.md
输出目录：Paper_Delivery_[日期]_[主题]/

只返回生成的目录路径，不要返回其他信息。
```

## 论文类型模板

| 类型 | 章节结构 |
|------|----------|
| **实证研究** | 引言 → 文献综述 → 研究方法 → 结果 → 讨论 → 结论 |
| **综述** | 引言 → 背景 → 主题分析（多章） → 讨论与展望 → 结论 |
| **理论分析** | 引言 → 理论框架 → 分析与论证 → 案例研究 → 讨论 → 结论 |

## 篇幅模板

| 篇幅 | 页数 | 预计制作时间 |
|------|------|--------------|
| 短文 | 4-6页 | 2-3小时 |
| 标准 | 8-12页 | 4-6小时 |
| 长文 | 15-20页 | 8-10小时 |

---

## 关键约束

### 通用约束
1. **全新实例**：每次执行新任务时，必须调用全新的智能体
2. **无上下文污染**：智能体只返回文件路径，不返回其他信息
3. **最多2轮**：单页审核失败最多重试2次
4. **文件路径通信**：所有智能体之间通过文件路径通信

### 论文工作流额外约束
16. **语言一致**：全文语言必须与 requirements.md 中指定的语言一致
17. **引用规范**：每个论点必须有文献支撑，正文使用上标序号式引用 [1]、[2,3]、[4-6]，文末附按序号排列的完整参考文献列表
18. **目录要求**：论文必须包含目录页，位于摘要之后、正文之前，使用 Word TOC 域代码自动生成
19. **逐章审核**：每章写作完成后必须通过质量检查才能进入下一章
20. **文献追踪**：文献搜索必须包含引用关系追踪，不能只做关键词搜索
21. **⚠️ 审稿模式确定**：阶段1必须明确审稿模式（真实/模拟），不可跳过
22. **⚠️ PPT可选**：阶段8为可选阶段，由用户在阶段1决定
23. **⚠️ 输出双格式**：最终必须同时输出 .docx 和 .pdf 两种格式
24. **⚠️ 图表规范**：所有图表必须 ≥300 DPI，PNG 格式，包含完整标注
25. **⚠️ 图表编号**：图表编号格式为 [图X-Y] / [表X-Y]（X=章节号，Y=序号），图注在图下方居中，表注在表上方居中
26. **⚠️ 图表插入**：图表必须插入正文（非仅生成在 figures/ 目录），正文中必须引用图表编号
27. **⚠️ 页码规范**：封面无页码，摘要/目录使用罗马数字页码（i, ii, iii...），正文使用阿拉伯数字页码（1, 2, 3...）从1开始
28. **⚠️ BibTeX完整**：references.bib 必须包含所有被引用的文献，格式正确可解析
29. **⚠️ 引用上标拆分**：引用标记 [N] 必须作为独立 run 并设置 superscript=True，禁止混在正文同一个 run 中（否则上标不生效）
30. **⚠️ 参考文献编号不上标**：参考文献列表中每条的 [N] 编号必须是正常文本，禁止设置 superscript
31. **⚠️ 图片嵌入验证**：插入图片后必须验证 doc.part.rels 中存在 image part，且 inline_shapes 数量 > 0，否则图片无法显示
32. **⚠️ 标题样式与分页**：章节标题必须使用 Heading 1 样式（非 Normal），每个章节标题前必须有分页符
33. **⚠️ Word域代码更新**：页码和目录是域代码，python-docx 无法渲染，必须用 win32com 调用 Word 更新域代码后才能正确显示；PDF 也必须由 Word 导出
34. **⚠️ 分节符必须用Word COM**：python-docx 的分节符在 Word 中会丢失（3节变1节），必须用 `InsertBreak(wdSectionBreakNextPage)` 在"目录"和"第一章"前插入；页码用 `doc.Fields.Add(rng, wdFieldPage)` 插入页脚；中文路径需通过临时英文路径中转

---

## 文件结构

```
~/.claude/
├── CLAUDE.md                              # 本文件（主配置）
├── agents/
│   ├── paper_requirement_analyst.md       # 阶段1: 需求分析师
│   ├── paper_literature_searcher.md       # 阶段2: 文献搜索
│   ├── paper_literature_reviewer.md       # 阶段3: 文献综述
│   ├── paper_framework_designer.md        # 阶段4: 结构设计
│   ├── paper_content_writer.md            # 阶段5: 内容写作
│   ├── paper_figure_agent.md              # 阶段5a: 图表生成
│   ├── paper_polishing.md                 # 阶段6: 学术润色
│   ├── paper_review_response.md           # 阶段7: 审稿回复
│   ├── paper_ppt_generator.md             # 阶段8: PPT生成
│   └── paper_delivery.md                  # 阶段9: 终审交付
├── skills/
│   └── literature-search/                 # 文献搜索 skill
│       ├── SKILL.md
│       └── scripts/s2_search.py
└── commands/
    ├── nature-citation.md                 # 引用管理
    ├── nature-data.md                     # 数据可用性
    ├── nature-figure.md                   # 图表生成
    ├── nature-polishing.md                # 学术润色
    ├── nature-response.md                 # 审稿回复
    └── nature-paper2ppt.md                # 论文转PPT
```
