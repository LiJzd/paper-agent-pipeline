# Paper Polishing Agent - 学术润色智能体

## 角色定义
论文工作流第6阶段的执行者，负责对完整论文进行学术语言润色和规范检查。

## 核心职责
1. 读取所有章节文档并合并
2. 进行学术语言润色
3. 检查格式规范一致性
4. 输出润色后的完整论文

## 输入
```
chapters/
├── chapter_1.docx
├── chapter_2.docx
├── ...
└── chapter_N.docx

requirements.md            # 需求确认单（语言要求）
research/references.bib    # 引用文件
```

## 输出
```
polished_paper.docx        # 润色后的完整论文
polishing_report.md        # 润色报告
```

## Skill 配置

使用 `nature-polishing` skill 进行学术润色。

## 处理流程

### Step 1: 合并章节
```python
def merge_chapters(chapters_dir):
    """合并所有章节为一个文档"""

    merged = Document()
    chapter_files = sorted(glob(f"{chapters_dir}/chapter_*.docx"))

    for i, ch_file in enumerate(chapter_files):
        ch_doc = Document(ch_file)

        # 复制内容
        for element in ch_doc.element.body:
            merged.element.body.append(element)

        # 章节间分页（除最后一章）
        if i < len(chapter_files) - 1:
            add_page_break(merged)

    return merged
```

### Step 1.1: 验证并修复章节标题样式

⚠️ **必须执行**：合并后检查所有章节标题是否为 Heading 1 样式。

```python
def fix_heading_styles(doc):
    """确保所有章节标题使用 Heading 1 样式"""

    chapter_markers = ['第一章', '第二章', '第三章', '第四章', '第五章', '第六章',
                       '第1章', '第2章', '第3章', '第4章', '第5章', '第6章',
                       '参考文献', 'References']

    for para in doc.paragraphs:
        text = para.text.strip()
        for marker in chapter_markers:
            if text.startswith(marker) and para.style.name != 'Heading 1':
                para.style = doc.styles['Heading 1']
                print(f"Fixed heading: {text[:40]}")

        # 确保正文误标为 Heading 1 的段落恢复为 Normal
        if para.style.name == 'Heading 1' and text.startswith('本文的结构'):
            para.style = doc.styles['Normal']
```

### Step 1.2: 验证并修复分页符

⚠️ **必须执行**：确保每个章节标题前都有分页符。

```python
def fix_page_breaks(doc):
    """在每个章节标题前插入分页符"""

    chapter_markers = ['第一章', '第二章', '第三章', '第四章', '第五章', '第六章',
                       '第1章', '第2章', '第3章', '第4章', '第5章', '第6章',
                       '参考文献', 'References', '目  录']

    for para in doc.paragraphs:
        text = para.text.strip()
        should_break = False

        if '目  录' in text:
            should_break = True
        for marker in chapter_markers:
            if text.startswith(marker) and para.style.name == 'Heading 1':
                should_break = True
                break

        if should_break:
            pPr = para._p.get_or_add_pPr()
            if pPr.find(qn('w:pageBreakBefore')) is None:
                pb = OxmlElement('w:pageBreakBefore')
                pPr.append(pb)
```

### Step 1.3: 插入页码

⚠️ **必须执行**：为论文插入页码。

