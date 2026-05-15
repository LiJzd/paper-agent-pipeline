"""
generate_tables.py — 从 results_master.json 生成规范表格 CSV

读取 results_master.json 中的数据，按 artifact_manifest.json 的登记信息，
生成 artifacts/tables/*.csv。禁止手工编造数值。

用法：
    python generate_tables.py --project-root .
    python generate_tables.py --manifest artifacts/artifact_manifest.json --results artifacts/results_master.json
"""

import argparse
import csv
import json
import os
import sys


def generate_tables(manifest_path: str, results_path: str, project_root: str = ".") -> dict:
    """根据 manifest 和 results_master 生成所有表格 CSV"""
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    generated = []
    errors = []

    for table in manifest.get("tables", []):
        tid = table.get("table_id", "unknown")
        path = table.get("path", "")
        source_keys = table.get("source_keys", [])

        if not path:
            errors.append({"type": "no_path", "table_id": tid, "message": "表格没有指定 path"})
            continue

        abs_path = os.path.join(project_root, path) if not os.path.isabs(path) else path
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        try:
            data = _extract_table_data(results, source_keys, table)
            _write_csv(abs_path, data)
            generated.append({"table_id": tid, "path": path, "rows": len(data.get("rows", []))})
        except Exception as e:
            errors.append({"type": "generation_error", "table_id": tid, "message": str(e)})

    # 自动登记生成的文件到 manifest
    try:
        from artifact_manifest import ArtifactManifest
        manifest_obj = ArtifactManifest(manifest_path)
        for g in generated:
            manifest_obj.update_table_entry(
                g["table_id"],
                path=g["path"],
                generated_by="generate_tables.py"
            )
    except Exception:
        pass

    return {"generated": generated, "errors": errors}


def _extract_table_data(results: dict, source_keys: list, table_def: dict) -> dict:
    """从 results_master 中提取表格数据"""
    columns = table_def.get("columns", [])
    if not columns:
        # 自动推断列名
        columns = ["指标", "值"]

    rows = []
    for sk in source_keys:
        val = _deep_get(results, sk)
        if val is not None:
            # 尝试拆分 key 路径作为行标签
            parts = sk.split(".")
            label = parts[-1] if parts else sk
            if isinstance(val, dict):
                for k, v in val.items():
                    rows.append([k, str(v)])
            elif isinstance(val, list):
                for i, v in enumerate(val):
                    rows.append([str(i), str(v)])
            else:
                rows.append([label, str(val)])
        else:
            rows.append([sk, ""])

    return {"columns": columns[:2] if len(columns) > 2 else columns, "rows": rows}


def _write_csv(path: str, data: dict):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data.get("columns", []))
        for row in data.get("rows", []):
            writer.writerow(row)


def _deep_get(data: dict, dotpath: str):
    parts = dotpath.split(".")
    current = data
    for p in parts:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            return None
    return current


def main():
    parser = argparse.ArgumentParser(description="从 results_master 生成规范表格")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--results", default=None)
    args = parser.parse_args()

    root = os.path.abspath(args.project_root)
    manifest = args.manifest or os.path.join(root, "artifacts", "artifact_manifest.json")
    results = args.results or os.path.join(root, "artifacts", "results_master.json")

    report = generate_tables(manifest, results, root)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
