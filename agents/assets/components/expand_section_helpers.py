# -*- coding: utf-8 -*-
"""
扩写辅助工具
为 evidence_based_expander 提供辅助函数
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple


class ExpansionLogger:
    """扩写日志记录器"""

    def __init__(self, chapter_id: str, output_dir: str):
        self.chapter_id = chapter_id
        self.output_dir = output_dir
        self.used_source_keys = []
        self.data_requests = []
        self.artifact_requests = []
        self.expansion_actions = []
        self.warnings = []

    def add_used_source_key(self, key: str, context: str = ""):
        """记录使用的 source_key"""
        self.used_source_keys.append({
            "key": key,
            "context": context,
        })

    def add_data_request(self, field: str, reason: str, suggested_source: str):
        """记录缺失的数字"""
        self.data_requests.append({
            "field": field,
            "reason": reason,
            "suggested_source": suggested_source,
        })

    def add_artifact_request(self, artifact_type: str, description: str, suggested_data_source: str):
        """记录缺失的图表"""
        self.artifact_requests.append({
            "type": artifact_type,
            "description": description,
            "suggested_data_source": suggested_data_source,
        })

    def add_expansion_action(self, section: str, action: str):
        """记录扩写动作"""
        self.expansion_actions.append({
            "section": section,
            "action": action,
        })

    def add_warning(self, message: str):
        """记录警告"""
        self.warnings.append(message)

    def save(self):
        """保存扩写日志"""
        log_path = os.path.join(self.output_dir, f"{self.chapter_id}_expansion_log.md")
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"# {self.chapter_id} Expansion Log\n\n")

            f.write("## Used Source Keys\n")
            if self.used_source_keys:
                for item in self.used_source_keys:
                    f.write(f"- `{item['key']}`: {item['context']}\n")
            else:
                f.write("- None\n")
            f.write("\n")

            f.write("## DATA_REQUEST\n")
            if self.data_requests:
                for req in self.data_requests:
                    f.write(f"- `{req['field']}` | {req['reason']} | Source: {req['suggested_source']}\n")
            else:
                f.write("- None\n")
            f.write("\n")

            f.write("## ARTIFACT_REQUEST\n")
            if self.artifact_requests:
                for req in self.artifact_requests:
                    f.write(f"- {req['type']}: {req['description']} | Data: {req['suggested_data_source']}\n")
            else:
                f.write("- None\n")
            f.write("\n")

            f.write("## Expansion Actions\n")
            if self.expansion_actions:
                for i, action in enumerate(self.expansion_actions, 1):
                    f.write(f"{i}. {action['section']}: {action['action']}\n")
            else:
                f.write("- None\n")
            f.write("\n")

            if self.warnings:
                f.write("## Warnings\n")
                for w in self.warnings:
                    f.write(f"- {w}\n")

        return log_path


class SourceKeyValidator:
    """Source Key 验证器"""

    def __init__(self, results_master_path: str):
        with open(results_master_path, 'r', encoding='utf-8') as f:
            self.results = json.load(f)
        self._flatten_cache = None

    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """将嵌套字典展平为 dot-path 形式"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                items.append((new_key, v))
            else:
                items.append((new_key, v))
        return dict(items)

    def get_flat_keys(self) -> dict:
        """获取展平后的所有键值对"""
        if self._flatten_cache is None:
            self._flatten_cache = self._flatten_dict(self.results)
        return self._flatten_cache

    def validate_key(self, key: str) -> bool:
        """验证 key 是否存在"""
        flat = self.get_flat_keys()
        return key in flat

    def get_value(self, key: str, default=None):
        """获取 key 对应的值"""
        flat = self.get_flat_keys()
        return flat.get(key, default)

    def find_similar_keys(self, key: str, max_results: int = 5) -> List[str]:
        """查找相似的 key"""
        flat = self.get_flat_keys()
        key_parts = key.lower().split('.')
        similar = []
        for k in flat.keys():
            k_lower = k.lower()
            # 检查是否有共同的部分
            common = sum(1 for part in key_parts if part in k_lower)
            if common > 0:
                similar.append((common, k))
        similar.sort(reverse=True)
        return [k for _, k in similar[:max_results]]