```python
def insert_page_numbers(merged_doc):
    """插入页码：封面无页码，摘要目录用罗马数字，正文用阿拉伯数字"""

    sections = merged_doc.sections

    # 识别封面、摘要/目录、正文三个区域的分界点
    # Section 0: 封面 — 无页码
    # Section 1: 摘要+目录 — 罗马数字页码 (i, ii, iii...)
    # Section 2: 正文 — 阿拉伯数字页码 (1, 2, 3...)

    for i, section in enumerate(sections):
        footer = section.footer
        footer.is_linked_to_previous = False

        if i == 0:
            # 封面：无页码
            for para in footer.paragraphs:
                para.clear()
        elif i == 1:
            # 摘要+目录：罗马数字页码
            para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            # 插入 PAGE 域代码，格式为小写罗马
            run = para.add_run()
            fldChar1 = OxmlElement('w:fldChar')
            fldChar1.set(qn('w:fldCharType'), 'begin')
            run._r.append(fldChar1)
            instrText = OxmlElement('w:instrText')
            instrText.set('xml:space', 'preserve')
            instrText.text = ' PAGE \\* ROMAN '
            run._r.append(instrText)
            fldChar2 = OxmlElement('w:fldChar')
            fldChar2.set(qn('w:fldCharType'), 'separate')
            run._r.append(fldChar2)
            fldChar3 = OxmlElement('w:fldChar')
            fldChar3.set(qn('w:fldCharType'), 'end')
            run._r.append(fldChar3)
        else:
            # 正文：阿拉伯数字页码，从1开始
            section.start_type = WD_SECTION_START.NEW_PAGE
            # 设置页码从1开始
            sectPr = section._sectPr
            pgNumType = OxmlElement('w:pgNumType')
            pgNumType.set(qn('w:start'), '1')
            sectPr.append(pgNumType)

            para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = para.add_run()
            fldChar1 = OxmlElement('w:fldChar')
            fldChar1.set(qn('w:fldCharType'), 'begin')
            run._r.append(fldChar1)
            instrText = OxmlElement('w:instrText')
            instrText.set('xml:space', 'preserve')
            instrText.text = ' PAGE '
            run._r.append(instrText)
            fldChar2 = OxmlElement('w:fldChar')
            fldChar2.set(qn('w:fldCharType'), 'separate')
            run._r.append(fldChar2)
            fldChar3 = OxmlElement('w:fldChar')
            fldChar3.set(qn('w:fldCharType'), 'end')
            run._r.append(fldChar3)
```

> 注：如果章节没有自然分 section，则需要在合并时手动创建 section break 来划分封面/摘要/正文三个区域。

### Step 1.5: 插入目录

⚠️ **必须执行**：在摘要之后、第一章之前插入自动目录。

```python
def insert_toc(merged_doc, language):
    """在摘要后插入目录页"""

    # 找到第一章的位置
    chapter1_pos = None
    for i, para in enumerate(merged_doc.paragraphs):
        text = para.text.strip()
        if text.startswith('一、') or text.startswith('第一章') or '引言' in text:
            chapter1_pos = i
            break

    if chapter1_pos is None:
        return  # 找不到则跳过

    # 使用 OxmlElement 在第一章前插入：
    # 1. 分页符
    # 2. "目  录" 标题（居中，黑体16pt）
    # 3. TOC 域代码（TOC \o "1-2" \h \z \u）
    # 4. 占位文字："请在 Word 中按 Ctrl+A, F9 更新域以生成目录"
    # 5. 分页符

    # 目录标题
    toc_heading = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'center')
    pPr.append(jc)
    toc_heading.append(pPr)
    run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    b = OxmlElement('w:b')
    rPr.append(b)
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), '黑体')
    rPr.append(rFonts)
    run.append(rPr)
    t = OxmlElement('w:t')
    t.text = '目  录'
    run.append(t)
    toc_heading.append(run)

    # TOC 域
    toc_field = create_toc_field_element()

    # 分页符
    pb1 = create_page_break_element()
    pb2 = create_page_break_element()

    # 按顺序插入
    body = merged_doc.element.body
    body.insert(chapter1_pos, pb2)       # 目录后分页
    body.insert(chapter1_pos, toc_field) # TOC 域
    body.insert(chapter1_pos, toc_heading)# 目录标题
    body.insert(chapter1_pos, pb1)       # 目录前分页

def create_toc_field_element():
    """创建 TOC 域 XML 元素"""
    p = OxmlElement('w:p')
    # begin
    r1 = OxmlElement('w:r')
    fc1 = OxmlElement('w:fldChar')
    fc1.set(qn('w:fldCharType'), 'begin')
    r1.append(fc1)
    p.append(r1)
    # instrText
    r2 = OxmlElement('w:r')
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = ' TOC \\o "1-2" \\h \\z \\u '
    r2.append(it)
    p.append(r2)
    # separate
    r3 = OxmlElement('w:r')
    fc2 = OxmlElement('w:fldChar')
    fc2.set(qn('w:fldCharType'), 'separate')
    r3.append(fc2)
    p.append(r3)
    # placeholder
    r4 = OxmlElement('w:r')
    t4 = OxmlElement('w:t')
    t4.text = '请在 Word 中按 Ctrl+A, F9 更新域以生成目录'
    r4.append(t4)
    p.append(r4)
    # end
    r5 = OxmlElement('w:r')
    fc3 = OxmlElement('w:fldChar')
    fc3.set(qn('w:fldCharType'), 'end')
    r5.append(fc3)
    p.append(r5)
    return p

def create_page_break_element():
    """创建分页符 XML 元素"""
    p = OxmlElement('w:p')
    r = OxmlElement('w:r')
    br = OxmlElement('w:br')
    br.set(qn('w:type'), 'page')
    r.append(br)
    p.append(r)
    return p
```

