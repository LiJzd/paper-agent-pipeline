# CLAUDE.md - 多智能体协作配置

## 三个工作流

| 工作流 | 用途 | 触发方式 | 智能体数量 |
|--------|------|----------|------------|
| **编码工作流** | 通用软件开发 | "帮我写一个XXX功能" | 3个 |
| **PPT工作流** | 专业PPT制作 | "帮我做一个PPT" | 9个 |
| **论文工作流** | 学术论文/数学建模 | "帮我写一篇论文" | 8-11个（按类型） |

---

## 工作流1: 编码工作流

### 智能体角色

| 角色 | 职责 | 配置文件 |
|------|------|----------|
| 主智能体 (Orchestrator) | 任务协调、拆解、分配 | `orchestrator.md` |
| 编码智能体 (Coder) | 编写代码 | `coder.md` |
| 评审智能体 (Reviewer) | 评审代码质量 | `reviewer.md` |

### 工作流程
```
1. 主智能体接收任务
2. 拆解为子任务
3. 对每个子任务：编码(新)→评审(新)→不通过则修复重审(最多3轮)
4. 整合结果
```

### 调用方式
```
帮我写一个 [功能描述]
```

---

## 工作流2: PPT工作流

### 智能体角色（9个）

| 阶段 | 角色 | 配置文件 |
|------|------|----------|
| 0 | 素材提取师 | `ppt_extractor.md` |
| 1 | 需求分析师 | `ppt_requirement_analyst.md` |
| 2 | 内容研究员 | `ppt_content_researcher.md` |
| 3 | 架构设计师 | `ppt_framework_designer.md` |
| 4 | 协调智能体 | `ppt_coordinator.md` |
| 4a | 内容智能体(每页) | `ppt_page_content.md` |
| 4b | 素材智能体(每页) | `ppt_page_asset.md` |
| 4c | 审核智能体(每页) | `ppt_page_review.md` |
| 5 | 终审智能体 | `ppt_reviewer.md` |
| 6 | 交付协调员 | `ppt_delivery.md` |

### 工作流程
```
阶段0: 素材提取（可选）
阶段1: 需求确认 → requirements.md
阶段2: 内容搜索 → research/
阶段3: 逐页大纲 → outline.md
阶段4: 逐页协作构建（每页3-5分钟）：
  对每一页:
    内容智能体(新) → 布局规范
    素材智能体(新) → 页面代码
    审核智能体(新) → 审核报告（不通过则重试最多2次）
  协调智能体组装 → create_ppt.py + presentation.pptx + presentation.html
阶段5: 终审 → final_review.md
阶段6: 交付 → PPT_Delivery_*/
```

### ⛔ 素材库验证（阶段5.5 - 强制执行）

在调用终审智能体之前，检查生成的脚本是否使用了PPTBuilder：

```bash
grep -c "from ppt_builder import PPTBuilder\|PPTBuilder" [脚本文件]
```

匹配数为0则重新调用ppt_coder重写。最多重试2次。

### 设计规范
- 配色方案：学术蓝/学术绿/简约黑/暗色科技/农业绿/芯动忆生蓝/茶园绿
- 字体规范：微软雅黑 + Arial/Helvetica
- 图表规范：300 DPI+，PNG格式

### 时长模板

| 时长 | 页数 | 预计制作时间 |
|------|------|--------------|
| 5分钟 | 5-8页 | 1-1.5小时 |
| 15分钟 | 15-20页 | 2-3小时 |
| 30分钟 | 20-30页 | 4-5小时 |
| 60分钟 | 30-50页 | 6-8小时 |

---

## 工作流3: 论文工作流

### 快速使用
```
帮我写一篇论文，主题是：[你的主题]
```

### 论文类型分支