class ClaimValidator:
    """结论验证器"""

    def __init__(self, artifact_manifest_path: str):
        with open(artifact_manifest_path, 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)

    def check_claim_allowed(self, figure_id: str, claim: str) -> bool:
        """检查某个结论是否被允许"""
        figures = self.manifest.get("figures", {})
        if figure_id not in figures:
            return False
        allowed_claims = figures[figure_id].get("allowed_claims", [])
        return claim in allowed_claims

    def get_allowed_claims(self, figure_id: str) -> List[str]:
        """获取某个图表的所有允许结论"""
        figures = self.manifest.get("figures", {})
        if figure_id not in figures:
            return []
        return figures[figure_id].get("allowed_claims", [])


class ExpansionMetrics:
    """扩写度量工具"""

    @staticmethod
    def count_chinese_words(text: str) -> int:
        """统计中文字数"""
        # 中文字符
        chinese_chars = len(re.findall(r'[一-鿿]', text))
        # 英文单词
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return chinese_chars + english_words

    @staticmethod
    def count_sections(text: str) -> int:
        """统计章节数"""
        return len(re.findall(r'^#{1,3}\s', text, re.MULTILINE))

    @staticmethod
    def count_figures(text: str) -> int:
        """统计图表引用数"""
        return len(re.findall(r'图\s*\d+|表\s*\d+|Figure\s*\d+|Table\s*\d+', text))

    @staticmethod
    def count_numbers(text: str) -> int:
        """统计数字数"""
        return len(re.findall(r'\d+\.?\d*', text))


def load_chapter_summary(chapter_dir: str, chapter_id: str) -> Optional[str]:
    """加载章节摘要"""
    summary_path = os.path.join(chapter_dir, f"{chapter_id}_summary.md")
    if os.path.exists(summary_path):
        with open(summary_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def load_chapter_draft(chapter_dir: str, chapter_id: str) -> Optional[str]:
    """加载章节草稿"""
    # 尝试多种格式
    for ext in ['.md', '.txt']:
        draft_path = os.path.join(chapter_dir, f"{chapter_id}{ext}")
        if os.path.exists(draft_path):
            with open(draft_path, 'r', encoding='utf-8') as f:
                return f.read()
    return None


def extract_data_requests(text: str) -> List[Dict]:
    """从文本中提取 DATA_REQUEST"""
    requests = []
    pattern = r'DATA_REQUEST:\s*\[(.*?)\]\s*\|\s*\[(.*?)\]\s*\|\s*\[(.*?)\]'
    for match in re.finditer(pattern, text):
        requests.append({
            "field": match.group(1),
            "reason": match.group(2),
            "suggested_source": match.group(3),
        })
    return requests


def extract_artifact_requests(text: str) -> List[Dict]:
    """从文本中提取 ARTIFACT_REQUEST"""
    requests = []
    pattern = r'ARTIFACT_REQUEST:\s*\[(.*?)\]\s*\|\s*\[(.*?)\]\s*\|\s*\[(.*?)\]'
    for match in re.finditer(pattern, text):
        requests.append({
            "type": match.group(1),
            "description": match.group(2),
            "suggested_data_source": match.group(3),
        })
    return requests


def extract_need_expansion_markers(text: str) -> List[Dict]:
    """从文本中提取 NEED_EXPANSION 标记"""
    markers = []
    pattern = r'NEED_EXPANSION:\s*\[(.*?)\]'
    for match in re.finditer(pattern, text):
        markers.append({
            "section": match.group(1),
            "position": match.start(),
        })
    return markers


if __name__ == "__main__":
    # 测试
    logger = ExpansionLogger("test_chapter", "/tmp")
    logger.add_used_source_key("problem2.metrics.XGBoost.R2", "模型评价")
    logger.add_data_request("problem3.daily_plans", "缺少每日备菜方案", "优化求解器")
    logger.add_expansion_action("5.2.3", "添加 R2 解释段落")
    log_path = logger.save()
    print(f"Log saved to: {log_path}")