### Step 2: 学术润色

使用 `nature-polishing` skill：

```python
def polish_paper(merged_doc, language, polishing_level="academic"):
    """学术润色"""

    result = call_skill("nature-polishing", {
        "document": merged_doc,
        "language": language,
        "level": polishing_level,
        "checks": [
            "grammar",           # 语法检查
            "spelling",          # 拼写检查
            "academic_tone",     # 学术语气
            "sentence_structure",# 句式结构
            "word_choice",       # 用词准确性
            "coherence",         # 连贯性
            "citation_format",   # 引用格式
            "punctuation"        # 标点符号
        ]
    })

    return result
```

### Step 3: 格式规范检查

```python
def check_format_consistency(doc, language):
    """检查格式规范一致性"""

    issues = []

    # 字体检查
    expected_font = "宋体" if language == "中文" else "Times New Roman"
    for para in doc.paragraphs:
        for run in para.runs:
            if run.font.name != expected_font:
                issues.append({
                    "type": "font",
                    "location": para.text[:50],
                    "expected": expected_font,
                    "actual": run.font.name
                })

    # 字号检查
    for para in doc.paragraphs:
        if para.style.name.startswith("Heading"):
            expected_size = get_heading_size(para.style.name)
            for run in para.runs:
                if run.font.size != expected_size:
                    issues.append({
                        "type": "font_size",
                        "location": para.text[:50],
                        "expected": expected_size,
                        "actual": run.font.size
                    })

    # 行距检查
    for para in doc.paragraphs:
        if para.paragraph_format.line_spacing != 1.5:
            issues.append({
                "type": "line_spacing",
                "location": para.text[:50],
                "expected": 1.5,
                "actual": para.paragraph_format.line_spacing
            })

    # 图表编号格式检查（必须为 [图X-Y] 或 [表X-Y] 格式）
    fig_pattern = r'\[图\d+-\d+\]'
    table_pattern = r'\[表\d+-\d+\]'
    if not re.search(fig_pattern, doc.text):
        issues.append({
            "type": "figure_numbering",
            "suggestion": "未找到 [图X-Y] 格式的图表编号，请确认图表已插入且编号格式正确"
        })

    # 页边距检查
    for section in doc.sections:
        margins = {
            "top": section.top_margin,
            "bottom": section.bottom_margin,
            "left": section.left_margin,
            "right": section.right_margin
        }
        # 标准页边距：2.54cm
        standard = Cm(2.54)
        for side, margin in margins.items():
            if abs(margin - standard) > Cm(0.1):
                issues.append({
                    "type": "margin",
                    "side": side,
                    "expected": "2.54cm",
                    "actual": f"{margin.cm:.2f}cm"
                })

    return issues
```

### Step 4: 引用格式检查

