# Paper Agent Pipeline

> 基于 Claude Code 的多智能体学术论文自动写作系统

一个 9 阶段流水线，通过 10+ 专业智能体协作，从主题到交付完成一篇完整的学术论文。支持通用学术、计算机、历史学、数学建模四种论文分支。

## 简介

**Paper Agent Pipeline** 是一套为 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 设计的多智能体工作流配置。它将学术论文写作拆解为 9 个阶段，每个阶段由专门的智能体负责，通过文件路径进行智能体间通信，最终输出包含规范格式的 `.docx` 和 `.pdf` 论文。

### 核心特性

- **9 阶段流水线**：需求分析 → 文献搜索 → 文献综述 → 结构设计 → 逐章写作（含格式检查） → 学术润色 → 审稿回复 → PPT生成 → 终审交付
- **4 种论文分支**：通用学术、计算机/软件工程、历史学、数学建模，各自有专用的架构设计师和内容写作智能体
- **回退机制**：阶段5/4发现上游问题时可自动回退到阶段4/2修正（大纲修正、文献补搜）
- **人工审核断点**：用户可选择在阶段2、4、5暂停等待审核，支持多选
- **逐章格式检查**：每章写作完成后自动检查字体、字号、行距、引用格式等
- **共享工具脚本**：代码逻辑抽取到独立 `.py` 脚本，智能体文档只保留职责说明和调用方式
- **自动格式规范**：引用上标、页码分节、目录生成、图表编号全部自动处理
- **多语言支持**：中文 / 英文 / 双语论文
- **审稿模式**：支持模拟审稿和真实审稿意见回复

## 架构

```
用户输入主题
     │
     ▼
┌─────────────┐
│ 阶段1: 需求  │ → requirements.md
│  分析师      │    确定论文类型 → 选择分支
└──────┬──────┘
       │
       ├──────────────────────────────────────┐
       │ 通用学术/计算机/历史学分支             │ 数学建模分支
       ▼                                      ▼
┌─────────────┐                         ┌─────────────┐
│ 阶段1.5: 代码│ (可选，仅基于系统的论文)  │ 阶段4: 结构  │ → outline.md
│  阅读        │                         │  设计(建模)  │
└──────┬──────┘                         └──────┬──────┘
       │                                      │
       ▼                                      ▼
┌─────────────┐                         ┌─────────────┐
│ 阶段2: 文献  │ → research/             │ 阶段5: 逐章  │ → chapters/
│  搜索        │                         │  写作(建模)  │   chapter_N.docx
└──────┬──────┘                         └──────┬──────┘
       │                                      │
       ▼                                      │
┌─────────────┐                               │
│ 阶段3: 文献  │ → research/                   │
│  综述        │   literature_review.md        │
└──────┬──────┘                               │
       │                                      │
       ▼                                      │
┌─────────────┐                               │
│ 阶段4: 结构  │ → outline.md                  │
│  设计        │   chapter_plan.md             │
└──────┬──────┘                               │
       │                                      │
       ▼                                      │
┌─────────────┐                               │
│ 阶段5: 逐章  │ → chapters/                   │
│  写作(每章)  │   chapter_N.docx              │
└──────┬──────┘                               │
       │                                      │
       ▼                                      │
┌─────────────┐                               │
│ 阶段5.5: 格式│ → chapters/                   │
│  检查(每章)  │   chapter_N_format_report.md  │
└──────┬──────┘                               │
       │                                      │
       ▼                                      │
       ├──────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│ 阶段6: 学术  │ → polished_paper.docx
│  润色        │   polishing_report.md
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 阶段7: 审稿  │ → review_response/
│  回复        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 阶段8: PPT   │ → presentation.pptx (可选)
│  生成        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 阶段9: 终审  │ → Paper_Delivery_日期_主题/
│  交付        │   ├── paper.docx
└─────────────┘   ├── paper.pdf
                  └── ...

=== 回退通道 ===
阶段5 → 阶段4：大纲逻辑不通时回退修正大纲
阶段5 → 阶段2：文献不足时回退补搜文献
阶段4 → 阶段2：文献综述不足以支撑大纲设计时回退
```

## 前置条件

- **Claude Code** — Anthropic 的 CLI 工具
- **Python 3.10+** — 用于文档处理和图表生成
- **Microsoft Word**（Windows）— 用于域代码更新（`win32com`）
- **Semantic Scholar API Key**（可选）— 用于文献搜索，免费获取

## 安装

