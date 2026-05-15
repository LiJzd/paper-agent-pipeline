"""
result_store.py — 结果账本读取工具

提供对 artifacts/results_master.json 的读取接口。
章节写作 agent 必须通过此工具获取关键数字，禁止自行生成。

用法：
    from result_store import ResultStore
    store = ResultStore("artifacts/results_master.json")
    rmse = store.get("problem2.metrics.Prophet.rmse")      # 允许缺失，返回 None
    model = store.require("problem2.best_model")            # 缺失则抛出 ValueError
"""

import json
import os
from typing import Any


class ResultStore:
    """结果账本读取器"""

    def __init__(self, json_path: str = "artifacts/results_master.json"):
        self.json_path = json_path
        self._data = None

    def _load(self):
        if self._data is None:
            if not os.path.exists(self.json_path):
                raise FileNotFoundError(
                    f"结果账本不存在: {self.json_path}\n"
                    f"请先运行 build_results.py 生成 results_master.json"
                )
            with open(self.json_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        return self._data

    def get(self, key: str, default: Any = None) -> Any:
        """按点分路径获取值，不存在返回 default。

        用于非关键字段，允许缺失。
        示例：store.get("problem2.forecast_table")
        """
        data = self._load()
        parts = key.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def require(self, key: str) -> Any:
        """按点分路径获取值，不存在或为空则抛出 ValueError。

        用于关键字段（模型指标、最优模型名、利润数据等），不允许缺失。
        示例：store.require("problem2.best_model")
        """
        val = self.get(key)
        if val is None or val == "":
            available = self.list_keys()
            raise ValueError(
                f"必需字段缺失: {key}\n"
                f"请检查 results_master.json 中是否已填充该字段。\n"
                f"当前可用 key 数量: {len(available)}\n"
                f"部分可用 key: {', '.join(available[:20])}"
            )
        return val

    def list_keys(self, prefix: str = "", data: Any = None) -> list:
        """列出所有叶子节点的点分路径，方便调试。

        示例：store.list_keys("problem2")
        """
        if data is None:
            data = self._load()
        keys = []
        if isinstance(data, dict):
            for k, v in data.items():
                full_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    keys.extend(self.list_keys(full_key, v))
                elif isinstance(v, list):
                    keys.append(full_key)
                else:
                    keys.append(full_key)
        return keys

    def to_dict(self) -> dict:
        """返回完整的结果账本字典"""
        return self._load()

    @property
    def status(self) -> str:
        """返回结果账本状态: complete / incomplete / unknown"""
        return self.get("status", "unknown")


def get(key: str, default: Any = None) -> Any:
    """模块级快捷函数，使用默认路径"""
    store = ResultStore()
    return store.get(key, default)


def require(key: str) -> Any:
    """模块级快捷函数，使用默认路径"""
    store = ResultStore()
    return store.require(key)


def list_keys(prefix: str = "") -> list:
    """模块级快捷函数，使用默认路径"""
    store = ResultStore()
    return store.list_keys(prefix)