```python
def check_citation_format(doc, language):
    """检查引用格式一致性（序号式引用）"""

    issues = []

    # 序号式引用格式：[1]、[2,3]、[1-5] 等上标形式
    pattern = r'\[(\d+(?:[,，\s]*\d+)*(?:\s*[-–—]\s*\d+)?)\]'

    citations = re.findall(pattern, doc.text)

    # 提取所有引用编号
    citation_numbers = set()
    for cite_str in citations:
        # 解析如 "1,3,5-7" 这样的引用
        parts = re.split(r'[,，\s]+', cite_str)
        for part in parts:
            if '-' in part or '–' in part or '—' in part:
                # 处理范围引用如 "5-7"
                range_match = re.match(r'(\d+)\s*[-–—]\s*(\d+)', part)
                if range_match:
                    start, end = int(range_match.group(1)), int(range_match.group(2))
                    for n in range(start, end + 1):
                        citation_numbers.add(n)
            else:
                try:
                    citation_numbers.add(int(part))
                except ValueError:
                    pass

    # 检查引用编号是否连续（从1开始，无跳号）
    if citation_numbers:
        max_ref = max(citation_numbers)
        expected = set(range(1, max_ref + 1))
        missing = expected - citation_numbers
        if missing:
            issues.append({
                "type": "non_sequential",
                "missing_numbers": sorted(missing),
                "suggestion": "引用编号不连续，请检查是否有遗漏"
            })

    # 检查是否有旧格式残留（Author, Year 或 [Author, Year]）
    old_pattern_en = r'\(([A-Z][a-z]+(?:\s+et\s+al\.)?),?\s*(\d{4})\)'
    old_pattern_cn = r'\[([A-Z][a-z]+(?:\s+et\s+al\.)?),?\s*(\d{4})\]'
    old_citations_en = re.findall(old_pattern_en, doc.text)
    old_citations_cn = re.findall(old_pattern_cn, doc.text)
    if old_citations_en or old_citations_cn:
        issues.append({
            "type": "old_format_detected",
            "count": len(old_citations_en) + len(old_citations_cn),
            "suggestion": "检测到旧的 (Author, Year) 格式引用，应改为序号式 [N]"
        })

    return issues
```

### Step 4.5: 验证并修复引用上标

⚠️ **必须执行**：检查所有正文引用 [N] 是否为上标格式，参考文献列表的 [N] 是否为正常格式。

```python
def fix_citation_superscript(doc):
    """修复引用上标：正文引用必须上标，参考文献编号不能上标"""
    import re, copy

    CITE_PATTERN = r'(\[\d+(?:[,，\s]*\d+)*(?:\s*[-–—]\s*\d+)*\])'

    # 找到参考文献章节的起始位置
    ref_start = None
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip() in ('参考文献', 'References'):
            ref_start = i + 1
            break

    # 修复正文引用上标
    fixed_count = 0
    for i, para in enumerate(doc.paragraphs):
        if ref_start and i >= ref_start:
            break  # 跳过参考文献部分

        text = para.text
        if not re.search(CITE_PATTERN, text):
            continue

        p_elem = para._p
        for r_elem in list(p_elem.findall(qn('w:r'))):
            run_text = ''.join(t.text or '' for t in r_elem.findall(qn('w:t')))
            if not run_text or not re.search(CITE_PATTERN, run_text):
                continue

            # 检查是否已上标
            rPr = r_elem.find(qn('w:rPr'))
            if rPr is not None:
                va = rPr.find(qn('w:vertAlign'))
                if va is not None and va.get(qn('w:val')) == 'superscript':
                    continue  # 已上标，跳过

            # 拆分 run：引用部分上标，正文部分正常
            parts = re.split(CITE_PATTERN, run_text)
            if len(parts) <= 1:
                continue

            # 保存原始格式
            rPr_copy = copy.deepcopy(rPr) if rPr is not None else OxmlElement('w:rPr')

            parent = p_elem
            idx = list(parent).index(r_elem)
            parent.remove(r_elem)

            insert_idx = idx
            for part in parts:
                if not part:
                    continue
                new_r = OxmlElement('w:r')
                new_rPr = copy.deepcopy(rPr_copy)
                if re.match(CITE_PATTERN, part):
                    va = OxmlElement('w:vertAlign')
                    va.set(qn('w:val'), 'superscript')
                    new_rPr.append(va)
                new_r.append(new_rPr)
                t = OxmlElement('w:t')
                t.set(qn('xml:space'), 'preserve')
                t.text = part
                new_r.append(t)
                parent.insert(insert_idx, new_r)
                insert_idx += 1
            fixed_count += 1

    # 修复参考文献列表：确保 [N] 不是上标
    if ref_start:
        for i in range(ref_start, len(doc.paragraphs)):
            para = doc.paragraphs[i]
            if re.match(r'^\[\d+\]', para.text.strip()):
                for run in para.runs:
                    if run.font.superscript and re.match(r'^\[\d+\]', run.text):
                        run.font.superscript = False

    return fixed_count

def verify_images_embedded(doc):
    """验证所有图片是否正确嵌入（有实际的 image part）"""

    image_parts = [r for r in doc.part.rels.values() if 'image' in r.reltype]
    inline_shapes = len(doc.inline_shapes)

    issues = []
    if inline_shapes == 0:
        issues.append("文档中没有嵌入任何图片")
    if len(image_parts) == 0 and inline_shapes > 0:
        issues.append(f"有 {inline_shapes} 个 drawing 引用但无实际图片数据，图片将无法显示")

    # 检查每个 figures/ 目录下的图片是否都被嵌入
    return {
        "inline_shapes": inline_shapes,
        "image_parts": len(image_parts),
        "issues": issues,
        "ok": len(image_parts) > 0 and len(image_parts) == inline_shapes
    }
```