### 方法一：使用安装脚本（推荐）

```powershell
# 克隆仓库
git clone https://github.com/LiJzd/paper-agent-pipeline.git
cd paper-agent-pipeline

# 运行安装脚本（Windows PowerShell）
.\install.ps1
```

### 方法二：手动安装

```powershell
# 1. 复制智能体定义
Copy-Item agents\paper_*.md ~/.claude/agents/

# 2. 复制共享工具脚本
Copy-Item -Recurse agents\assets\components\*.py ~/.claude/agents/assets/components/

# 3. 复制内置 Skill
Copy-Item -Recurse skills\literature-search ~/.claude/skills/

# 4. 复制命令桥接文件
Copy-Item commands\nature-*.md ~/.claude/commands/

# 5. 将 CLAUDE.md 的论文工作流部分追加到 ~/.claude/CLAUDE.md
# （如果 ~/.claude/CLAUDE.md 已存在，需要手动合并）
```

### 安装 Python 依赖

```powershell
pip install python-docx matplotlib numpy seaborn bibtexparser docx2pdf
```

### 安装外部 Skills

```powershell
# 安装 nature-skills（MIT 许可证）
git clone https://github.com/Yuan1z0825/nature-skills ~/.claude/skills/nature-skills

# word-document-processor 需要从 Claude Code Skill 市场安装
# 或手动获取后放到 ~/.claude/skills/word-document-processor/
```

## 使用

### 快速开始

在 Claude Code 中输入：

```
帮我写一篇论文，主题是：大语言模型在教育中的应用
```

系统会自动进入阶段1，询问你关于论文类型、语言、篇幅等配置。

### 完整调用示例

#### 通用学术论文

```
帮我写一篇论文，主题是：大语言模型在教育中的应用
- 类型：实证研究
- 语言：中文
- 目标期刊：Computers & Education
- 篇幅：标准（8-12页）
- 需要PPT：是
```

#### 数学建模论文

```
帮我写一篇数学建模论文，题目是：短途运输货量预测与车辆调度优化
- 竞赛类型：全国大学生数学建模竞赛
- 题目类型：D题
- 队伍编号：MC2500XXXX
```

#### 计算机论文

```
帮我写一篇论文，主题是：基于微服务架构的分布式任务调度系统
- 类型：毕业设计
- 语言：中文
- 基于特定系统：是（系统路径：./my-project）
```

### 需求确认

阶段1会询问以下问题：

| 问题 | 选项 | 默认值 |
|------|------|--------|
| 学历层次 | 课堂作业 / 专科 / 本科 / 硕士 / 博士 | 本科 |
| 论文类型 | 实证研究 / 综述 / 理论分析 / 毕业设计 | 实证研究 |
| 论文语言 | 中文 / 英文 / 双语 | 英文 |
| 目标期刊 | 用户指定或"不指定" | 不指定 |
| 是否有真实审稿意见 | 有 / 无 | 无 |
| 是否需要生成演示PPT | 是 / 否 | 否 |
| 预期篇幅 | 课堂作业 / 专科 / 本科 / 短文 / 标准 / 长文 / 硕士 | 标准 |
| 是否基于特定系统 | 是 / 否 | 否 |
| 人工审核断点（多选） | review_literature / review_outline / review_per_chapter / review_draft / 不设 | 不设 |

## 各阶段详解

### 阶段1: 需求分析（5分钟）

**智能体**: `paper_requirement_analyst.md`

解析用户输入，确认论文类型、语言、目标期刊、审稿模式、人工审核断点等参数，输出 `requirements.md` 需求确认单。根据论文类型选择对应分支（通用学术 / 计算机 / 历史学 / 数学建模）。

### 阶段2: 文献搜索（20分钟）

**智能体**: `paper_literature_searcher.md` | **Skill**: `literature-search`

通过 Semantic Scholar API 搜索学术文献，执行：
- 关键词搜索，获取 top 50 篇论文
- 按引用量筛选 top 20 篇
- 深度追踪 top 5 篇的引用关系
- 输出 `research/references_raw.json` 和 `research/top_papers.md`

### 阶段3: 文献综述（20分钟）

**智能体**: `paper_literature_reviewer.md` | **Skill**: `nature-citation`

对搜索结果进行主题分类，撰写结构化文献综述，生成 BibTeX 引用文件：
- 按主题分组（非按时间排列）
- 批判性分析，指出研究间的联系和矛盾
- 明确研究空白
- 输出 `research/literature_review.md` 和 `research/references.bib`