| 论文类型 | 触发关键词 | 架构设计师 | 编写智能体 |
|----------|------------|------------|------------|
| **通用学术论文** | 实证研究/综述/理论分析/毕业设计 | `paper_framework_designer.md` | `paper_content_writer.md` |
| **计算机/软件工程** | 计算机/软件/系统/算法/深度学习 | `paper_cs_framework_designer.md` | `paper_cs_content_writer.md` |
| **历史学** | 历史/史料/考证/古代/近代 | `paper_history_framework_designer.md` | `paper_history_content_writer.md` |
| **数学建模** | 数学建模/建模竞赛/国赛/美赛 | `paper_math_modeling_framework_designer.md` | `paper_math_modeling_content_writer.md` |

### 智能体角色

#### 通用智能体（所有类型共享）

| 阶段 | 角色 | 配置文件 |
|------|------|----------|
| 1 | 需求分析师 | `paper_requirement_analyst.md` |
| 1.5 | 代码阅读智能体 | `paper_code_reader.md` |
| 2 | 文献搜索智能体 | `paper_literature_searcher.md` |
| 3 | 文献综述智能体 | `paper_literature_reviewer.md` |
| 4.5 | ⚠️ 结果构建智能体(仅数学建模) | `paper_math_modeling_result_builder.md` |
| 5.5 | 格式检查智能体 | `paper_format_checker.md` |
| 6 | 学术润色智能体 | `paper_polishing.md` |
| 8.5 | ⚠️ 一致性审计智能体(仅数学建模) | `paper_consistency_auditor.md` |
| 8.6 | ⚠️ 图表账本检查(自动化脚本) | `artifact_checker.py` |
| 8.7 | ⚠️ 正文验证智能体(仅数学建模) | `paper_final_consistency_verifier.md` |
| 7 | 审稿回复智能体 | `paper_review_response.md` |
| 8 | PPT生成智能体 | `paper_ppt_generator.md` |
| 9 | 终审交付智能体 | `paper_delivery.md` |

### 工作流程

```
【通用学术/计算机/历史分支】          【数学建模分支（13阶段）】
        ↓                                   ↓
阶段1: 需求分析                      阶段1: problem_parser → problem_spec.json
        ↓                                   ↓
阶段1.5: 代码阅读(可选)              阶段2: solution_planner → solution_plan.json
        ↓                                   ↓
阶段2: 文献搜索                      阶段3: result_builder → results_master.json
        ↓                                   ↓
阶段3: 文献综述                      阶段4: canonical_table_gen → tables/*.csv
        ↓                                   ↓
阶段4: 结构设计                      阶段5: figure_generator → figures/*.png
        ↓                                   ↓
阶段5: 逐章写作                      阶段6: artifact_manifest_builder → artifact_manifest.json
        ↓                                   ↓
阶段6-9: 润色→审稿→交付              阶段7: chapter_writer → chapters/chapter_N.docx（骨架模式）
                                       ↓
                                      阶段8: evidence_based_expander → chapter_N_expanded.docx
                                       ↓
                                      阶段9: abstract_writer → 摘要/结论（最后编写）
                                       ↓
                                      阶段10: consistency_checker → 结果账本内部一致性
                                       ↓
                                      阶段11: artifact_checker → 图表账本一致性
                                       ↓
                                      阶段12: document_verifier → 正文与账本一致性
                                       ↓
                                      阶段13: delivery → 终审交付
```

#### 逐章写作循环（阶段7→8）
```
对每章:
  chapter_writer(新) → chapter_{N}.docx + chapter_{N}_summary.md + chapter_{N}_requests.md
  evidence_based_expander(新) → chapter_{N}_expanded.docx + chapter_{N}_expansion_log.md
```

#### 检查阶段 fail-fast
```
阶段10-12 任一 checker status=failed → 立即停止，输出错误报告
不得跳过检查进入交付阶段
```

#### 回退通道
- 阶段7→阶段4：大纲逻辑不通 → 输出 rollback_feedback.md → 重新设计大纲
- 阶段7→阶段2：文献不足 → 输出 rollback_feedback.md → 补搜文献
- 回退次数限制：同一方向最多1次，累计最多2次

### 需求确认时询问的问题

