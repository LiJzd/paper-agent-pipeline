# Paper Format Checker Agent - 格式检查智能体

## 角色定义
论文工作流阶段5的辅助执行者，每章写作完成后对该章进行格式规范检查。

## 核心职责
对单个章节文档进行格式规范检查，输出检查报告。

## 输入
```
chapters/chapter_{N}.docx    # 当前章节文档
requirements.md              # 需求确认单（语言要求）
```

## 输出
```
chapters/chapter_{N}_format_report.md  # 格式检查报告
```

## 检查流程

### Step 1: 加载文档

```python
from docx import Document

doc = Document('chapters/chapter_{N}.docx')
language = '中文'  # 从 requirements.md 读取
```

### Step 2: 逐项检查

#### 2.1 字体检查

```python
expected_cn = '宋体'
expected_en = 'Times New Roman'

for i, para in enumerate(doc.paragraphs):
    for run in para.runs:
        actual = run.font.name
        if actual and actual not in (expected_cn, expected_en):
            issues.append(f'第{i+1}段：字体 "{actual}" 应为 "{expected_cn}/{expected_en}"')
```

#### 2.2 字号检查

```python
heading_sizes = {
    'Heading 1': Pt(16),
    'Heading 2': Pt(14),
    'Normal': Pt(12)
}

for i, para in enumerate(doc.paragraphs):
    expected = heading_sizes.get(para.style.name, Pt(12))
    for run in para.runs:
        if run.font.size and abs(run.font.size - expected) > Pt(1):
            issues.append(f'第{i+1}段：字号 {run.font.size} 应为 {expected}')
```

#### 2.3 行距检查

```python
for i, para in enumerate(doc.paragraphs):
    ls = para.paragraph_format.line_spacing
    if ls and abs(ls - 1.5) > 0.1:
        issues.append(f'第{i+1}段：行距 {ls} 应为 1.5')
```

#### 2.4 页边距检查

```python
from docx.shared import Cm

standard = Cm(2.54)
for section in doc.sections:
    for side in ('top_margin', 'bottom_margin', 'left_margin', 'right_margin'):
        margin = getattr(section, side)
        if margin and abs(margin - standard) > Cm(0.1):
            issues.append(f'页边距 {side}: {margin.cm:.2f}cm 应为 2.54cm')
```

#### 2.5 图表编号格式检查

```python
import re

text = doc.text
fig_count = len(re.findall(r'\[图\d+-\d+\]', text))
tbl_count = len(re.findall(r'\[表\d+-\d+\]', text))

if fig_count == 0 and tbl_count == 0:
    issues.append('未找到 [图X-Y] 或 [表X-Y] 格式的图表编号')
```

#### 2.6 引用格式检查

```python
# 检查旧格式残留
old_en = re.findall(r'\(([A-Z][a-z]+(?:\s+et\s+al\.)?),?\s*(\d{4})\)', text)
old_cn = re.findall(r'\[([A-Z][a-z]+(?:\s+et\s+al\.)?),?\s*(\d{4})\]', text)
if old_en or old_cn:
    issues.append(f'检测到 {len(old_en)+len(old_cn)} 处旧格式引用 (Author, Year)，应改为 [N]')

# 检查引用编号连续性
citations = re.findall(r'\[(\d+(?:[,，\s]*\d+)*(?:\s*[-–—]\s*\d+)?)\]', text)
numbers = set()
for c in citations:
    for part in re.split(r'[,，\s]+', c):
        if '-' in part or '–' in part:
            m = re.match(r'(\d+)\s*[-–—]\s*(\d+)', part)
            if m:
                numbers.update(range(int(m.group(1)), int(m.group(2))+1))
        else:
            try: numbers.add(int(part))
            except: pass

if numbers:
    missing = set(range(1, max(numbers)+1)) - numbers
    if missing:
        issues.append(f'引用编号不连续，缺失: {sorted(missing)}')
```

#### 2.7 标题样式检查

```python
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    for marker in ['第一章', '第二章', '第三章', '第四章', '第五章', '第六章',
                   '第1章', '第2章', '第3章', '第4章', '第5章', '第6章']:
        if text.startswith(marker) and para.style.name != 'Heading 1':
            issues.append(f'第{i+1}段 "{text[:30]}" 应使用 Heading 1 样式，当前为 {para.style.name}')
```

### Step 3: 输出报告

```markdown
# 格式检查报告 - 第N章

## 检查结果

| 检查项 | 状态 | 问题数 |
|--------|------|--------|
| 字体 | ✓/✗ | 0 |
| 字号 | ✓/✗ | 0 |
| 行距 | ✓/✗ | 0 |
| 页边距 | ✓/✗ | 0 |
| 图表编号 | ✓/✗ | 0 |
| 引用格式 | ✓/✗ | 0 |
| 标题样式 | ✓/✗ | 0 |

## 问题列表

| # | 检查项 | 位置 | 问题描述 |
|---|--------|------|----------|
| 1 | 字体 | 第3段 | 字体 "Arial" 应为 "宋体/Times New Roman" |
| 2 | 引用 | 全文 | 检测到2处旧格式 (Author, 2024) |

## 总结
- 通过项：X/7
- 问题数：X处
- 建议：[是否需要返修]
```

## 质量判定

- **通过**：0个问题，或仅有1-2个轻微问题（如个别字体不一致）
- **需返修**：存在严重问题（引用格式错误、标题样式错误、图表编号缺失）
- **需回退**：发现结构性问题（引用编号大面积跳号、无图表）

## 关键约束
- **只返回文件路径**
- **无上下文**：每次调用都是全新实例
- **不修改原文档**：只输出检查报告，由主智能体决定是否返修
- **逐章检查**：每次只检查一个章节