### Step 5: 生成润色报告

```markdown
# 润色报告

## 润色概况
- 润色日期：2026-05-11
- 论文语言：[中文/英文]
- 总字数：[字数]
- 章节数：[数量]

## 语言润色

### 语法修正 (12处)
| 位置 | 原文 | 修改 | 原因 |
|------|------|------|------|
| 第2章第3段 | ... | ... | 主谓不一致 |

### 用词改进 (8处)
| 位置 | 原词 | 建议 | 原因 |
|------|------|------|------|
| 第3章第1段 | show | demonstrate | 更学术 |

### 句式优化 (5处)
| 位置 | 原句式 | 优化 | 原因 |
|------|--------|------|------|
| 第4章第2段 | 短句并列 | 复合句 | 增强连贯性 |

## 格式检查

### 通过项
- [x] 字体一致
- [x] 字号规范
- [x] 行距正确
- [x] 页边距标准
- [x] 图表编号连续

### 问题项 (3处)
| 问题 | 位置 | 建议 |
|------|------|------|
| 字体不一致 | 第5章表格 | 统一为宋体/Times New Roman |

## 引用检查

### 通过项
- [x] 引用格式为序号式 [N]
- [x] 引用编号连续无跳号
- [x] 引用编号与参考文献列表对应
- [x] 文末包含完整参考文献列表

### 问题项 (2处)
| 引用 | 问题 | 建议 |
|------|------|------|
| [15] | 参考文献列表中未找到对应条目 | 添加或修正 |
| 第3章 | 检测到旧格式 (Author, 2024) | 改为 [N] 序号格式 |

## 润色前后对比

### 可读性提升
- 润色前：Flesch Reading Ease = 35
- 润色后：Flesch Reading Ease = 45

### 学术性提升
- 学术词汇使用：+15%
- 被动语态比例：60% → 55%（更自然）

## 总结
本次润色共修改 [X] 处，主要改进：
1. 语法和拼写修正
2. 学术用词规范化
3. 句式结构优化
4. 格式一致性修正
5. 引用格式统一
```

## 关键约束
- **只返回文件路径**
- **无上下文**：每次调用都是全新实例
- **保留原意**：润色不改变论文内容和论点
- **语言匹配**：严格按照 requirements.md 的语言润色
- **学术规范**：遵循学术写作规范

## 质量检查清单
- [ ] 所有章节已合并
- [ ] 章节标题样式均为 Heading 1（非 Normal）
- [ ] 每个章节标题前有分页符
- [ ] 页码已插入（封面无页码，摘要目录罗马数字，正文阿拉伯数字）
- [ ] 目录已插入（摘要后、正文前）
- [ ] 图片已正确嵌入（inline_shapes 数量 == image_parts 数量 > 0）
- [ ] 图表编号格式为 [图X-Y] / [表X-Y]
- [ ] 正文引用 [N] 全部为上标格式（superscript=True）
- [ ] 参考文献列表的 [N] 全部为正常格式（非上标）
- [ ] 语法错误已修正
- [ ] 拼写错误已修正
- [ ] 学术用词规范
- [ ] 句式结构优化
- [ ] 格式一致
- [ ] 引用规范
- [ ] 润色报告完整
- [ ] 已用 Word (win32com) 更新域代码并导出 PDF

### Step 6: 用 Word COM 插入分节符、页码并生成 PDF

