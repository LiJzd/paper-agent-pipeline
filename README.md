# Paper Agent Pipeline

> 基于 Claude Code 的多智能体学术论文自动写作系统

一个 9 阶段流水线，通过 10 个专业智能体协作，从主题到交付完成一篇完整的学术论文。

## 简介

**Paper Agent Pipeline** 是一套为 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 设计的多智能体工作流配置。它将学术论文写作拆解为 9 个阶段，每个阶段由专门的智能体负责，通过文件路径进行智能体间通信，最终输出包含规范格式的 `.docx` 和 `.pdf` 论文。

### 核心特性

- **9 阶段流水线**：需求分析 → 文献搜索 → 文献综述 → 结构设计 → 逐章写作 → 学术润色 → 审稿回复 → PPT生成 → 终审交付
- **10 个专业智能体**：每个阶段有独立的智能体定义，无上下文污染
- **自动格式规范**：引用上标、页码分节、目录生成、图表编号全部自动处理
- **多语言支持**：中文 / 英文 / 双语论文
- **多种论文类型**：实证研究、综述、理论分析
- **审稿模式**：支持模拟审稿和真实审稿意见回复

## 架构

```
用户输入主题
     │
     ▼
┌─────────────┐
│ 阶段1: 需求  │ → requirements.md
│  分析师      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 阶段2: 文献  │ → research/references_raw.json
│  搜索        │   research/top_papers.md
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 阶段3: 文献  │ → research/literature_review.md
│  综述        │   research/references.bib
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 阶段4: 结构  │ → outline.md
│  设计        │   chapter_plan.md
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ 阶段5: 内容  │────→│ 阶段5a: 图表 │
│  写作(每章)  │     │  生成(每章)  │
└──────┬──────┘     └──────┬──────┘
       │                   │
       │   chapters/       │   figures/
       │   chapter_N.docx  │   chapter_N/
       ▼                   ▼
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
```

## 前置条件

- **Claude Code** — Anthropic 的 CLI 工具
- **Python 3.10+** — 用于文献搜索脚本和文档处理
- **Microsoft Word**（Windows）— 用于域代码更新和 PDF 导出（`win32com`）
- **Semantic Scholar API Key**（可选）— 用于文献搜索，免费获取

## 安装

### 方法一：使用安装脚本（推荐）

```powershell
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/paper-agent-pipeline.git
cd paper-agent-pipeline

# 运行安装脚本（Windows PowerShell）
.\install.ps1
```

### 方法二：手动安装

```powershell
# 1. 复制智能体定义
Copy-Item agents\paper_*.md ~/.claude/agents/

# 2. 复制内置 Skill
Copy-Item -Recurse skills\literature-search ~/.claude/skills/

# 3. 复制命令桥接文件
Copy-Item commands\nature-*.md ~/.claude/commands/

# 4. 将 CLAUDE.md 的论文工作流部分追加到 ~/.claude/CLAUDE.md
# （如果 ~/.claude/CLAUDE.md 已存在，需要手动合并）
```

### 安装外部依赖

