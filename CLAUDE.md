# CLAUDE.md - 论文工作流多智能体配置

> Paper Agent Pipeline: 基于 Claude Code 的学术论文自动写作系统，支持专科/本科/硕士多层次论文

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

## 智能体角色（11个）

| 阶段 | 角色 | 职责 | 配置文件 | 使用的 Skill |
|------|------|------|----------|--------------|
| 1 | 需求分析师 | 理解需求，确认论文类型、语言、审稿模式等 | `paper_requirement_analyst.md` | — |
| 1.5 | 代码阅读智能体 | 读取系统源码，分析架构/模块/数据库/API（仅基于系统的论文） | `paper_code_reader.md` | — |
| 2 | 文献搜索智能体 | 搜索文献、追踪引用、评估影响力 | `paper_literature_searcher.md` | `literature-search` |
| 3 | 文献综述智能体 | 整理文献、撰写综述、生成 BibTeX | `paper_literature_reviewer.md` | `nature-citation` |
| 4 | 架构设计师 | 设计大纲、章节结构、论证逻辑 | `paper_framework_designer.md` | — |
| 5 | 内容写作智能体 | 逐章节撰写正文+生成并嵌入图表 | `paper_content_writer.md` | `word-document-processor` + `nature-figure` |
| 6 | 学术润色智能体 | 全文语言润色、格式规范检查 | `paper_polishing.md` | `nature-polishing` |
| 7 | 审稿回复智能体 | 模拟审稿或回复真实审稿意见 | `paper_review_response.md` | `nature-response` |
| 8 | PPT生成智能体 | 论文核心内容转为演示PPT | `paper_ppt_generator.md` | `nature-paper2ppt` |
| 9 | 终审交付智能体 | 最终检查、PDF转换、打包交付 | `paper_delivery.md` | `word-document-processor` |

## 工作流程

```
阶段1: 需求分析 (5分钟)
  → 需求分析师 → requirements.md
  → 询问：学历层次、论文类型、语言、是否基于特定系统、系统代码路径

阶段1.5: 代码阅读 (10-15分钟，仅"基于特定系统"的论文)
  → 代码阅读智能体 → research/code_analysis.md
  → 读取系统源码，分析：项目结构、技术栈、功能模块、数据库、API接口
  → 输出代码分析报告，供后续章节写作使用

阶段2: 文献搜索 (20分钟)
  → 文献搜索智能体 → research/references_raw.json + research/top_papers.md

阶段3: 文献综述 (20分钟)
  → 文献综述智能体 → research/literature_review.md + research/references.bib

阶段4: 结构设计 (15分钟)
  → 架构设计师 → outline.md + chapter_plan.md
  ⚠️ 基于系统的论文，大纲必须按代码分析报告中的模块划分组织

阶段5: 逐章写作 (每章10-15分钟):
  对每一章:
    内容写作智能体(新) → chapters/chapter_{N}.docx（含内联图表）
    └─ 审核不通过 → 重写（注入修改意见，最多2轮）
  ⚠️ 图表必须在写作阶段内联插入chapter_N.docx，禁止事后批量插入

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
| 学历层次 | 专科 / 本科 / 硕士 / 博士 | 本科 |
| 论文类型 | 实证研究 / 综述 / 理论分析 / 毕业设计 | 实证研究 |
| 论文语言 | 中文 / 英文 / 双语 | 英文 |
| 目标期刊 | 用户指定或"不指定" | 不指定 |
| 是否有真实审稿意见 | 有 / 无 | 无 |
| 是否需要生成演示PPT | 是 / 否 | 否 |
| 预期篇幅 | 短文(4-6页) / 标准(8-12页) / 长文(15-20页) / 专科(5000-8000字) / 本科(1-2万字) / 硕士(3-5万字) | 标准 |
| 是否基于特定系统 | 是（需提供系统名称和代码路径） / 否 | 否 |

## 调用模板

### 调用需求分析师（阶段1）
```
请调用 Agent 工具生成一个新的 paper_requirement_analyst 子智能体，执行以下任务：

用户需求：[用户输入]
输出文件：requirements.md