| 问题 | 选项 | 默认值 |
|------|------|--------|
| 学历层次 | 课堂作业 / 专科 / 本科 / 硕士 / 博士 | 本科 |
| 论文类型 | 实证研究 / 综述 / 理论分析 / 毕业设计 | 实证研究 |
| 论文语言 | 中文 / 英文 / 双语 | 英文 |
| 目标期刊 | 用户指定或"不指定" | 不指定 |
| 是否有真实审稿意见 | 有 / 无 | 无 |
| 是否需要生成演示PPT | 是 / 否 | 否 |
| 预期篇幅 | 见下方模板 | 标准 |
| 是否基于特定系统 | 是 / 否 | 否 |
| 人工审核断点（多选） | review_literature / review_outline / review_per_chapter / review_draft / 无 | 无 |

### 篇幅模板

| 篇幅 | 页数 | 预计制作时间 |
|------|------|--------------|
| 课堂作业 | 3-5页 | 0.5-1小时 |
| 专科毕业论文 | 10-15页 | 2-3小时 |
| 本科毕业论文 | 15-30页 | 4-6小时 |
| 短文 | 4-6页 | 2-3小时 |
| 标准 | 8-12页 | 4-6小时 |
| 长文 | 15-20页 | 8-10小时 |
| 硕士学位论文 | 50-80页 | 10-15小时 |

### 数学建模论文结构（15-30页）

```
封面（队伍编号、题号、标题）
摘要（300-500字，包含具体数据结果）⚠️ 求解完成后编写
关键词（5-8个，分号分隔）

目录

一、问题重述（1-2页）
二、问题分析（2-3页）
三、模型假设（0.5-1页）
四、符号说明（0.5-1页）
五、模型建立与求解（10-20页，核心）
六、模型评价与优化（1-2页）
七、参考文献
八、附录（代码+数据）
```

### ⚠️ 数学建模关键原则