### 阶段4: 结构设计（15分钟）

根据论文类型调用对应的架构设计师：

| 论文类型 | 智能体 |
|----------|--------|
| 通用学术 | `paper_framework_designer.md` |
| 计算机 | `paper_cs_framework_designer.md` |
| 历史学 | `paper_history_framework_designer.md` |
| 数学建模 | `paper_math_modeling_framework_designer.md` |

设计详细大纲，输出 `outline.md` 和 `chapter_plan.md`。

### 阶段5: 逐章写作（每章10-15分钟）

根据论文类型调用对应的内容写作智能体：

| 论文类型 | 智能体 |
|----------|--------|
| 通用学术 | `paper_content_writer.md` |
| 计算机 | `paper_cs_content_writer.md` |
| 历史学 | `paper_history_content_writer.md` |
| 数学建模 | `paper_math_modeling_content_writer.md` |

逐章节撰写学术论文正文，每章生成独立的 `.docx` 文件和章节摘要 `_summary.md`。

### 阶段5.5: 格式检查（每章）

**智能体**: `paper_format_checker.md`

每章写作完成后自动执行格式检查：
- 字体检查（中文宋体 / 英文 Times New Roman）
- 字号、行距、页边距检查
- 图表编号格式检查
- 引用格式检查（无旧格式残留）
- 标题样式和分页符检查
- 输出 `chapters/chapter_{N}_format_report.md`
- 检查不通过则返修（最多2轮）

### 阶段6: 学术润色（20分钟）

**智能体**: `paper_polishing.md` | **Skill**: `nature-polishing`

合并所有章节并进行全文润色：
- 调用 `merge_docx_chapters.py` 合并章节（保留内联图片）
- 学术语言规范化（nature-polishing skill）
- 引用上标修复
- 调用 `word_com_finalize.py` 插入分节符、页码、更新域代码
- 输出 `polished_paper.docx` 和 `polishing_report.md`

### 阶段7: 审稿回复（15分钟）

**智能体**: `paper_review_response.md` | **Skill**: `nature-response`

- **有真实审稿意见**：逐条回复，生成 `review_response/response_to_reviewers.md`
- **无真实审稿意见**：模拟审稿 + 回复，生成 `review_response/simulated_review.md`

### 阶段8: PPT生成（20分钟，可选）

**智能体**: `paper_ppt_generator.md` | **Skill**: `nature-paper2ppt`

将论文核心内容转换为演示 PPT，输出 `presentation.pptx`。

### 阶段9: 终审交付（10分钟）

**智能体**: `paper_delivery.md`

最终质量检查和打包交付：
- 结构完整性检查
- 引用格式验证
- 图片嵌入验证
- 页码和目录验证
- 打包所有文件到 `Paper_Delivery_[日期]_[主题]/`

## 回退机制

论文写作不是严格单向的，阶段5和阶段4会自动检测上游问题并触发回退：

| 触发 | 回退到 | 条件 |
|------|--------|------|
| 阶段5 → 阶段4 | 大纲修正 | 大纲某节逻辑不通、论证链条断裂 |
| 阶段5 → 阶段2 | 文献补搜 | 某论点缺乏文献支撑（<3篇） |
| 阶段4 → 阶段2 | 文献补搜 | 文献综述不足以支撑章节设计 |

回退后输出 `rollback_feedback.md`，回退目标阶段的智能体读取反馈并修正。版本管理：修正后的文件加 `_v2` 后缀，受影响的章节标记为 `_OBSOLETE`。

## 输出结构

```
Paper_Delivery_20260511_主题/
├── paper.docx                 # 论文 Word 版
├── paper.pdf                  # 论文 PDF 版
├── presentation.pptx          # 演示PPT（如有）
├── supplementary/
│   └── figures/               # 图表文件
├── review_response.md         # 审稿回复
├── references.bib             # BibTeX 引用
├── references_list.md         # 按编号排列的参考文献
└── README.md                  # 交付说明
```

## 工作目录结构

运行过程中会在当前目录生成以下中间文件：