只返回生成的文件路径，不要返回其他信息。
```

### 调用代码阅读智能体（阶段1.5 - 仅基于特定系统的论文）
```
请调用 Agent 工具生成一个新的 paper_code_reader 子智能体，执行以下任务：

## 你必须完成的事情

1. 读取 requirements.md 了解论文需求
2. 读取用户提供的系统源码目录
3. 分析系统的完整架构和实现
4. 输出代码分析报告

## ⚠️ 触发条件

仅当 requirements.md 中"是否基于特定系统"为"是"时才执行此阶段。否则跳过。

## 分析内容

### 1. 项目结构分析
- 读取项目根目录结构
- 识别技术栈（前端/后端/数据库/框架）
- 识别构建工具（Maven/Gradle/npm等）

### 2. 功能模块分析
- 识别系统的主要功能模块
- 分析模块间的依赖关系
- 统计每个模块的代码量

### 3. 数据库分析
- 读取数据库配置文件
- 读取实体类/Model类，提取表结构
- 分析表间关系（一对多、多对多等）

### 4. API接口分析
- 读取Controller层代码
- 提取所有REST API接口（路径、方法、参数）
- 分析接口的业务逻辑

### 5. 关键代码提取
- 每个模块提取1-2个核心代码片段
- 标注代码的业务含义

## 输出文件

research/code_analysis.md（代码分析报告）

报告格式：
```
## 系统概述
- 系统名称：
- 技术栈：
- 项目结构：

## 功能模块
- 模块1：[名称] - [功能] - [关键文件路径]
- 模块2：...

## 数据库设计
- 表1：[表名] - [字段列表]
- 表2：...

## API接口
- GET /api/xxx - [功能]
- POST /api/xxx - [功能]

## 关键代码片段
### 模块1：[核心代码]
### 模块2：[核心代码]
```

系统源码路径：[用户提供的路径]

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
代码分析：research/code_analysis.md（如有，基于系统的论文必须读取）
输出文件：outline.md

⚠️ 如果是基于特定系统的论文，大纲的章节结构必须按照代码分析报告中的模块划分来组织。

只返回生成的文件路径，不要返回其他信息。
```

### 调用内容写作智能体（阶段5 - 每章调用）
```
请调用 Agent 工具生成一个新的 paper_content_writer 子智能体，执行以下任务：

## 你必须完成的事情

1. 先用 Read 工具读取 ~/.claude/agents/paper_content_writer.md 了解职责
2. 读取 outline.md、chapter_plan.md、research/literature_review.md、research/references.bib
   ⚠️ 如果存在 research/code_analysis.md，必须读取（基于系统的论文，代码分析是核心数据来源）
3. 撰写本章正文
4. ⚠️ 生成本章所有图表（使用 nature-figure skill）并内联嵌入到 chapter_{N}.docx 中
5. 使用 word-document-processor skill 输出 Word 文档

## ⚠️ 强制要求（违反任何一条视为不合格）

- **图表必须内联插入**：使用 run.add_picture() 将图片插入到首次引用该图的段落之后
- **表格必须内联插入**：使用 doc.add_table() 将表格插入到首次引用该表的段落之后
- **禁止事后补插**：图表必须在本次智能体调用中完成，不能留给后续阶段
- **每章至少1-2个图表**：架构图、流程图、对比表、数据表等
- **图表编号格式**：[图X-Y] / [表X-Y]，X为章节号，Y为序号
- **图表规范**：≥300 DPI，PNG 格式，图注在下方居中，表注在上方居中

## 输入文件

- requirements.md
- outline.md
- chapter_plan.md
- research/literature_review.md
- research/references.bib
- research/code_analysis.md（如有）
- 当前章节：第N章

## 输出文件

chapters/chapter_{N}.docx（必须包含内联图表）

只返回生成的文件路径，不要返回其他信息。
```

### 调用学术润色智能体（阶段6）
```
请调用 Agent 工具生成一个新的 paper_polishing 子智能体，执行以下任务：

## 你必须完成的事情

1. 读取 ~/.claude/agents/paper_polishing.md 了解职责
2. 读取 requirements.md、chapters/、research/references.bib
3. 合并所有章节，生成完整论文
4. 使用 word-document-processor skill

## ⚠️ 文档组装顺序（必须严格按此顺序）

