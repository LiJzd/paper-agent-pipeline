"""
Word COM 收尾脚本
用于论文工作流阶段6，完成分节符插入、页码添加、域代码更新。

⚠️ 仅 Windows 可用，需要安装 pywin32 (pip install pywin32)
⚠️ 不能导出 PDF（已移除该功能）

使用方法：
    from word_com_finalize import finalize_docx
    finalize_docx('polished_paper.docx')

原理说明：
    python-docx 的分节符和域代码在 Word 中会丢失（3节变1节），
    必须用 win32com 完成最终处理。
    中文路径无法被 Word COM 直接处理，需通过临时英文路径中转。
"""

import os
import shutil
import tempfile
import time
import subprocess


def finalize_docx(docx_path):
    """
    对论文 docx 进行最终处理：插入分节符、添加页码、更新域代码。

    Args:
        docx_path: 论文 docx 文件路径（会被原地修改）

    Returns:
        dict: 处理结果，包含 sections_count, fields_updated 等信息
    """
    import win32com.client

    if not os.path.exists(docx_path):
        raise FileNotFoundError(f'文件不存在: {docx_path}')

    # 复制到临时英文路径（COM 不支持中文路径）
    tmp_dir = tempfile.mkdtemp()
    tmp_docx = os.path.join(tmp_dir, 'paper.docx')
    shutil.copy2(docx_path, tmp_docx)

    word = None
    result = {'sections': 0, 'fields_updated': False, 'toc_updated': False}

    try:
        word = win32com.client.DispatchEx('Word.Application')
        word.Visible = False

        doc = word.Documents.Open(tmp_docx)

        WD_SECTION_BREAK_NEXT_PAGE = 2
        WD_HEADER_FOOTER_PRIMARY = 1
        WD_ALIGN_PARAGRAPH_CENTER = 2
        WD_FIELD_PAGE = 33

        # ===== Step 1: 插入分节符 =====
        # 在"目录"标题前插入分节符（封面 / 目录分界）
        for i in range(1, doc.Paragraphs.Count + 1):
            text = doc.Paragraphs(i).Range.Text.strip()
            if text in ('目  录', '目录'):
                doc.Paragraphs(i).Range.InsertBreak(WD_SECTION_BREAK_NEXT_PAGE)
                break

        # 在"第一章"前插入分节符（目录 / 正文分界）
        for i in range(1, doc.Paragraphs.Count + 1):
            text = doc.Paragraphs(i).Range.Text.strip()
            if text.startswith('第一章') or text.startswith('第1章'):
                doc.Paragraphs(i).Range.InsertBreak(WD_SECTION_BREAK_NEXT_PAGE)
                break

        # ===== Step 2: 为每节添加页码 =====
        result['sections'] = doc.Sections.Count

        for i in range(1, doc.Sections.Count + 1):
            section = doc.Sections(i)
            footer = section.Footers(WD_HEADER_FOOTER_PRIMARY)
            footer.LinkToPrevious = False

            if i == 1:
                # 封面：无页码
                footer.Range.Text = ''
            else:
                # 目录和正文：插入 PAGE 域
                footer.Range.Text = ''
                rng = footer.Range
                rng.Collapse(0)  # wdCollapseStart
                doc.Fields.Add(rng, WD_FIELD_PAGE)
                footer.Range.ParagraphFormat.Alignment = WD_ALIGN_PARAGRAPH_CENTER

        # ===== Step 3: 更新所有域代码 =====
        for story_range in doc.StoryRanges:
            story_range.Fields.Update()
            result['fields_updated'] = True
            while story_range.NextStoryRange is not None:
                story_range = story_range.NextStoryRange
                story_range.Fields.Update()

        for toc in doc.TablesOfContents:
            toc.Update()
            result['toc_updated'] = True

        # ===== Step 4: 保存 =====
        doc.Save()
        doc.Close()

    finally:
        if word:
            try:
                word.Quit()
            except:
                pass
        # 强制清理 Word 进程
        time.sleep(2)
        subprocess.run(['taskkill', '/f', '/im', 'WINWORD.EXE'],
                       capture_output=True, check=False)
        time.sleep(1)

        # 复制回原路径
        try:
            shutil.copy2(tmp_docx, docx_path)
        except Exception as e:
            print(f'复制回原路径失败: {e}')
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return result


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('用法: python word_com_finalize.py <docx_path>')
        print('示例: python word_com_finalize.py polished_paper.docx')
        sys.exit(1)

    path = sys.argv[1]
    print(f'处理: {path}')
    result = finalize_docx(path)
    print(f'完成: {result["sections"]}节, 域代码已更新')