```
./
├── requirements.md            # 需求确认单
├── outline.md                 # 论文大纲
├── chapter_plan.md            # 写作计划
├── polished_paper.docx        # 润色后的完整论文
├── rollback_feedback.md       # 回退反馈（如有）
├── research/
│   ├── references_raw.json    # 原始文献数据
│   ├── top_papers.md          # 高影响力论文
│   ├── literature_review.md   # 文献综述
│   └── references.bib         # BibTeX 引用文件
├── chapters/
│   ├── chapter_1.docx
│   ├── chapter_1_summary.md   # 章节摘要（传递给下一章）
│   ├── chapter_1_format_report.md  # 格式检查报告
│   ├── chapter_2.docx
│   └── ...
├── figures/
│   ├── chapter_1/
│   ├── chapter_2/
│   └── ...
└── review_response/
    └── simulated_review.md    # 或 response_to_reviewers.md
```

## 智能体角色表

### 通用智能体（所有分支共享）

| 阶段 | 角色 | 配置文件 |
|------|------|----------|
| 1 | 需求分析师 | `paper_requirement_analyst.md` |
| 1.5 | 代码阅读智能体 | `paper_code_reader.md` |
| 2 | 文献搜索智能体 | `paper_literature_searcher.md` |
| 3 | 文献综述智能体 | `paper_literature_reviewer.md` |
| 5.5 | 格式检查智能体 | `paper_format_checker.md` |
| 6 | 学术润色智能体 | `paper_polishing.md` |
| 7 | 审稿回复智能体 | `paper_review_response.md` |
| 8 | PPT生成智能体 | `paper_ppt_generator.md` |
| 9 | 终审交付智能体 | `paper_delivery.md` |

### 分支专用智能体

| 分支 | 架构设计师（阶段4） | 内容写作（阶段5） |
|------|---------------------|-------------------|
| 通用学术 | `paper_framework_designer.md` | `paper_content_writer.md` |
| 计算机 | `paper_cs_framework_designer.md` | `paper_cs_content_writer.md` |
| 历史学 | `paper_history_framework_designer.md` | `paper_history_content_writer.md` |
| 数学建模 | `paper_math_modeling_framework_designer.md` | `paper_math_modeling_content_writer.md` |

### 共享工具脚本

| 脚本 | 用途 |
|------|------|
| `paper_docx_utils.py` | Word 文档操作（段落、表格、引用、摘要生成） |
| `paper_figure_utils.py` | matplotlib 图表生成（分布图、时序图、热力图等） |
| `paper_delivery_utils.py` | 交付打包（目录创建、PDF生成、参考文献列表） |
| `merge_docx_chapters.py` | 章节合并（保留内联图片） |
| `word_com_finalize.py` | Word COM 收尾（分节符、页码、域代码） |

## 论文类型模板

| 类型 | 章节结构 | 适用场景 |
|------|----------|----------|
| **实证研究** | 引言 → 文献综述 → 研究方法 → 结果 → 讨论 → 结论 | 实验、调查、数据分析 |
| **综述** | 引言 → 背景 → 主题分析（多章） → 讨论与展望 → 结论 | 文献综述、系统综述 |
| **理论分析** | 引言 → 理论框架 → 分析与论证 → 案例研究 → 讨论 → 结论 | 理论探讨、框架构建 |
| **毕业设计（专科）** | 绪论 → 技术介绍 → 需求分析 → 系统设计 → 系统实现 → 测试 → 结论 | 专科毕业论文（5000-8000字） |
| **毕业设计（本科）** | 绪论 → 相关技术 → 需求分析 → 系统设计 → 系统实现 → 测试 → 结论 | 本科毕业论文（1-2万字） |
| **计算机系统设计** | 引言 → 相关工作 → 系统设计 → 实现 → 实验 → 讨论 → 结论 | 系统设计类论文 |
| **计算机算法研究** | 引言 → 相关工作 → 方法 → 实验 → 讨论 → 结论 | 算法/模型研究 |
| **历史学考证** | 绪论 → 史料概述 → 考证（多章） → 结论 | 史料考证 |
| **历史学叙事** | 绪论 → 背景 → 叙事（多章） → 影响评价 → 结论 | 历史叙事 |
| **数学建模** | 问题重述 → 问题分析 → 模型假设 → 符号说明 → 模型建立与求解 → 模型评价 | 数学建模竞赛 |

## 篇幅模板

| 篇幅 | 页数 | 预计制作时间 |
|------|------|--------------|
| 课堂作业 | 3-5页 | 0.5-1小时 |
| 专科毕业论文 | 10-15页 | 2-3小时 |
| 本科毕业论文 | 15-30页 | 4-6小时 |
| 短文 | 4-6页 | 2-3小时 |
| 标准 | 8-12页 | 4-6小时 |
| 长文 | 15-20页 | 8-10小时 |
| 硕士学位论文 | 50-80页 | 10-15小时 |