1. 封面页
2. 中文摘要
3. 英文摘要
4. **目录页** ← 必须在摘要之后、正文之前（禁止放到最后）
5. 第1章 引言
6. 第2章 ~ 第N章
7. 参考文献
8. 致谢

## ⚠️ 图表处理

- 各章节的图表已内联嵌入在 chapter_N.docx 中，合并时必须保留
- 不要重新插入图表，只需合并章节文件
- 合并后验证 inline_shapes 数量是否正确

## 输出文件

- polished_paper.docx
- polishing_report.md

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

## ⚠️ 交付前必须验证的格式清单

- [ ] 目录在摘要之后、正文之前（不是在文档最后）
- [ ] 图表已内联嵌入（inline_shapes > 0）
- [ ] 图表位置正确（紧跟引用段落之后，不是堆在末尾）
- [ ] 引用格式正确（上标序号）
- [ ] 参考文献编号与正文引用一一对应
- [ ] 章节标题使用 Heading 1 样式
- [ ] 章节间有分页符
- [ ] 页码正确（封面无页码，摘要目录罗马数字，正文阿拉伯数字）

论文文件：polished_paper.docx
审稿回复：review_response/
图表目录：figures/
PPT文件：presentation.pptx（如有）
需求文件：requirements.md
输出目录：Paper_Delivery_[日期]_[主题]/

只返回生成的目录路径，不要返回其他信息。
```

---

## 学历层次模板

### 专科毕业论文（5000-8000字）

> ⚠️ 专科论文特点：重实操、轻理论，不需要研究意义/目的等空洞章节，重点是系统实现过程

**基于特定系统的标准结构：**
```
摘要（中文即可）
第1章 绪论（简短，300-500字）
  1.1 选题背景（1-2段，说清楚为什么要做这个系统）
  1.2 系统概述（1段，简要介绍系统做什么）
第2章 相关技术介绍（800-1200字）
  2.1 [技术1]（如 Spring Boot）
  2.2 [技术2]（如 Vue.js）
  2.3 [技术3]（如 MySQL）
  ⚠️ 每个技术只写"是什么+为什么用它"，不要大段抄百科
第3章 系统需求分析（800-1200字）
  3.1 功能需求（按系统模块列出）
  3.2 非功能需求（简述）
第4章 系统设计（1200-1500字）
  4.1 系统架构设计（整体架构图）
  4.2 功能模块设计（⚠️ 必须按系统实际模块划分）
  4.3 数据库设计（核心表结构）
第5章 系统实现（1500-2000字，重点章节）
  5.1 开发环境
  5.2 [模块1]实现（⚠️ 必须按系统模块路径编写，展示关键代码和界面截图）
  5.3 [模块2]实现
  5.4 [模块3]实现
  ⚠️ 每个模块必须包含：界面截图 + 关键代码片段 + 功能说明
第6章 系统测试（800-1200字）
  6.1 测试环境
  6.2 功能测试（测试用例表）
  6.3 测试结论
