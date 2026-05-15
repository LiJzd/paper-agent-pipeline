"""
artifact_manifest.py — 图表账本读取工具

提供对 artifacts/artifact_manifest.json 的读写接口。
每个表格和图像都必须在此文件中登记来源、数据文件和允许结论。

用法：
    from artifact_manifest import ArtifactManifest
    manifest = ArtifactManifest("artifacts/artifact_manifest.json")
    fig = manifest.get_figure("fig2-1")
    table = manifest.get_table("tab2-1")
"""

import json
import os
from typing import Any


class ArtifactManifest:
    """图表账本读取器"""

    def __init__(self, json_path: str = "artifacts/artifact_manifest.json"):
        self.json_path = json_path
        self._data = None

    def _load(self):
        if self._data is None:
            if not os.path.exists(self.json_path):
                raise FileNotFoundError(
                    "图表账本不存在: {}\n请先创建 artifact_manifest.json".format(self.json_path)
                )
            with open(self.json_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        return self._data

    def to_dict(self) -> dict:
        return self._load()

    def get_tables(self) -> list:
        """返回所有已登记的表格"""
        return self._load().get("tables", [])

    def get_figures(self) -> list:
        """返回所有已登记的图表"""
        return self._load().get("figures", [])

    def get_table(self, table_id: str) -> dict:
        """按 ID 获取表格"""
        for t in self.get_tables():
            if t.get("table_id") == table_id:
                return t
        return {}

    def get_figure(self, figure_id: str) -> dict:
        """按 ID 获取图表"""
        for f in self.get_figures():
            if f.get("figure_id") == figure_id:
                return f
        return {}

    def get_figure_by_image(self, image_path: str) -> dict:
        """按图片路径获取图表"""
        for f in self.get_figures():
            if f.get("image_path") == image_path:
                return f
        return {}

    def get_all_source_keys(self) -> set:
        """收集所有已登记的 source_keys"""
        keys = set()
        for t in self.get_tables():
            keys.update(t.get("source_keys", []))
        for f in self.get_figures():
            keys.update(f.get("source_keys", []))
            for claim in f.get("allowed_claims", []):
                keys.update(claim.get("source_keys", []))
        return keys

    def get_all_image_paths(self) -> set:
        """收集所有已登记的图片路径"""
        return {f.get("image_path", "") for f in self.get_figures() if f.get("image_path")}

    def get_all_table_paths(self) -> set:
        """收集所有已登记的表格路径"""
        paths = {t.get("path", "") for t in self.get_tables() if t.get("path")}
        paths.update({f.get("source_table", "") for f in self.get_figures() if f.get("source_table")})
        paths.update({f.get("data_path", "") for f in self.get_figures() if f.get("data_path")})
        return paths

    def get_figure_claims(self, figure_id: str) -> list:
        """获取图表的允许结论"""
        fig = self.get_figure(figure_id)
        return fig.get("allowed_claims", [])

    def update_table_entry(self, table_id: str, **kwargs):
        """添加或更新一个表格条目"""
        data = self._load()
        tables = data.setdefault("tables", [])
        for t in tables:
            if t.get("table_id") == table_id:
                t.update(kwargs)
                self._save(data)
                return
        entry = {"table_id": table_id}
        entry.update(kwargs)
        tables.append(entry)
        self._save(data)

    def update_figure_entry(self, figure_id: str, **kwargs):
        """添加或更新一个图表条目"""
        data = self._load()
        figures = data.setdefault("figures", [])
        for f in figures:
            if f.get("figure_id") == figure_id:
                f.update(kwargs)
                self._save(data)
                return
        entry = {"figure_id": figure_id}
        entry.update(kwargs)
        figures.append(entry)
        self._save(data)

    def _save(self, data: dict):
        os.makedirs(os.path.dirname(self.json_path) or ".", exist_ok=True)
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self._data = data