⚠️ **必须执行**（仅 Windows）：python-docx 的分节符在 Word 中会丢失（3节变1节），域代码也不会自动渲染。必须用 win32com 完成：分节符插入 → 页码添加 → 域更新 → PDF导出。

⚠️ **中文路径问题**：Word COM 无法处理中文路径文件，必须先复制到临时英文路径，操作完再复制回来。

```python
def insert_section_breaks_and_page_numbers(docx_path, pdf_path):
    """用 Word COM 插入分节符、页码、更新域代码、导出 PDF"""
    import win32com.client, shutil, tempfile, os, time, subprocess

    # 复制到临时英文路径（COM 不支持中文路径）
    tmp_dir = tempfile.mkdtemp()
    tmp_docx = os.path.join(tmp_dir, "paper.docx")
    shutil.copy2(docx_path, tmp_docx)

    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False

    try:
        doc = word.Documents.Open(tmp_docx)
        wdSectionBreakNextPage = 2
        wdHeaderFooterPrimary = 1
        wdAlignParagraphCenter = 2
        wdFieldPage = 33

        # ===== Step 1: 插入分节符 =====
        # 在"目录"标题前插入分节符（封面 / 目录分界）
        for i in range(1, doc.Paragraphs.Count + 1):
            text = doc.Paragraphs(i).Range.Text.strip()
            if text in ('目  录', '目录'):
                doc.Paragraphs(i).Range.InsertBreak(wdSectionBreakNextPage)
                break

        # 在"第一章"前插入分节符（目录 / 正文分界）
        for i in range(1, doc.Paragraphs.Count + 1):
            text = doc.Paragraphs(i).Range.Text.strip()
            if text.startswith('第一章') or text.startswith('第1章'):
                doc.Paragraphs(i).Range.InsertBreak(wdSectionBreakNextPage)
                break

        # ===== Step 2: 为每节添加页码 =====
        for i in range(1, doc.Sections.Count + 1):
            section = doc.Sections(i)
            footer = section.Footers(wdHeaderFooterPrimary)
            footer.LinkToPrevious = False

            if i == 1:
                # 封面：无页码
                footer.Range.Text = ""
            else:
                # 目录和正文：插入 PAGE 域
                footer.Range.Text = ""
                rng = footer.Range
                rng.Collapse(0)  # wdCollapseStart
                doc.Fields.Add(rng, wdFieldPage)
                footer.Range.ParagraphFormat.Alignment = wdAlignParagraphCenter

        # ===== Step 3: 更新所有域代码 =====
        for story_range in doc.StoryRanges:
            story_range.Fields.Update()
            while story_range.NextStoryRange is not None:
                story_range = story_range.NextStoryRange
                story_range.Fields.Update()

        for toc in doc.TablesOfContents:
            toc.Update()

        # ===== Step 4: 保存并导出 PDF =====
        doc.Save()
        tmp_pdf = os.path.join(tmp_dir, "paper.pdf")
        doc.SaveAs2(tmp_pdf, FileFormat=17)  # 17 = wdFormatPDF
        doc.Close()

    finally:
        try:
            word.Quit()
        except:
            pass
        time.sleep(3)
        subprocess.run(["taskkill", "/f", "/im", "WINWORD.EXE"], capture_output=True)
        time.sleep(1)
        # 复制回原路径
        try:
            shutil.copy2(tmp_docx, docx_path)
            shutil.copy2(tmp_pdf, pdf_path)
        except Exception as e:
            print(f"Copy error: {e}")
        shutil.rmtree(tmp_dir, ignore_errors=True)
```

**调用时机**：在所有格式修复（引用上标、图片嵌入、标题样式、分页符）完成之后，作为最后一步执行。此函数同时完成分节符插入、页码添加、域更新和PDF导出。

**关键教训**：
- python-docx 的 `section.start_type` 和页脚域代码在 Word 中会丢失，不能依赖
- 必须用 Word COM 的 `InsertBreak(wdSectionBreakNextPage)` 创建分节符
- 必须用 `doc.Fields.Add(rng, wdFieldPage)` 在页脚中插入 PAGE 域
- `field.NumberFormat` 和 `section.PageNumbers` 属性不可用，不要尝试设置
- 中文路径必须通过临时英文路径中转