## 格式规范

本工作流经过多次实战迭代，解决了以下常见格式问题：

### 引用格式

- **正文引用**：上标序号 `[1]`、`[2,3]`、`[4-6]`
- **引用拆分**：`[N]` 必须作为独立 run 并设置 `superscript=True`，否则上标不生效
- **参考文献列表**：文末按编号排列，`[N]` 为正常文本（非上标）

### 图片格式

- **插入方式**：使用 `run.add_picture(path, width=Inches(5.5))`，禁止手动构造 XML drawing
- **编号格式**：[图X-Y] / [表X-Y]（X=章节号，Y=序号）
- **分辨率**：≥300 DPI，PNG 格式
- **验证**：插入后检查 `doc.part.rels` 中存在 image part

### 页码和分节

- **封面**：无页码
- **摘要/目录**：罗马数字页码（i, ii, iii...）
- **正文**：阿拉伯数字页码（1, 2, 3...），从1开始
- **分节符**：用 Word COM 的 `InsertBreak(wdSectionNextPage)` 插入（封装在 `word_com_finalize.py`）
- **域代码**：用 `win32com` 调用 Word 更新后才能渲染（封装在 `word_com_finalize.py`）

### 标题和分页

- **章节标题**：必须使用 Heading 1 样式（非 Normal）
- **分页符**：每个章节标题前必须有分页符
- **目录**：使用 Word TOC 域代码自动生成

## 已知问题与解决方案

### 1. python-docx 分节符在 Word 中丢失

**问题**：python-docx 创建的 section 在 Word 中会合并为1节。
**解决**：用 Word COM 的 `InsertBreak(wdSectionBreakNextPage)` 插入分节符。

### 2. 引用上标不生效

**问题**：引用 [N] 混在正文同一个 run 中，superscript 设置无效。
**解决**：用 `re.split` 将 [N] 拆分为独立 run，再设置 `superscript=True`。

### 3. 图片无法显示

**问题**：手动构造 XML drawing 会产生断裂引用。
**解决**：必须用 `run.add_picture()` 方法插入图片。

### 4. 页码和目录不显示

**问题**：python-docx 的域代码在 Word 中不会自动渲染。
**解决**：用 `win32com` 调用 Word 更新所有域代码。

### 5. 中文路径导致 COM 失败

**问题**：Word COM 无法处理中文字符路径。
**解决**：先复制到临时英文路径操作，完成后再复制回来。

### 6. 参考文献编号误上标

**问题**：参考文献列表的 [N] 被错误设为上标。
**解决**：参考文献章节之后的 run，若以 [数字] 开头则设 `superscript=False`。

### 7. 标题样式不一致

**问题**：部分章节标题为 Normal 而非 Heading 1。
**解决**：合并后遍历段落，以"第X章"开头的设为 Heading 1。

## 外部依赖

| 依赖 | 许可证 | 用途 | 安装方式 |
|------|--------|------|----------|
| [nature-skills](https://github.com/Yuan1z0825/nature-skills) | MIT | 引用、润色、图表、审稿回复等 6 个 Skill | `git clone` |
| word-document-processor | Anthropic 专有 | Word 文档创建和编辑 | Claude Code Skill 市场 |
| [Semantic Scholar API](https://www.semanticscholar.org/product/api) | 免费 | 文献搜索 | 获取 API Key |

### Python 依赖

```powershell
pip install python-docx matplotlib numpy seaborn bibtexparser docx2pdf
```

| 包 | 用途 |
|----|------|
| python-docx | Word 文档创建和编辑 |
| matplotlib | 图表生成 |
| numpy | 数值计算 |
| seaborn | 统计图表美化 |
| bibtexparser | BibTeX 解析 |
| docx2pdf | PDF 导出（可选，需要 Word） |

## 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境

```bash
# 克隆仓库
git clone https://github.com/LiJzd/paper-agent-pipeline.git
cd paper-agent-pipeline

# 安装 Python 依赖
pip install python-docx matplotlib numpy seaborn bibtexparser docx2pdf requests
```

### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 [MIT License](LICENSE)。

## 致谢

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — Anthropic 的 CLI 工具
- [nature-skills](https://github.com/Yuan1z0825/nature-skills) — Nature 风格学术 Skill 集合
- [Semantic Scholar](https://www.semanticscholar.org/) — 学术文献搜索 API