结论（300-500字）
参考文献
致谢
```

**⚠️ 专科论文关键原则：**
1. **砍掉空洞章节**：不写"研究目的与意义"、"国内外研究现状"、"可行性分析"等套话
2. **按系统模块写**：第4-6章必须按照系统实际的功能模块来组织
3. **截图必须有**：每个模块实现必须有系统界面截图
4. **代码要精简**：只展示核心代码（3-5行关键逻辑），不要大段粘贴
5. **数据库表要全**：列出系统所有核心表的字段设计
6. **测试用例表**：至少10个测试用例，覆盖主要功能

### 本科毕业论文（1-2万字）

标准7章结构（引言→技术→需求→设计→实现→测试→结论）。

### 硕士学位论文（3-5万字）

需增加：相关工作深度综述、理论框架、详细实验对比、威胁效度分析等。

## 篇幅模板

| 篇幅 | 页数 | 预计制作时间 |
|------|------|--------------|
| 专科毕业论文 | 10-15页 | 2-3小时 |
| 本科毕业论文 | 15-30页 | 4-6小时 |
| 短文 | 4-6页 | 2-3小时 |
| 标准 | 8-12页 | 4-6小时 |
| 长文 | 15-20页 | 8-10小时 |
| 硕士学位论文 | 50-80页 | 10-15小时 |

---

## 关键约束

### 通用约束
1. **全新实例**：每次执行新任务时，必须调用全新的智能体
2. **无上下文污染**：智能体只返回文件路径，不返回其他信息
3. **最多2轮**：单页审核失败最多重试2次
4. **文件路径通信**：所有智能体之间通过文件路径通信

### 论文工作流额外约束
5. **语言一致**：全文语言必须与 requirements.md 中指定的语言一致
6. **引用规范**：每个论点必须有文献支撑，正文使用上标序号式引用 [1]、[2,3]、[4-6]，文末附按序号排列的完整参考文献列表
7. **目录要求**：论文必须包含目录页，位于摘要之后、正文之前，使用 Word TOC 域代码自动生成
8. **逐章审核**：每章写作完成后必须通过质量检查才能进入下一章
9. **文献追踪**：文献搜索必须包含引用关系追踪，不能只做关键词搜索
10. **⚠️ 审稿模式确定**：阶段1必须明确审稿模式（真实/模拟），不可跳过
11. **⚠️ PPT可选**：阶段8为可选阶段，由用户在阶段1决定
12. **⚠️ 输出双格式**：最终必须同时输出 .docx 和 .pdf 两种格式
13. **⚠️ 图表规范**：所有图表必须 ≥300 DPI，PNG 格式，包含完整标注
14. **⚠️ 图表编号**：图表编号格式为 [图X-Y] / [表X-Y]（X=章节号，Y=序号），图注在图下方居中，表注在表上方居中
15. **⚠️ 图表必须在写作阶段内联插入**：图表必须在阶段5逐章写作时就生成并嵌入到 chapter_N.docx 中（使用 run.add_picture() / doc.add_table()），图表必须紧跟在首次引用该图表的段落之后。禁止事后批量插入（会导致位置错误）。每章生成后必须验证 inline_shapes > 0 且 tables > 0
16. **⚠️ 页码规范**：封面无页码，摘要/目录使用罗马数字页码（i, ii, iii...），正文使用阿拉伯数字页码（1, 2, 3...）从1开始
17. **⚠️ BibTeX完整**：references.bib 必须包含所有被引用的文献，格式正确可解析
18. **⚠️ 引用上标拆分**：引用标记 [N] 必须作为独立 run 并设置 superscript=True，禁止混在正文同一个 run 中（否则上标不生效）
19. **⚠️ 参考文献编号不上标**：参考文献列表中每条的 [N] 编号必须是正常文本，禁止设置 superscript
20. **⚠️ 图片嵌入验证**：插入图片后必须验证 doc.part.rels 中存在 image part，且 inline_shapes 数量 > 0，否则图片无法显示
21. **⚠️ 标题样式与分页**：章节标题必须使用 Heading 1 样式（非 Normal），每个章节标题前必须有分页符
22. **⚠️ Word域代码更新**：页码和目录是域代码，python-docx 无法渲染，必须用 win32com 调用 Word 更新域代码后才能正确显示；PDF 也必须由 Word 导出
23. **⚠️ 分节符必须用Word COM**：python-docx 的分节符在 Word 中会丢失（3节变1节），必须用 `InsertBreak(wdSectionBreakNextPage)` 在"目录"和"第一章"前插入；页码用 `doc.Fields.Add(rng, wdFieldPage)` 插入页脚；中文路径需通过临时英文路径中转
24. **⚠️ 目录位置**：目录必须在摘要之后、正文之前，禁止放到文档最后

---

## 文件结构

```
~/.claude/
├── CLAUDE.md                              # 本文件（主配置）
├── agents/
│   ├── paper_requirement_analyst.md       # 阶段1: 需求分析师
│   ├── paper_code_reader.md               # 阶段1.5: 代码阅读智能体
│   ├── paper_literature_searcher.md       # 阶段2: 文献搜索
│   ├── paper_literature_reviewer.md       # 阶段3: 文献综述
│   ├── paper_framework_designer.md        # 阶段4: 结构设计
│   ├── paper_content_writer.md            # 阶段5: 内容写作+图表嵌入
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
