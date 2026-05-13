"""
论文章节合并脚本模板
用于论文工作流阶段6，正确合并多个 chapter_N.docx 文件，保留所有内联图片

⚠️ 关键原理：
- python-docx 自动命名图片为 image1.png, image2.png
- 每个 chapter_N.docx 独立生成，都从1开始计数
- 直接合并会导致图片覆盖，必须重命名为唯一名称

使用方法：
    from merge_docx_chapters import merge_chapters
    chapter_files = [f'chapters/chapter_{i}.docx' for i in range(1, 8)]
    merge_chapters(chapter_files, 'output.docx', base_dir='.')
"""

import zipfile
import os
from lxml import etree
from copy import deepcopy


def merge_chapters(chapter_files, output_path, base_dir='.'):
    """
    合并多个章节 docx 文件，保留所有内联图片

    Args:
        chapter_files: 章节文件路径列表
        output_path: 输出文件路径
        base_dir: 基础目录（用于构建相对路径）
    """

    # 命名空间
    NS_W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'

    all_media = {}  # zip路径 -> 二进制数据
    all_paragraphs = []  # 段落XML元素列表
    rels_entries = []  # 新的关系条目

    # ========== 第一步：逐个处理章节 ==========
    for chapter_idx, chapter_file in enumerate(chapter_files):
        if not os.path.exists(chapter_file):
            print(f'警告：跳过不存在的文件 {chapter_file}')
            continue

        chapter_num = chapter_idx + 1
        print(f'处理 chapter_{chapter_num}.docx...')

        with zipfile.ZipFile(chapter_file, 'r') as zf:
            # --- 1.1 提取图片，重命名为唯一名称 ---
            media_mapping = {}  # 原始zip路径 -> 新文件名
            for name in zf.namelist():
                if name.startswith('word/media/'):
                    old_basename = os.path.basename(name)
                    ext = os.path.splitext(old_basename)[1]
                    new_basename = f'ch{chapter_num}_{old_basename}'
                    media_mapping[name] = new_basename
                    all_media[f'word/media/{new_basename}'] = zf.read(name)

            # --- 1.2 提取关系文件，建立 rId 映射 ---
            rels_xml = zf.read('word/_rels/document.xml.rels')
            rels_tree = etree.fromstring(rels_xml)
            rid_mapping = {}  # 旧rId -> 新rId

            for rel in rels_tree:
                old_rid = rel.get('Id')
                target = rel.get('Target')
                if target and target.startswith('media/'):
                    old_media_zip_path = f'word/{target}'
                    if old_media_zip_path in media_mapping:
                        new_rid = f'ch{chapter_num}_{old_rid}'
                        new_target = f'media/{media_mapping[old_media_zip_path]}'
                        rid_mapping[old_rid] = new_rid
                        rels_entries.append({
                            'Id': new_rid,
                            'Type': rel.get('Type'),
                            'Target': new_target
                        })

            # --- 1.3 提取段落，更新图片引用 ---
            doc_xml = zf.read('word/document.xml')
            doc_tree = etree.fromstring(doc_xml)
            body = doc_tree.find(f'.//{{{NS_W}}}body')

            for child in body:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if tag in ('p', 'tbl'):  # 段落或表格
                    element_copy = deepcopy(child)

                    # 更新 blip 引用（图片）
                    for blip in element_copy.iter(f'{{{NS_A}}}blip'):
                        old_embed = blip.get(f'{{{NS_R}}}embed')
                        if old_embed and old_embed in rid_mapping:
                            blip.set(f'{{{NS_R}}}embed', rid_mapping[old_embed])

                    all_paragraphs.append(element_copy)

    # ========== 第二步：组装新文档 ==========
    print('组装新文档...')

    # 以第一个章节为模板
    template_file = chapter_files[0]

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as out_zf:
        # --- 2.1 复制模板中的非文档、非媒体文件 ---
        with zipfile.ZipFile(template_file, 'r') as template_zf:
            for name in template_zf.namelist():
                if name == 'word/document.xml':
                    # 构建新的 document.xml
                    template_doc = etree.fromstring(template_zf.read(name))
                    body = template_doc.find(f'.//{{{NS_W}}}body')

                    # 清空body（保留 sectPr）
                    sect_pr = body.find(f'{{{NS_W}}}sectPr')
                    for child in list(body):
                        if child != sect_pr:
                            body.remove(child)

                    # 添加所有段落
                    for para in all_paragraphs:
                        body.append(para)

                    # 重新添加 sectPr
                    if sect_pr is not None:
                        body.append(sect_pr)

                    out_zf.writestr(name, etree.tostring(
                        template_doc,
                        xml_declaration=True,
                        encoding='UTF-8',
                        standalone=True
                    ))

                elif name == 'word/_rels/document.xml.rels':
                    # 合并关系文件
                    template_rels = etree.fromstring(template_zf.read(name))

                    # 添加新的图片关系
                    for entry in rels_entries:
                        new_rel = etree.SubElement(template_rels, 'Relationship')
                        new_rel.set('Id', entry['Id'])
                        new_rel.set('Type', entry['Type'])
                        new_rel.set('Target', entry['Target'])

                    out_zf.writestr(name, etree.tostring(
                        template_rels,
                        xml_declaration=True,
                        encoding='UTF-8',
                        standalone=True
                    ))

                elif name.startswith('word/media/'):
                    # 跳过原始媒体文件（后面统一写入）
                    continue

                else:
                    # 其他文件直接复制
                    out_zf.writestr(name, template_zf.read(name))

        # --- 2.2 写入所有媒体文件 ---
        for name, data in all_media.items():
            out_zf.writestr(name, data)

    # ========== 第三步：修复 Content_Types.xml ==========
    _fix_content_types(output_path)

    print(f'合并完成: {output_path}')


