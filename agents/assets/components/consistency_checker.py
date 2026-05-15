"""
consistency_checker.py — 跨章节数据一致性检查器

读取 results_master.json，按规则验证数据一致性。
输出结构化报告供 consistency_auditor agent 使用。

用法：
    # 指定文件路径
    python consistency_checker.py --results artifacts/results_master.json

    # 指定项目根目录（自动查找 artifacts/results_master.json）
    python consistency_checker.py --project-root .

    # 作为模块导入
    from consistency_checker import check_consistency
    report = check_consistency("artifacts/results_master.json")
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any


def check_consistency(json_path: str = "artifacts/results_master.json") -> dict:
    """执行所有一致性检查，返回结构化报告"""
    if not os.path.exists(json_path):
        return {
            "status": "failed",
            "errors": [{"type": "file_missing", "location": json_path,
                        "claim": "结果账本文件不存在", "expected": "文件存在", "source": "filesystem"}],
            "warnings": []
        }

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    errors = []
    warnings = []

    _check_best_model_consistency(data, errors)
    _check_date_scope(data, errors)
    _check上下游_data_source(data, errors)
    _check_nutrition_constraints(data, errors)
    _check_summary_claims_v2(data, errors, warnings)
    _check_method_config(data, warnings)
    _check_derived_claims(data, errors, warnings)

    return {
        "status": "failed" if errors else "passed",
        "errors": errors,
        "warnings": warnings
    }


def _deep_get(data: dict, dotpath: str) -> Any:
    """按点分路径获取嵌套值"""
    parts = dotpath.split(".")
    current = data
    for p in parts:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            return None
    return current


def _check_best_model_consistency(data: dict, errors: list):
    """规则1：最优模型选择一致性"""
    p2 = data.get("problem2", {})
    selection_rule = p2.get("selection_rule", "")
    best_model = p2.get("best_model", "")
    metrics = p2.get("metrics", {})

    if not selection_rule or not best_model or not metrics:
        return

    if selection_rule == "rmse_min":
        min_rmse = None
        min_model = None
        for model_name, model_metrics in metrics.items():
            rmse = model_metrics.get("rmse")
            if rmse is not None:
                if min_rmse is None or rmse < min_rmse:
                    min_rmse = rmse
                    min_model = model_name
        if min_model and min_model != best_model:
            errors.append({
                "type": "best_model_inconsistent",
                "location": "problem2",
                "claim": f"selection_rule='rmse_min'，但 best_model='{best_model}' 不是 RMSE 最小的模型",
                "expected": f"best_model 应为 '{min_model}'（RMSE={min_rmse}）",
                "source": "problem2.metrics.*.rmse"
            })

    elif selection_rule == "r2_max":
        max_r2 = None
        max_model = None
        for model_name, model_metrics in metrics.items():
            r2 = model_metrics.get("r2")
            if r2 is not None:
                if max_r2 is None or r2 > max_r2:
                    max_r2 = r2
                    max_model = model_name
        if max_model and max_model != best_model:
            errors.append({
                "type": "best_model_inconsistent",
                "location": "problem2",
                "claim": f"selection_rule='r2_max'，但 best_model='{best_model}' 不是 R² 最大的模型",
                "expected": f"best_model 应为 '{max_model}'（R²={max_r2}）",
                "source": "problem2.metrics.*.r2"
            })


def _check_date_scope(data: dict, errors: list):
    """规则2：问题三日期范围一致性"""
    p3 = data.get("problem3", {})
    date_scope = p3.get("date_scope", "")
    target_dates = p3.get("target_dates_problem3", [])

    if date_scope == "workdays_only" and target_dates:
        weekend_dates = []
        for d in target_dates:
            try:
                dt = datetime.strptime(d, "%Y-%m-%d")
                if dt.weekday() >= 5:
                    weekend_dates.append(d)
            except (ValueError, TypeError):
                pass
        if weekend_dates:
            errors.append({
                "type": "date_scope_violation",
                "location": "problem3.target_dates_problem3",
                "claim": f"date_scope='workdays_only'，但 target_dates 包含非工作日: {weekend_dates}",
                "expected": "target_dates 不应包含周六或周日",
                "source": "problem3.target_dates_problem3"
            })


def _check上下游_data_source(data: dict, errors: list):
    """规则3：上下游数据来源一致性"""
    p3 = data.get("problem3", {})
    input_source = p3.get("input_source", "")

    if not input_source:
        return

    val = _deep_get(data, input_source)
    if val is None:
        if not input_source.endswith(".csv") and not input_source.endswith(".json"):
            errors.append({
                "type": "data_source_missing",
                "location": "problem3.input_source",
                "claim": f"input_source='{input_source}' 在 results_master.json 中不存在",
                "expected": f"'{input_source}' 应指向 problem2.forecast_table 或已存在的字段",
                "source": "problem3.input_source"
            })


def _check_nutrition_constraints(data: dict, errors: list):
    """规则4：套餐营养约束一致性"""
    p4 = data.get("problem4", {})
    min_ratio = p4.get("nutrition_min_ratio")
    package_results = p4.get("package_results", {})

    if min_ratio is None or not package_results:
        return

    if isinstance(package_results, dict):
        for pkg_name, pkg_data in package_results.items():
            if not isinstance(pkg_data, dict):
                continue
            nutrition = pkg_data.get("nutrition_compliance", pkg_data.get("nutrition", {}))
            if not isinstance(nutrition, dict):
                continue
            for nutrient, ratio in nutrition.items():
                if isinstance(ratio, (int, float)) and ratio < min_ratio:
                    errors.append({
                        "type": "nutrition_constraint_violation",
                        "location": f"problem4.package_results.{pkg_name}.{nutrient}",
                        "claim": f"套餐 '{pkg_name}' 的 {nutrient} 达标率 {ratio} < {min_ratio}",
                        "expected": f"所有营养指标达标率 >= {min_ratio}",
                        "source": f"problem4.package_results.{pkg_name}"
                    })


def _check_summary_claims_v2(data: dict, errors: list, warnings: list):
    """规则5：摘要证据包验证（v2 灵活 schema）

    检查逻辑：
    - source_keys 必须全部存在于 results_master.json
    - numbers[].source_key 必须存在
    - allowed_strength 必须是 weak/moderate/strong
    - claim_type 必须是预定义类型
    - claim_type 特定约束（model_selection 必须有模型选择来源等）
    - 不检查句子是否一致，不检查措辞
    """
    claims = data.get("summary_claims", [])

    if not claims:
        warnings.append({
            "type": "no_summary_claims",
            "location": "summary_claims",
            "message": "summary_claims 为空，摘要编写时需补充证据包"
        })
        return

    valid_strengths = {"weak", "moderate", "strong"}
    valid_types = {"model_selection", "forecast_result", "optimization_result",
                   "package_result", "operation_suggestion"}

    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append({
                "type": "claim_format_error",
                "location": "summary_claims[{}]".format(i),
                "claim": "证据包格式错误",
                "expected": "dict with claim_id, claim_type, scope, conclusion, source_keys, numbers, allowed_strength",
                "source": "summary_claims"
            })
            continue

        claim_id = claim.get("claim_id", "unknown_{}".format(i))
        claim_type = claim.get("claim_type", "")
        scope = claim.get("scope", [])
        conclusion = claim.get("conclusion", "")
        source_keys = claim.get("source_keys", [])
        numbers = claim.get("numbers", [])
        allowed_strength = claim.get("allowed_strength", "")

        loc = "summary_claims[{}]".format(claim_id)

        # 检查 claim_type
        if claim_type not in valid_types:
            errors.append({
                "type": "claim_invalid_type",
                "location": loc,
                "claim": "claim_type='{}' 不是有效类型".format(claim_type),
                "expected": "有效类型: {}".format(", ".join(sorted(valid_types))),
                "source": loc
            })

        # 检查 allowed_strength
        if allowed_strength not in valid_strengths:
            errors.append({
                "type": "claim_invalid_strength",
                "location": loc,
                "claim": "allowed_strength='{}' 不是有效值".format(allowed_strength),
                "expected": "有效值: weak, moderate, strong",
                "source": loc
            })

        # 检查 scope 是否包含 abstract（warning，不阻断）
        if "abstract" not in scope:
            warnings.append({
                "type": "claim_not_in_abstract_scope",
                "location": loc,
                "message": "结论 '{}' 的 scope={} 不含 abstract，摘要中不应引用此结论".format(claim_id, scope)
            })

        # 检查 source_keys 是否全部存在
        for j, sk in enumerate(source_keys):
            if not sk:
                errors.append({
                    "type": "claim_empty_source_key",
                    "location": "{}.source_keys[{}]".format(loc, j),
                    "claim": "结论 '{}' 的 source_keys[{}] 为空字符串".format(claim_id, j),
                    "expected": "每个 source_key 必须指向 results_master 中的字段",
                    "source": loc
                })
                continue
            if _deep_get(data, sk) is None:
                errors.append({
                    "type": "claim_source_not_found",
                    "location": "{}.source_keys[{}]".format(loc, j),
                    "claim": "source_key='{}' 在 results_master.json 中不存在".format(sk),
                    "expected": "'{}' 应指向已有字段".format(sk),
                    "source": loc
                })

        # 检查 numbers 中每个数字
        for j, num_entry in enumerate(numbers):
            if not isinstance(num_entry, dict):
                errors.append({
                    "type": "claim_number_format_error",
                    "location": "{}.numbers[{}]".format(loc, j),
                    "claim": "数字条目格式错误: {}".format(num_entry),
                    "expected": "dict with name, value, unit, source_key",
                    "source": loc
                })
                continue

            num_sk = num_entry.get("source_key", "")
            if not num_sk:
                errors.append({
                    "type": "claim_number_missing_source",
                    "location": "{}.numbers[{}]".format(loc, j),
                    "claim": "数字 '{}' 缺少 source_key".format(num_entry.get("name", "unnamed")),
                    "expected": "每个数字必须有 source_key",
                    "source": loc
                })
                continue

            if _deep_get(data, num_sk) is None:
                errors.append({
                    "type": "claim_number_source_not_found",
                    "location": "{}.numbers[{}]".format(loc, j),
                    "claim": "数字 source_key='{}' 在 results_master.json 中不存在".format(num_sk),
                    "expected": "'{}' 应指向已有字段".format(num_sk),
                    "source": loc
                })

        # claim_type 特定约束
        if claim_type == "model_selection":
            _check_model_selection_claim(claim, data, loc, errors)
        elif claim_type == "optimization_result":
            _check_optimization_claim(claim, data, loc, errors)
        elif claim_type == "package_result":
            _check_package_claim(claim, data, loc, errors)


def _check_model_selection_claim(claim: dict, data: dict, loc: str, errors: list):
    """model_selection 类型必须有指向 best_model 或 metrics 的 source_key"""
    source_keys = claim.get("source_keys", [])
    has_model_ref = any(
        "best_model" in sk or "metrics" in sk or "selection" in sk
        for sk in source_keys
    )
    if not has_model_ref and source_keys:
        errors.append({
            "type": "claim_type_source_mismatch",
            "location": loc,
            "claim": "claim_type='model_selection' 但 source_keys 中没有模型相关字段",
            "expected": "source_keys 应包含 best_model 或 metrics.* 相关路径",
            "source": loc
        })


def _check_optimization_claim(claim: dict, data: dict, loc: str, errors: list):
    """optimization_result 类型必须有指向 profit 相关字段的 source_key"""
    source_keys = claim.get("source_keys", [])
    has_profit_ref = any(
        "profit" in sk or "improvement" in sk or "optimization" in sk
        for sk in source_keys
    )
    if not has_profit_ref and source_keys:
        errors.append({
            "type": "claim_type_source_mismatch",
            "location": loc,
            "claim": "claim_type='optimization_result' 但 source_keys 中没有利润/优化相关字段",
            "expected": "source_keys 应包含 profit_summary 或 optimization 相关路径",
            "source": loc
        })


def _check_package_claim(claim: dict, data: dict, loc: str, errors: list):
    """package_result 类型必须有指向 nutrition 相关字段的 source_key"""
    source_keys = claim.get("source_keys", [])
    has_nutrition_ref = any(
        "nutrition" in sk or "package" in sk or "compliance" in sk
        for sk in source_keys
    )
    if not has_nutrition_ref and source_keys:
        errors.append({
            "type": "claim_type_source_mismatch",
            "location": loc,
            "claim": "claim_type='package_result' 但 source_keys 中没有营养/套餐相关字段",
            "expected": "source_keys 应包含 nutrition 或 package 相关路径",
            "source": loc
        })


def _check_method_config(data: dict, warnings: list):
    """规则6：method_config 字段类型检查（warning 级别）"""
    mc = data.get("method_config")
    if not mc or not isinstance(mc, dict):
        return

    numeric_fields = {
        "train_test_split": (0.5, 0.95, "训练集比例"),
        "cv_folds": (2, 20, "交叉验证折数"),
        "confidence_level": (0.8, 0.999, "置信水平"),
        "significance_level": (0.001, 0.2, "显著性水平"),
        "cost_ratio": (0.1, 100, "成本系数比"),
        "waste_penalty": (0.1, 100, "浪费惩罚系数"),
    }
    for field, (lo, hi, desc) in numeric_fields.items():
        val = mc.get(field)
        if val is None:
            continue
        if not isinstance(val, (int, float)):
            warnings.append({
                "type": "method_config_type_error",
                "location": "method_config.{}".format(field),
                "message": "method_config.{} 应为数值，当前值: {}".format(field, val),
            })
        elif not (lo <= val <= hi):
            warnings.append({
                "type": "method_config_range_warning",
                "location": "method_config.{}".format(field),
                "message": "method_config.{} ({}) 超出常见范围 [{}, {}] ({})".format(
                    field, val, lo, hi, desc),
            })


def _check_derived_claims(data: dict, errors: list, warnings: list):
    """规则7：derived_claims 格式验证"""
    claims = data.get("derived_claims", [])
    if not claims:
        return

    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append({
                "type": "derived_claim_format_error",
                "location": "derived_claims[{}]".format(i),
                "claim": "derived_claims[{}] 格式错误，应为 dict".format(i),
                "expected": "dict with claim_id, from_source_keys, conclusion, supporting_numbers",
                "source": "derived_claims"
            })
            continue

        claim_id = claim.get("claim_id", "unknown_{}".format(i))
        loc = "derived_claims[{}]".format(claim_id)

        # 检查 from_source_keys
        from_keys = claim.get("from_source_keys", [])
        for j, sk in enumerate(from_keys):
            if _deep_get(data, sk) is None:
                warnings.append({
                    "type": "derived_claim_source_not_found",
                    "location": "{}.from_source_keys[{}]".format(loc, j),
                    "message": "source_key='{}' 在 results_master.json 中不存在".format(sk),
                })

        # 检查 supporting_numbers
        for j, num in enumerate(claim.get("supporting_numbers", [])):
            if not isinstance(num, dict):
                errors.append({
                    "type": "derived_claim_number_format",
                    "location": "{}.supporting_numbers[{}]".format(loc, j),
                    "claim": "数字条目格式错误",
                    "expected": "dict with name, value, source_key",
                    "source": loc
                })
                continue
            num_sk = num.get("source_key", "")
            if num_sk and _deep_get(data, num_sk) is None:
                warnings.append({
                    "type": "derived_claim_number_source_missing",
                    "location": "{}.supporting_numbers[{}]".format(loc, j),
                    "message": "source_key='{}' 在 results_master.json 中不存在".format(num_sk),
                })


def _resolve_path(project_root: str, relative_path: str) -> str:
    """将相对路径解析为基于 project_root 的绝对路径"""
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.join(project_root, relative_path)


def main():
    parser = argparse.ArgumentParser(description="跨章节数据一致性检查器")
    parser.add_argument("--project-root", default=".", help="项目根目录（默认当前目录）")
    parser.add_argument("--results", default=None, help="results_master.json 的路径（覆盖 --project-root）")
    args = parser.parse_args()

    if args.results:
        json_path = args.results
    else:
        json_path = os.path.join(args.project_root, "artifacts", "results_master.json")

    report = check_consistency(json_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
