"""
build_results.py — 结果账本构建入口

扫描项目中的求解输出文件，生成 artifacts/results_master.json。
如果没有求解输出，生成空白模板并标记 status: "incomplete"。

用法：
    # 在项目根目录运行
    python assets/components/build_results.py --project-root .

    # 指定输出路径
    python assets/components/build_results.py --project-root . --output artifacts/results_master.json

    # 扫描已有求解输出
    python assets/components/build_results.py --project-root . --scan
"""

import argparse
import json
import os
import sys
from datetime import datetime


# 结果账本 schema（空白模板）
BLANK_TEMPLATE = {
    "status": "incomplete",
    "built_at": "",
    "paper_meta": {
        "title": "",
        "problem_type": "math_modeling",
        "target_dates_problem3": []
    },
    "method_config": {
        "train_test_split": None,
        "cv_folds": None,
        "confidence_level": None,
        "significance_level": None,
        "cost_ratio": None,
        "waste_penalty": None
    },
    "problem1": {
        "data_summary": {},
        "cleaning_summary": {},
        "dish_clusters": []
    },
    "problem2": {
        "selection_rule": "rmse_min",
        "best_model": "",
        "metrics": {},
        "forecast_table": ""
    },
    "problem3": {
        "input_source": "problem2.forecast_table",
        "date_scope": "workdays_only",
        "optimization_result_table": "",
        "profit_summary": {}
    },
    "problem4": {
        "nutrition_min_ratio": 0.8,
        "package_results": {}
    },
    "derived_claims": [],
    "summary_claims": [],
    "data_requests": [],
    "artifact_requests": []
}


def scan_solver_outputs(project_root: str) -> dict:
    """扫描项目中的求解输出文件，尝试提取关键数字。

    扫描策略：
    1. 查找 code/ 目录下的 .py 脚本输出
    2. 查找 output/ 或 results/ 目录下的 CSV/JSON
    3. 查找 artifacts/ 下已有的部分结果

    注意：此函数只做文件发现和基础解析，不伪造任何数字。
    """
    merged = {}
    artifacts_dir = os.path.join(project_root, "artifacts")
    code_dir = os.path.join(project_root, "code")
    output_dir = os.path.join(project_root, "output")
    results_dir = os.path.join(project_root, "results")

    # 扫描 artifacts/ 下已有的 results_master.json（部分填充的）
    existing_path = os.path.join(artifacts_dir, "results_master.json")
    if os.path.exists(existing_path):
        with open(existing_path, "r", encoding="utf-8") as f:
            merged = json.load(f)

    # 扫描 artifacts/tables/ 下的 CSV 文件
    tables_dir = os.path.join(artifacts_dir, "tables")
    if os.path.isdir(tables_dir):
        csv_files = [f for f in os.listdir(tables_dir) if f.endswith(".csv")]
        for csv_file in csv_files:
            # 尝试根据文件名推断归属
            _attach_csv_reference(merged, csv_file, f"artifacts/tables/{csv_file}")

    return merged


def _attach_csv_reference(data: dict, filename: str, path: str):
    """根据 CSV 文件名推断其在 results_master 中的位置"""
    name_lower = filename.lower()
    p2 = data.setdefault("problem2", {})
    p3 = data.setdefault("problem3", {})

    if "forecast" in name_lower:
        p2["forecast_table"] = path
    elif "metric" in name_lower or "model" in name_lower:
        p2.setdefault("_csv_files", []).append(path)
    elif "optim" in name_lower or "profit" in name_lower:
        p3["optimization_result_table"] = path
    elif "package" in name_lower or "nutrition" in name_lower:
        p4 = data.setdefault("problem4", {})
        p4.setdefault("_csv_files", []).append(path)


def build_results(project_root: str, output_path: str, scan: bool = False) -> str:
    """构建 results_master.json

    Args:
        project_root: 项目根目录
        output_path: 输出文件路径
        scan: 是否扫描已有求解输出

    Returns:
        输出文件的绝对路径
    """
    if scan:
        data = scan_solver_outputs(project_root)
    else:
        data = BLANK_TEMPLATE.copy()

    data["built_at"] = datetime.now().isoformat()
    if "status" not in data:
        data["status"] = "incomplete"

    # 确保输出目录存在
    abs_output = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(abs_output), exist_ok=True)

    with open(abs_output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return abs_output


def main():
    parser = argparse.ArgumentParser(description="结果账本构建工具")
    parser.add_argument("--project-root", default=".", help="项目根目录（默认当前目录）")
    parser.add_argument("--output", default=None, help="输出路径（默认 artifacts/results_master.json）")
    parser.add_argument("--scan", action="store_true", help="扫描已有求解输出并合并")
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    output_path = args.output or os.path.join(project_root, "artifacts", "results_master.json")

    result_path = build_results(project_root, output_path, scan=args.scan)

    # 验证输出
    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    status = data.get("status", "unknown")
    print(f"结果账本已生成: {result_path}")
    print(f"状态: {status}")

    if status == "incomplete":
        print("注意: 结果账本为空白模板，需填充求解结果后才能通过一致性检查。")
        print("请运行求解代码后重新执行 build_results.py --scan，或手动编辑 results_master.json。")

    return result_path


if __name__ == "__main__":
    main()