```powershell
# 安装 nature-skills（MIT 许可证）
git clone https://github.com/Yuan1z0825/nature-skills ~/ai-skills/nature-skills

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

```
帮我写一篇论文，主题是：大语言模型在教育中的应用
- 类型：实证研究
- 语言：中文
- 目标期刊：Computers & Education
- 篇幅：标准（8-12页）
- 需要PPT：是
```

### 需求确认

阶段1会询问以下问题：

| 问题 | 选项 | 默认值 |
|------|------|--------|
| 论文类型 | 实证研究 / 综述 / 理论分析 | 实证研究 |
| 论文语言 | 中文 / 英文 / 双语 | 英文 |
| 目标期刊 | 用户指定或"不指定" | 不指定 |
| 是否有真实审稿意见 | 有 / 无 | 无 |
| 是否需要生成演示PPT | 是 / 否 | 否 |
| 预期篇幅 | 短文(4-6页) / 标准(8-12页) / 长文(15-20页) | 标准 |

## 各阶段详解

### 阶段1: 需求分析（5分钟）

**智能体**: `paper_requirement_analyst.md`

解析用户输入，确认论文类型、语言、目标期刊、审稿模式等参数，输出 `requirements.md` 需求确认单。

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

**智能体**: `paper_framework_designer.md`

根据论文类型设计详细大纲：
- 实证研究：引言 → 文献综述 → 研究方法 → 结果 → 讨论 → 结论
- 综述：引言 → 背景 → 主题分析 → 讨论与展望 → 结论
- 理论分析：引言 → 理论框架 → 分析与论证 → 案例研究 → 讨论 → 结论
- 输出 `outline.md` 和 `chapter_plan.md`

### 阶段5: 逐章写作（每章10-15分钟）

**智能体**: `paper_content_writer.md` | **Skill**: `word-document-processor`

逐章节撰写学术论文正文，每章生成独立的 `.docx` 文件。关键格式要求：
- 引用 [N] 必须拆分为独立 run 并设置上标
- 图片使用 `run.add_picture()` 插入，禁止手动构造 XML
- 章节标题使用 Heading 1 样式
- 输出 `chapters/chapter_{N}.docx`

### 阶段5a: 图表生成（每章）

**智能体**: `paper_figure_agent.md` | **Skill**: `nature-figure` + `nature-data`

为每章生成科研图表：
- ≥300 DPI，PNG 格式
- 编号格式：[图X-Y] / [表X-Y]
- 输出 `figures/chapter_{N}/`

### 阶段6: 学术润色（20分钟）

**智能体**: `paper_polishing.md` | **Skill**: `nature-polishing`

合并所有章节并进行全文润色：
- 学术语言规范化
- 格式一致性检查
- 引用上标修复
- 标题样式和分页符修复
- 插入目录（TOC 域代码）
- 用 Word COM 插入分节符和页码
- 更新域代码并导出 PDF
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
├── research/
│   ├── references_raw.json    # 原始文献数据
│   ├── top_papers.md          # 高影响力论文
│   ├── literature_review.md   # 文献综述
│   └── references.bib         # BibTeX 引用文件
├── chapters/
│   ├── chapter_1.docx
│   ├── chapter_2.docx
│   └── ...
├── figures/
│   ├── chapter_1/
│   ├── chapter_2/
│   └── ...
└── review_response/
    └── simulated_review.md    # 或 response_to_reviewers.md
```

## 论文类型模板

| 类型 | 章节结构 | 适用场景 |
|------|----------|----------|
| **实证研究** | 引言 → 文献综述 → 研究方法 → 结果 → 讨论 → 结论 | 实验、调查、数据分析 |
| **综述** | 引言 → 背景 → 主题分析（多章） → 讨论与展望 → 结论 | 文献综述、系统综述 |
| **理论分析** | 引言 → 理论框架 → 分析与论证 → 案例研究 → 讨论 → 结论 | 理论探讨、框架构建 |

## 篇幅模板

| 篇幅 | 页数 | 预计制作时间 | 章节数 |
|------|------|--------------|--------|
| 短文 | 4-6页 | 2-3小时 | 4-5章 |
| 标准 | 8-12页 | 4-6小时 | 6章 |
| 长文 | 15-20页 | 8-10小时 | 7-8章 |

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
- **分节符**：必须用 Word COM 的 `InsertBreak(wdSectionBreakNextPage)` 插入（python-docx 的分节符在 Word 中会丢失）
- **域代码**：页码和目录是域代码，必须用 `win32com` 调用 Word 更新后才能渲染

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
**解决**：用 `win32com` 调用 Word 更新所有域代码后导出 PDF。

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

## 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/paper-agent-pipeline.git
cd paper-agent-pipeline

# 安装 Python 依赖（用于文献搜索）
pip install requests

# 安装 python-docx（用于文档处理）
pip install python-docx
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
