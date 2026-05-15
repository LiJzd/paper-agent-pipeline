"""
artifact_checker.py — 图表账本一致性检查器

验证 artifact_manifest.json 中登记的图表/表格：
1. 文件是否存在
2. source_keys 是否存在于 results_master.json
3. figure_data 与 source_table 数据是否一致
4. allowed_claims 中的结论是否与 results_master 一致

用法：
    python artifact_checker.py --project-root .
    python artifact_checker.py --manifest artifacts/artifact_manifest.json --results artifacts/results_master.json
"""

import argparse
import csv
import json
import os
import sys
from typing import Any


def check_artifacts(
    manifest_path: str = "artifacts/artifact_manifest.json",
    results_path: str = "artifacts/results_master.json",
    project_root: str = ".",
) -> dict:
    """执行所有图表账本检查"""
    errors = []
    warnings = []

    # 加载 manifest
    if not os.path.exists(manifest_path):
        return {
            "status": "failed",
            "errors": [{"type": "manifest_missing", "location": manifest_path,
                        "claim": "artifact_manifest.json 不存在", "expected": "文件存在", "source": "filesystem"}],
            "warnings": []
        }

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # 加载 results_master
    results_data = {}
    if os.path.exists(results_path):
        with open(results_path, "r", encoding="utf-8") as f:
            results_data = json.load(f)

    # 规则1-3: 文件存在性
    _check_file_existence(manifest, project_root, errors)

    # 规则6: source_keys 存在性
    _check_source_keys(manifest, results_data, errors)

    # 规则5: figure_data 与 source_table 一致性
    _check_data_consistency(manifest, project_root, errors, warnings)

    # 规则7-8: allowed_claims 验证
    _check_allowed_claims(manifest, results_data, errors)

    return {
        "status": "failed" if errors else "passed",
        "errors": errors,
        "warnings": warnings
    }