def _fix_content_types(docx_path):
    """确保 Content_Types.xml 包含 PNG 类型声明"""
    import shutil
    import tempfile

    temp_path = docx_path + '.tmp'

    with zipfile.ZipFile(docx_path, 'r') as zin:
        ct_xml = zin.read('[Content_Types].xml')
        ct_tree = etree.fromstring(ct_xml)

        # 检查是否已有 PNG 默认类型
        has_png = False
        for elem in ct_tree:
            if elem.get('Extension') == 'png':
                has_png = True
                break

        if not has_png:
            # 添加 PNG 默认类型
            ns = 'http://schemas.openxmlformats.org/package/2006/content-types'
            default = etree.SubElement(ct_tree, f'{{{ns}}}Default')
            default.set('Extension', 'png')
            default.set('ContentType', 'image/png')

        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                if item == '[Content_Types].xml':
                    zout.writestr(item, etree.tostring(
                        ct_tree,
                        xml_declaration=True,
                        encoding='UTF-8',
                        standalone=True
                    ))
                else:
                    zout.writestr(item, zin.read(item))

    shutil.move(temp_path, docx_path)


def verify_merged_docx(docx_path):
    """验证合并后的文档"""
    import hashlib

    with zipfile.ZipFile(docx_path, 'r') as zf:
        # 统计图片
        media_files = []
        for name in zf.namelist():
            if name.startswith('word/media/'):
                data = zf.read(name)
                md5 = hashlib.md5(data).hexdigest()[:8]
                media_files.append((name, len(data), md5))

        print(f'\n=== 合并文档验证 ===')
        print(f'图片总数: {len(media_files)}')

        unique_md5 = set(md5 for _, _, md5 in media_files)
        print(f'唯一图片数: {len(unique_md5)}')

        if len(media_files) != len(unique_md5):
            print('⚠️ 警告：存在重复图片！')
        else:
            print('✓ 所有图片都是唯一的')

        # 检查关系文件
        rels_xml = zf.read('word/_rels/document.xml.rels')
        rels_tree = etree.fromstring(rels_xml)

        img_rels = []
        for rel in rels_tree:
            if 'image' in rel.get('Type', ''):
                img_rels.append((rel.get('Id'), rel.get('Target')))

        print(f'图片关系数: {len(img_rels)}')

        # 检查 document.xml 中的 blip 引用
        doc_xml = zf.read('word/document.xml')
        doc_tree = etree.fromstring(doc_xml)

        blip_rids = []
        for blip in doc_tree.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
            rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            if rid:
                blip_rids.append(rid)

        print(f'文档中图片引用数: {len(blip_rids)}')

        # 验证所有引用都有对应的关系
        rel_ids = set(rid for rid, _ in img_rels)
        missing = [rid for rid in blip_rids if rid not in rel_ids]
        if missing:
            print(f'⚠️ 警告：以下引用缺少关系: {missing}')
        else:
            print('✓ 所有图片引用都有对应的关系')


# ========== 使用示例 ==========
if __name__ == '__main__':
    base_dir = r'C:\Users\lost\Desktop\1'
    chapter_files = [os.path.join(base_dir, 'chapters', f'chapter_{i}.docx') for i in range(1, 8)]
    output_path = os.path.join(base_dir, 'merged_paper.docx')

    merge_chapters(chapter_files, output_path, base_dir)
    verify_merged_docx(output_path)