1. **结果先于写作**：先求解生成 results_master.json，再写作（阶段3→阶段7）
2. **表格/图表先于正文**：先生成 tables/*.csv 和 figures/*.png，再解释（阶段4-6→阶段7）
3. **摘要最后写**：所有问题求解完成后，仅引用 summary_claims 中 scope 含 "abstract" 的证据包
4. **骨架+扩写分离**：chapter_writer 生成骨架（含 NEED_EXPANSION 标记），evidence_based_expander 基于证据扩写
5. **按问题组织**：每章对应一个问题，包含完整建模过程
6. **公式独立成行**：所有重要公式独立成行，右对齐编号 (1), (2), ...
7. **符号首次定义**：每个符号首次出现时必须有定义和单位
8. **图表必须内联**：生成后立即嵌入，用Read工具验证中文渲染
9. **三层检查必过**：consistency_checker + artifact_checker + document_verifier 任一 failed 不得交付

### ⚠️ 数学建模专用智能体

| 阶段 | 角色 | 配置文件 | 类型 |
|------|------|----------|------|
| 3 | 结果构建智能体 | `paper_math_modeling_result_builder.md` | agent |
| 7 | 骨架写作智能体 | `paper_math_modeling_content_writer.md` | agent |
| 8 | 证据扩写智能体 | `paper_evidence_based_expander.md` | agent |
| 9 | 摘要编写智能体 | (复用 chapter_writer 或专用) | agent |
| 10 | 一致性检查器 | `consistency_checker.py` | script |
| 11 | 图表账本检查器 | `artifact_checker.py` | script |
| 12 | 正文验证器 | `final_document_verifier.py` | script |

### ⚠️ 结果账本制度 (results_master.json)

所有关键数字必须从 `artifacts/results_master.json` 读取，通过 `ResultStore` 类：
```python
from result_store import ResultStore
store = ResultStore("artifacts/results_master.json")
rmse = store.require("problem2.metrics.Prophet.rmse")  # 缺失则报错
path = store.get("problem2.forecast_table")             # 缺失返回 None
```

**Schema 扩展字段**：
- `method_config`: 全局方法参数（train_test_split, cv_folds 等）
- `derived_claims`: 推导结论（中间结论）
- `summary_claims`: 摘要结论（仅 scope 含 "abstract" 的可在摘要中使用）
- `data_requests` / `artifact_requests`: 缺失项记录

### ⚠️ A/B/C 数字分类（正文验证器）

| 类别 | 含义 | 缺失时处理 |
|------|------|------------|
| A | 关键结果指标（R2, RMSE, 利润率等） | error（关键段落）/ warning（背景段落） |
| B | 方法参数（训练比例, 交叉验证折数等） | warning |
| C | 背景信息（年份, 页码, 序号等） | 忽略 |

---

## 关键约束（全局）

### 通用约束
1. **全新实例**：每次调用新智能体，无上下文
2. **文件路径通信**：智能体之间通过文件路径传递结果
3. **最多2轮**：单页/单章审核失败最多重试2次

### 论文工作流关键约束
4. **语言一致**：全文语言与requirements.md一致
5. **引用规范**：正文上标序号 [1]，文末完整列表
6. **目录在摘要之后、正文之前**
7. **逐章审核**：每章写作完成后必须通过质量检查
8. **⚠️ 图表必须在写作阶段内联插入**：禁止事后批量插入
9. **⚠️ 章节摘要传递机制**：每章生成chapter_{N}_summary.md，下一章必须读取
10. **⚠️ 回退机制必须启用**：发现问题输出rollback_feedback.md，不强行继续
11. **⚠️ 人工审核断点必须检查**：命中断点时必须暂停等待用户反馈

### 数学建模专用约束（仅数学建模分支）
12. **⚠️ 结果先于写作**：阶段3 生成 results_master.json 后才能进入阶段7 写作
13. **⚠️ 结果账本制度**：所有关键数字必须从 results_master.json 读取（ResultStore.require()）
14. **⚠️ 禁止自行生成数字**：章节 agent 不得自行生成模型指标、利润、达标率等关键数字
15. **⚠️ 骨架+扩写分离**：chapter_writer 只生成骨架（含 NEED_EXPANSION），evidence_based_expander 基于证据扩写
16. **⚠️ 摘要最后编写**：仅引用 summary_claims 中 scope 含 "abstract" 的证据包
17. **⚠️ 三层检查必过**：consistency_checker + artifact_checker + document_verifier 任一 failed 不得交付
18. **⚠️ 图表账本制度**：每个图表/表格必须在 artifact_manifest.json 中登记 source_keys、data_path、allowed_claims
19. **⚠️ 回归测试**：新增 `test_real_paper_regression.py` 覆盖 7 类已知错误模式

### PPT工作流关键约束
12. **设计一致性**：全文配色、字体、卡片样式统一
13. **素材库优先**：优先使用已提取的组件
14. **布局必须多样**：禁止连续两页相同布局
15. **双格式输出**：同时输出 .pptx 和 .html

---

## 文件结构

```
~/.claude/
├── CLAUDE.md                          # 本文件（主配置）
├── agents/
│   ├── orchestrator.md                # 编码工作流 - 主智能体
│   ├── coder.md                       # 编码工作流 - 编码智能体
│   ├── reviewer.md                    # 编码工作流 - 评审智能体
│   ├── ppt_extractor.md               # PPT工作流 - 素材提取师
│   ├── ppt_requirement_analyst.md     # PPT工作流 - 需求分析师
│   ├── ppt_content_researcher.md      # PPT工作流 - 内容研究员
│   ├── ppt_framework_designer.md      # PPT工作流 - 架构设计师
│   ├── ppt_coordinator.md             # PPT工作流 - 协调智能体
│   ├── ppt_page_content.md            # PPT工作流 - 内容智能体（单页）
│   ├── ppt_page_asset.md              # PPT工作流 - 素材智能体（单页）
│   ├── ppt_page_review.md             # PPT工作流 - 审核智能体（单页）
│   ├── ppt_reviewer.md                # PPT工作流 - 终审智能体
│   ├── ppt_delivery.md                # PPT工作流 - 交付协调员
│   ├── ppt_design_skills.md           # PPT设计规范
│   ├── ppt_workflow.md                # PPT工作流详细文档
│   ├── ppt_quickref.md                # PPT快速参考卡
│   ├── paper_requirement_analyst.md   # 论文工作流 - 需求分析师
│   ├── paper_literature_searcher.md   # 论文工作流 - 文献搜索智能体
│   ├── paper_literature_reviewer.md   # 论文工作流 - 文献综述智能体
│   ├── paper_framework_designer.md    # 论文工作流 - 架构设计师（通用学术分支）
│   ├── paper_content_writer.md        # 论文工作流 - 内容写作智能体（通用学术分支）
│   ├── paper_cs_framework_designer.md # 论文工作流 - 架构设计师（计算机分支）
│   ├── paper_cs_content_writer.md     # 论文工作流 - 内容写作智能体（计算机分支）
│   ├── paper_history_framework_designer.md # 论文工作流 - 架构设计师（历史学分支）
│   ├── paper_history_content_writer.md     # 论文工作流 - 内容写作智能体（历史学分支）
│   ├── paper_math_modeling_framework_designer.md  # 论文工作流 - 架构设计师（数学建模分支）
│   ├── paper_math_modeling_content_writer.md      # 论文工作流 - 骨架写作智能体（数学建模分支）
│   ├── paper_evidence_based_expander.md           # 论文工作流 - 证据扩写智能体（数学建模分支）
│   ├── paper_math_modeling_figure_agent.md        # 论文工作流 - 图表生成智能体（数学建模分支）
│   ├── paper_figure_agent.md          # 论文工作流 - 图表智能体
│   ├── paper_polishing.md             # 论文工作流 - 学术润色智能体
│   ├── paper_format_checker.md        # 论文工作流 - 格式检查智能体
│   ├── paper_review_response.md       # 论文工作流 - 审稿回复智能体
│   ├── paper_ppt_generator.md         # 论文工作流 - PPT生成智能体
│   ├── paper_delivery.md              # 论文工作流 - 终审交付智能体
│   └── assets/
│       ├── components/
│       │   ├── ppt_builder.py             # PPTBuilder（python-pptx）
│       │   ├── html_ppt_builder.py        # HTMLPPTBuilder（Reveal.js HTML）
│       │   ├── revealjs/                  # Reveal.js 核心文件
│       │   ├── merge_docx_chapters.py     # 论文章节合并脚本（保留图片）
│       │   ├── word_com_finalize.py       # Word COM 收尾脚本（分节符/页码/域代码）
│       │   ├── result_store.py            # 结果账本读取器（get/require）
│       │   ├── consistency_checker.py     # 结果账本内部一致性检查（含 method_config/derived_claims 验证）
│       │   ├── final_document_verifier.py # 论文正文一致性验证（含 A/B/C 数字分类）
│       │   ├── artifact_manifest.py       # 图表账本读取器
│       │   ├── artifact_checker.py        # 图表账本一致性检查
│       │   ├── generate_tables.py         # 从 results_master 生成表格 CSV
│       │   ├── generate_figures.py        # 从 figure_data 生成图表 PNG
│       │   ├── build_results.py           # 构建 results_master.json（含 method_config/derived_claims 等扩展字段）
│       │   ├── section_expansion_plan.py  # 逐节扩写配置（目标字数、扩写目标、必需 source_keys）
│       │   ├── expand_section_helpers.py  # 扩写辅助工具（ExpansionLogger/SourceKeyValidator/ClaimValidator）
│       │   ├── run_math_modeling_pipeline.py  # 数学建模 13 阶段流水线
│       │   └── test_real_paper_regression.py  # 回归测试（7 类已知错误模式）
│       ├── math_modeling_template.md  # 数学建模论文模板
│       └── reference_analysis/
│           └── layout_patterns.md     # 布局模式库
├── skills/
│   └── literature-search/             # 文献搜索 skill
└── memory/
    └── ...                            # 持久化记忆
```

---

## 快速参考

### 我想写代码
```
帮我写一个 [功能描述]
```

### 我想做PPT
```
帮我做一个 PPT，主题是：[主题]
```

### 我想写论文
```
帮我写一篇论文，主题是：[主题]
```