def _resolve(project_root: str, path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(project_root, path)


def _check_file_existence(manifest: dict, project_root: str, errors: list):
    """规则1-3: 表格/图片/数据文件是否存在"""
    for table in manifest.get("tables", []):
        tid = table.get("table_id", "unknown")
        path = table.get("path", "")
        if path and not os.path.exists(_resolve(project_root, path)):
            errors.append({
                "type": "table_file_missing",
                "location": "tables.{}".format(tid),
                "claim": "表格文件不存在: {}".format(path),
                "expected": "文件应存在于项目目录中",
                "source": path
            })

    for fig in manifest.get("figures", []):
        fid = fig.get("figure_id", "unknown")
        img_path = fig.get("image_path", "")
        data_path = fig.get("data_path", "")
        src_table = fig.get("source_table", "")

        if img_path and not os.path.exists(_resolve(project_root, img_path)):
            errors.append({
                "type": "figure_image_missing",
                "location": "figures.{}".format(fid),
                "claim": "图片文件不存在: {}".format(img_path),
                "expected": "图片文件应存在于项目目录中",
                "source": img_path
            })

        if data_path and not os.path.exists(_resolve(project_root, data_path)):
            errors.append({
                "type": "figure_data_missing",
                "location": "figures.{}".format(fid),
                "claim": "图表数据文件不存在: {}".format(data_path),
                "expected": "每个图表必须有对应的 figure_data CSV",
                "source": data_path
            })

        if src_table and not os.path.exists(_resolve(project_root, src_table)):
            errors.append({
                "type": "source_table_missing",
                "location": "figures.{}".format(fid),
                "claim": "来源表格不存在: {}".format(src_table),
                "expected": "source_table 应存在于项目目录中",
                "source": src_table
            })


def _check_source_keys(manifest: dict, results_data: dict, errors: list):
    """规则6: source_keys 必须存在于 results_master.json"""
    for table in manifest.get("tables", []):
        tid = table.get("table_id", "unknown")
        for sk in table.get("source_keys", []):
            if not _deep_get(results_data, sk):
                errors.append({
                    "type": "manifest_source_key_missing",
                    "location": "tables.{}".format(tid),
                    "claim": "source_key='{}' 在 results_master.json 中不存在".format(sk),
                    "expected": "'{}' 应指向已有字段".format(sk),
                    "source": "results_master.json"
                })

    for fig in manifest.get("figures", []):
        fid = fig.get("figure_id", "unknown")
        for sk in fig.get("source_keys", []):
            if not _deep_get(results_data, sk):
                errors.append({
                    "type": "manifest_source_key_missing",
                    "location": "figures.{}".format(fid),
                    "claim": "source_key='{}' 在 results_master.json 中不存在".format(sk),
                    "expected": "'{}' 应指向已有字段".format(sk),
                    "source": "results_master.json"
                })

        for ci, claim in enumerate(fig.get("allowed_claims", [])):
            for sk in claim.get("source_keys", []):
                if not _deep_get(results_data, sk):
                    errors.append({
                        "type": "claim_source_key_missing",
                        "location": "figures.{}.allowed_claims[{}]".format(fid, ci),
                        "claim": "allowed_claims source_key='{}' 不存在".format(sk),
                        "expected": "'{}' 应指向已有字段".format(sk),
                        "source": "results_master.json"
                    })


def _check_data_consistency(manifest: dict, project_root: str, errors: list, warnings: list):
    """规则5: figure_data 与 source_table 数据一致性"""
    for fig in manifest.get("figures", []):
        fid = fig.get("figure_id", "unknown")
        data_path = fig.get("data_path", "")
        src_table = fig.get("source_table", "")

        if not data_path or not src_table:
            continue

        data_file = _resolve(project_root, data_path)
        table_file = _resolve(project_root, src_table)

        if not os.path.exists(data_file) or not os.path.exists(table_file):
            continue

        data_cols = _read_csv_columns(data_file)
        table_cols = _read_csv_columns(table_file)

        if data_cols and table_cols:
            # 检查 data_path 的列是否是 source_table 列的子集
            missing = set(data_cols) - set(table_cols)
            if missing:
                warnings.append({
                    "type": "figure_data_column_mismatch",
                    "location": "figures.{}".format(fid),
                    "message": "figure_data 中的列 {} 不在 source_table 中".format(missing),
                })


def _check_allowed_claims(manifest: dict, results_data: dict, errors: list):
    """规则7-8: allowed_claims 与 results_master 一致性"""
    best_model = results_data.get("problem2", {}).get("best_model", "")

    for fig in manifest.get("figures", []):
        fid = fig.get("figure_id", "unknown")
        for ci, claim in enumerate(fig.get("allowed_claims", [])):
            loc = "figures.{}.allowed_claims[{}]".format(fid, ci)
            conclusion = claim.get("conclusion", "")
            source_keys = claim.get("source_keys", [])

            # 验证 source_keys 指向的值存在
            for sk in source_keys:
                val = _deep_get(results_data, sk)
                if val is None:
                    errors.append({
                        "type": "allowed_claim_source_missing",
                        "location": loc,
                        "claim": "allowed_claims source_key='{}' 不存在".format(sk),
                        "expected": "'{}' 应指向已有字段".format(sk),
                        "source": "results_master.json"
                    })

            # 检查模型选择相关结论
            if best_model and "best_model" in " ".join(source_keys):
                # 如果声称某个模型最优，验证是否与 best_model 一致
                claim_model = _deep_get(results_data, " ".join(source_keys).split(".")[-1] if "." in source_keys[0] else source_keys[0])
                # 简单检查：结论中提到的模型名是否与 best_model 一致
                for model_name in ["Prophet", "XGBoost", "LSTM", "GRU", "ARIMA", "SARIMA"]:
                    if model_name in conclusion:
                        if "最优" in conclusion or "最佳" in conclusion or "表现最好" in conclusion:
                            if model_name != best_model:
                                errors.append({
                                    "type": "allowed_claim_model_mismatch",
                                    "location": loc,
                                    "claim": "allowed_claims 声称 '{}' 最优，但 best_model='{}'".format(model_name, best_model),
                                    "expected": "best_model 应为 '{}'".format(best_model),
                                    "source": "problem2.best_model"
                                })


def _deep_get(data: dict, dotpath: str) -> Any:
    parts = dotpath.split(".")
    current = data
    for p in parts:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            return None
    return current


def _read_csv_columns(csv_path: str) -> list:
    """读取 CSV 表头"""
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                return [c.strip() for c in row if c.strip()]
    except Exception:
        pass
    return []


def main():
    parser = argparse.ArgumentParser(description="图表账本一致性检查器")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--results", default=None)
    args = parser.parse_args()

    root = os.path.abspath(args.project_root)
    manifest = args.manifest or os.path.join(root, "artifacts", "artifact_manifest.json")
    results = args.results or os.path.join(root, "artifacts", "results_master.json")

    report = check_artifacts(manifest, results, root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
