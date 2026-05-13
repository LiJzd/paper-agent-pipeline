"""
论文交付工具集
从交付智能体中提取的打包和检查函数。

使用方法：
    import sys, os
    sys.path.insert(0, os.path.expanduser('~/.claude/agents/assets/components'))
    from paper_delivery_utils import (
        create_delivery_package, generate_reference_list,
        generate_pdf, organize_supplementary,
    )
"""

import re
import os
import shutil
import glob
from datetime import datetime


def generate_reference_list(paper_text, bib_refs, output_path):
    """从论文正文中提取引用编号，生成按序号排列的参考文献列表。

    Args:
        paper_text: 论文正文全文（字符串）
        bib_refs: BibTeX 解析后的参考文献列表 [{key, authors, title, ...}]
        output_path: 输出 markdown 文件路径

    Returns:
        str: 输出文件路径
    """
    pattern = r'\[(\d+(?:[,，\s]*\d+)*(?:\s*[-–—]\s*\d+)?)]'
    citations = re.findall(pattern, paper_text)

    cited_numbers = set()
    for cite_str in citations:
        parts = re.split(r'[,，\s]+', cite_str)
        for part in parts:
            if '-' in part or '–' in part or '—' in part:
                range_match = re.match(r'(\d+)\s*[-–—]\s*(\d+)', part)
                if range_match:
                    start, end = int(range_match.group(1)), int(range_match.group(2))
                    cited_numbers.update(range(start, end + 1))
            else:
                try:
                    cited_numbers.add(int(part))
                except ValueError:
                    pass

    sorted_refs = sorted(cited_numbers)
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('# 参考文献 / References\n\n')
        for num in sorted_refs:
            ref = _find_ref_by_number(bib_refs, num)
            if ref:
                entry = f"[{num}] {ref['authors']}. {ref['title']}[{ref.get('type', 'J')}]. {ref.get('journal', '')}, {ref.get('year', '')}"
                if ref.get('volume'):
                    entry += f", {ref['volume']}"
                if ref.get('pages'):
                    entry += f": {ref['pages']}"
                entry += ".\n\n"
                f.write(entry)

    return output_path


def _find_ref_by_number(bib_refs, number):
    """在参考文献列表中按编号查找。"""
    for ref in bib_refs:
        if ref.get('number') == number:
            return ref
    return None


def generate_pdf(docx_path, pdf_path=None):
    """将 Word 文档转换为 PDF。

    优先使用 LibreOffice，其次使用 docx2pdf。

    Args:
        docx_path: 输入 docx 路径
        pdf_path: 输出 pdf 路径（默认同名 .pdf）

    Returns:
        str: PDF 文件路径
    """
    import subprocess

    if pdf_path is None:
        pdf_path = docx_path.replace('.docx', '.pdf')

    # 方法1: LibreOffice
    try:
        result = subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'pdf',
             docx_path, '--outdir', os.path.dirname(docx_path) or '.'],
            capture_output=True, timeout=60
        )
        if result.returncode == 0 and os.path.exists(pdf_path):
            return pdf_path
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 方法2: docx2pdf
    try:
        from docx2pdf import convert
        convert(docx_path, pdf_path)
        return pdf_path
    except ImportError:
        pass

    print('警告：无法生成 PDF，请安装 LibreOffice 或 docx2pdf')
    return None


def organize_supplementary(figures_dir=None, data_dir=None, code_dir=None):
    """整理补充材料文件列表。

    Returns:
        dict: {figures: [...], data: [...], code: [...]}
    """
    supplementary = {'figures': [], 'data': [], 'code': []}

    if figures_dir and os.path.exists(figures_dir):
        supplementary['figures'] = sorted(glob.glob(os.path.join(figures_dir, '**', '*.png'), recursive=True))

    if data_dir and os.path.exists(data_dir):
        supplementary['data'] = sorted(glob.glob(os.path.join(data_dir, '**', '*'), recursive=True))

    if code_dir and os.path.exists(code_dir):
        supplementary['code'] = sorted(glob.glob(os.path.join(code_dir, '**', '*'), recursive=True))

    return supplementary


def create_delivery_package(paper_path, topic, figures_dir=None, ppt_path=None,
                            review_path=None, bib_path=None, bib_refs=None,
                            base_dir='.'):
    """创建论文交付目录。

    Args:
        paper_path: polished_paper.docx 路径
        topic: 论文主题（用于目录名）
        figures_dir: 图表目录
        ppt_path: PPT 路径（可选）
        review_path: 审稿回复路径（可选）
        bib_path: BibTeX 路径（可选）
        bib_refs: 已解析的参考文献列表（可选）
        base_dir: 基础目录

    Returns:
        str: 交付目录路径
    """
    date_str = datetime.now().strftime('%Y%m%d')
    safe_topic = re.sub(r'[^\w一-鿿]', '_', topic)[:30]
    delivery_dir = os.path.join(base_dir, f'Paper_Delivery_{date_str}_{safe_topic}')

    # 创建目录结构
    os.makedirs(os.path.join(delivery_dir, 'supplementary', 'figures'), exist_ok=True)
    os.makedirs(os.path.join(delivery_dir, 'supplementary', 'data'), exist_ok=True)
    os.makedirs(os.path.join(delivery_dir, 'supplementary', 'code'), exist_ok=True)

    # 复制论文
    if os.path.exists(paper_path):
        shutil.copy2(paper_path, os.path.join(delivery_dir, 'paper.docx'))

    # 生成 PDF
    pdf_path = generate_pdf(paper_path, os.path.join(delivery_dir, 'paper.pdf'))

    # 复制 PPT
    if ppt_path and os.path.exists(ppt_path):
        shutil.copy2(ppt_path, os.path.join(delivery_dir, 'presentation.pptx'))

    # 复制图表
    if figures_dir and os.path.exists(figures_dir):
        for fig in glob.glob(os.path.join(figures_dir, '**', '*.png'), recursive=True):
            shutil.copy2(fig, os.path.join(delivery_dir, 'supplementary', 'figures'))

    # 复制审稿回复
    if review_path and os.path.exists(review_path):
        shutil.copy2(review_path, os.path.join(delivery_dir, 'review_response.md'))

    # 复制 BibTeX
    if bib_path and os.path.exists(bib_path):
        shutil.copy2(bib_path, os.path.join(delivery_dir, 'references.bib'))

    # 生成参考文献列表
    if bib_refs and os.path.exists(paper_path):
        from docx import Document
        doc = Document(paper_path)
        generate_reference_list(
            doc.text, bib_refs,
            os.path.join(delivery_dir, 'references_list.md')
        )

    # 生成 README
    _generate_readme(delivery_dir, topic)

    return delivery_dir


def _generate_readme(delivery_dir, topic):
    """生成交付说明 README。"""
    readme = f"""# 交付说明

## 论文信息
- 主题：{topic}
- 交付日期：{datetime.now().strftime('%Y-%m-%d')}

## 文件清单

| 文件 | 说明 |
|------|------|
| paper.docx | 论文 Word 版本 |
| paper.pdf | 论文 PDF 版本 |
| presentation.pptx | 演示PPT（如有） |
| review_response.md | 审稿回复（如有） |
| references.bib | BibTeX 引用文件 |
| references_list.md | 按编号排列的参考文献列表 |
| supplementary/figures/ | 图表文件 |
| supplementary/data/ | 数据文件 |
| supplementary/code/ | 代码文件 |

## 使用说明
1. paper.docx 可直接用于投稿
2. paper.pdf 用于预览和存档
3. presentation.pptx 用于学术报告
"""
    with open(os.path.join(delivery_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme)
