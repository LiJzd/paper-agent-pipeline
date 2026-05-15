"""
run_math_modeling_pipeline.py — 数学建模论文 15 阶段流水线（v2）

阶段顺序：
  1.  problem_parser              [agent]   解析题目
  2.  solution_planner            [agent]   设计求解方案
  3.  result_builder              [agent]   求解并填充 results_master.json
  4.  consistency_checker_prewrite [script]  结果账本内部一致性（pre-write）
  5.  generate_tables             [script]  从 results_master 生成 tables/*.csv
  6.  generate_figures            [script]  从 figure_data 生成 figures/*.png
  7.  artifact_manifest_builder   [script]  扫描 tables/figures → artifact_manifest.json
  8.  artifact_checker_prewrite   [script]  图表账本一致性（pre-write）
  9.  chapter_writer              [agent]   逐章骨架写作（markdown + 占位符）
  10. evidence_based_expander     [agent]   逐章证据扩写（markdown）
  11. abstract_conclusion_writer  [agent]   摘要/结论编写（markdown）
  12. renderer                    [script]  markdown → final.docx（插表插图+目录+页码）
  13. final_document_verifier     [script]  正文与账本一致性
  14. quality_gate_checker        [script]  综合质量门禁
  15. delivery                    [agent]   终审交付

任一 checker status=failed → 立即停止，不得进入下一阶段。

用法：
    python run_math_modeling_pipeline.py --project-root . --dry-run
    python run_math_modeling_pipeline.py --project-root . --from-stage 9
    python run_math_modeling_pipeline.py --project-root . --only check
"""

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ── 颜色输出 ───────────────────────────────────────────────────

def _green(text):
    return "\033[92m{}\033[0m".format(text)

def _yellow(text):
    return "\033[93m{}\033[0m".format(text)

def _red(text):
    return "\033[91m{}\033[0m".format(text)

def _bold(text):
    return "\033[1m{}\033[0m".format(text)

def _dim(text):
    return "\033[2m{}\033[0m".format(text)


# ── 阶段定义 ───────────────────────────────────────────────────

STAGES = {
    1:  {"name": "problem_parser",               "type": "agent",   "desc": "解析题目，生成 problem_spec.json"},
    2:  {"name": "solution_planner",             "type": "agent",   "desc": "读取 problem_spec.json → solution_plan.json"},
    3:  {"name": "result_builder",               "type": "agent",   "desc": "运行求解代码 → 填充 results_master.json + figure_data/"},
    4:  {"name": "consistency_checker_prewrite", "type": "script",  "desc": "结果账本内部一致性检查（pre-write）"},
    5:  {"name": "generate_tables",              "type": "script",  "desc": "从 results_master 生成 tables/*.csv"},
    6:  {"name": "generate_figures",             "type": "script",  "desc": "从 figure_data 生成 figures/*.png"},
    7:  {"name": "artifact_manifest_builder",    "type": "script",  "desc": "扫描 tables/figures → artifact_manifest.json"},
    8:  {"name": "artifact_checker_prewrite",    "type": "script",  "desc": "图表账本一致性检查（pre-write）"},
    9:  {"name": "chapter_writer",               "type": "agent",   "desc": "逐章骨架写作（markdown + {{figure:}}/{{table:}} 占位符）"},
    10: {"name": "evidence_based_expander",      "type": "agent",   "desc": "逐章证据扩写（markdown）"},
    11: {"name": "abstract_conclusion_writer",   "type": "agent",   "desc": "摘要/结论编写（markdown，最后执行，排版在最前）"},
    12: {"name": "renderer",                     "type": "script",  "desc": "markdown → final.docx（解析占位符+插表插图+目录+页码）"},
    13: {"name": "final_document_verifier",      "type": "script",  "desc": "正文与账本一致性验证"},
    14: {"name": "quality_gate_checker",         "type": "script",  "desc": "综合质量门禁"},
    15: {"name": "delivery",                     "type": "agent",   "desc": "终审交付"},
}

# checker 阶段映射
CHECKER_STAGES = {4, 8, 13, 14}

def _print_stage_header(stage_num: int):
    info = STAGES[stage_num]
    tag = "AGENT" if info["type"] == "agent" else "SCRIPT"
    print("\n" + "=" * 70)
    print(_bold("  阶段 {}: {} [{}]".format(stage_num, info["name"], tag)))
    print("  {}".format(info["desc"]))
    print("=" * 70)


# ── 文件依赖声明 ───────────────────────────────────────────────

STAGE_INPUTS = {
    1:  ["题目PDF/文本"],
    2:  ["artifacts/problem_spec.json"],
    3:  ["artifacts/problem_spec.json", "artifacts/solution_plan.json", "原始数据Excel"],
    4:  ["artifacts/results_master.json"],
    5:  ["artifacts/results_master.json", "artifacts/artifact_manifest.json"],
    6:  ["artifacts/artifact_manifest.json", "artifacts/figure_data/*.csv"],
    7:  ["artifacts/tables/*.csv", "artifacts/figures/*.png"],
    8:  ["artifacts/artifact_manifest.json", "artifacts/results_master.json"],
    9:  ["artifacts/results_master.json", "artifacts/artifact_manifest.json",
         "artifacts/tables/*.csv", "artifacts/figures/*.png",
         "chapters/chapter_{N-1}_summary.md (第2章起)"],
    10: ["chapters/chapter_N.md", "artifacts/results_master.json",
         "artifacts/tables/*.csv"],
    11: ["chapters/chapter_N_summary.md (所有章节)", "artifacts/results_master.json"],
    12: ["chapters/*.md (所有章节)", "artifacts/artifact_manifest.json",
         "artifacts/tables/*.csv", "artifacts/figures/*.png"],
    13: ["output/final.docx", "artifacts/results_master.json",
         "artifacts/artifact_manifest.json"],
    14: ["所有checker报告"],
    15: ["output/final.docx", "所有checker报告"],
}

STAGE_OUTPUTS = {
    1:  ["artifacts/problem_spec.json"],
    2:  ["artifacts/solution_plan.json"],
    3:  ["artifacts/results_master.json", "artifacts/figure_data/*.csv"],
    4:  ["artifacts/checker_reports/consistency_prewrite.json"],
    5:  ["artifacts/tables/*.csv"],
    6:  ["artifacts/figures/*.png"],
    7:  ["artifacts/artifact_manifest.json"],
    8:  ["artifacts/checker_reports/artifact_prewrite.json"],
    9:  ["chapters/chapter_N.md", "chapters/chapter_N_summary.md",
         "chapters/chapter_N_requests.md"],
    10: ["chapters/chapter_N_expanded.md", "chapters/chapter_N_expansion_log.md"],
    11: ["chapters/abstract.md"],
    12: ["output/final.docx"],
    13: ["artifacts/checker_reports/document_verifier.json"],
    14: ["artifacts/checker_reports/quality_gate.json"],
    15: ["output/Paper_Delivery/"],
}


# ── Dry-Run 逻辑 ───────────────────────────────────────────────

def _check_file_exists(path_pattern: str, project_root: str) -> bool:
    """检查文件是否存在（支持*通配符）"""
    import glob
    if "*" in path_pattern:
        full = os.path.join(project_root, path_pattern)
        return len(glob.glob(full)) > 0
    else:
        return os.path.exists(os.path.join(project_root, path_pattern))


def _dry_run_stage(stage_num: int, project_root: str) -> dict:
    """dry-run单个阶段，返回状态"""
    info = STAGES[stage_num]
    inputs = STAGE_INPUTS.get(stage_num, [])
    outputs = STAGE_OUTPUTS.get(stage_num, [])

    # 检查输入文件
    input_status = {}
    for inp in inputs:
        if inp.startswith("原始数据") or inp.startswith("题目") or inp.startswith("所有") or inp.startswith("chapters/chapter_{"):
            input_status[inp] = "assumed"  # 不检查
        else:
            exists = _check_file_exists(inp, project_root)
            input_status[inp] = "exists" if exists else "MISSING"

    # 检查输出文件
    output_status = {}
    for out in outputs:
        exists = _check_file_exists(out, project_root)
        output_status[out] = "exists" if exists else "not_generated"

    # 判断是否可执行
    can_run = all(v != "MISSING" for v in input_status.values())
    has_output = any(v == "exists" for v in output_status.values())

    return {
        "stage": stage_num,
        "name": info["name"],
        "type": info["type"],
        "desc": info["desc"],
        "inputs": input_status,
        "outputs": output_status,
        "can_run": can_run,
        "has_output": has_output,
    }


def _run_checker_script(stage_num: int, project_root: str) -> dict:
    """运行checker脚本，返回结果"""
    os.makedirs(os.path.join(project_root, "artifacts", "checker_reports"), exist_ok=True)

    if stage_num == 4:
        # consistency_checker_prewrite
        try:
            from consistency_checker import check_consistency
            json_path = os.path.join(project_root, "artifacts", "results_master.json")
            if not os.path.exists(json_path):
                return {"status": "skipped", "reason": "results_master.json not found"}
            report = check_consistency(json_path)
            report["stage"] = "consistency_checker_prewrite"
            out_path = os.path.join(project_root, "artifacts", "checker_reports", "consistency_prewrite.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return report
        except ImportError:
            return {"status": "error", "reason": "consistency_checker module not found"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    elif stage_num == 8:
        # artifact_checker_prewrite
        try:
            from artifact_checker import check_artifacts
            manifest_path = os.path.join(project_root, "artifacts", "artifact_manifest.json")
            results_path = os.path.join(project_root, "artifacts", "results_master.json")
            if not os.path.exists(manifest_path):
                return {"status": "skipped", "reason": "artifact_manifest.json not found"}
            report = check_artifacts(manifest_path, results_path, project_root)
            report["stage"] = "artifact_checker_prewrite"
            out_path = os.path.join(project_root, "artifacts", "checker_reports", "artifact_prewrite.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return report
        except ImportError:
            return {"status": "error", "reason": "artifact_checker module not found"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    elif stage_num == 13:
        # final_document_verifier
        try:
            from final_document_verifier import verify_document, _find_document
            doc_path = _find_document(project_root)
            if not doc_path:
                return {"status": "skipped", "reason": "final document not found"}
            results_path = os.path.join(project_root, "artifacts", "results_master.json")
            manifest_path = os.path.join(project_root, "artifacts", "artifact_manifest.json")
            report = verify_document(doc_path, results_path, project_root, manifest_path)
            report["stage"] = "final_document_verifier"
            out_path = os.path.join(project_root, "artifacts", "checker_reports", "document_verifier.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return report
        except ImportError:
            return {"status": "error", "reason": "final_document_verifier module not found"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    elif stage_num == 14:
        # quality_gate_checker: 汇总所有checker报告
        reports_dir = os.path.join(project_root, "artifacts", "checker_reports")
        all_reports = {}
        for fname in os.listdir(reports_dir) if os.path.isdir(reports_dir) else []:
            if fname.endswith(".json"):
                with open(os.path.join(reports_dir, fname), "r", encoding="utf-8") as f:
                    all_reports[fname] = json.load(f)

        failed = [k for k, v in all_reports.items() if v.get("status") == "failed"]
        errors = []
        for v in all_reports.values():
            errors.extend(v.get("errors", []))

        gate = {
            "stage": "quality_gate_checker",
            "status": "failed" if failed else "passed",
            "failed_checkers": failed,
            "total_errors": len(errors),
            "reports_loaded": list(all_reports.keys()),
        }
        out_path = os.path.join(project_root, "artifacts", "checker_reports", "quality_gate.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(gate, f, ensure_ascii=False, indent=2)
        return gate

    return {"status": "skipped", "reason": "unknown checker"}


def _validate_results_master(project_root: str) -> dict:
    """验证 results_master.json 是否包含所有必需字段"""
    path = os.path.join(project_root, "artifacts", "results_master.json")
    if not os.path.exists(path):
        return {"status": "failed", "reason": "results_master.json not found", "missing_fields": []}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required_fields = {
        "problem1": {
            "cleaning": ["raw_orders", "duplicate_orders", "matched_order_count",
                         "amount_outlier_orders", "matched_meal_counts"],
            "summary": ["order_count", "dish_types", "avg_daily_orders",
                        "avg_daily_revenue", "lunch_top3", "top20_sales_share",
                        "abc_counts", "association_top5"],
            "cluster_summary": "list",
            "season_daily": "list",
        },
        "problem2": {
            "best_model": "str",
            "model_comparison": "dict",
            "may_predictions": "list",
        },
        "problem3": {
            "meal_plans": "dict",
            "packages": "dict",
        },
    }

    missing = []
    for section, fields in required_fields.items():
        if section not in data:
            missing.append(f"{section} (entire section)")
            continue
        for field, expected_type in fields.items():
            if field not in data[section]:
                missing.append(f"{section}.{field}")
            elif expected_type == "list" and not isinstance(data[section][field], list):
                missing.append(f"{section}.{field} (expected list, got {type(data[section][field]).__name__})")
            elif expected_type == "dict" and not isinstance(data[section][field], dict):
                missing.append(f"{section}.{field} (expected dict, got {type(data[section][field]).__name__})")

    return {
        "status": "passed" if not missing else "failed",
        "missing_fields": missing,
        "total_keys": sum(len(v) if isinstance(v, dict) else 1 for v in data.values()),
    }


# ── Agent 阶段标记 ─────────────────────────────────────────────

def _agent_stage_info(stage_num: int) -> dict:
    """返回agent阶段的信息（不实际执行）"""
    info = STAGES[stage_num]
    return {
        "stage": stage_num,
        "name": info["name"],
        "type": "agent",
        "status": "NOT_IMPLEMENTED",
        "reason": "Agent stages must be dispatched by the orchestrator (main Claude session), "
                  "not by this script. Use Agent() tool to call each stage.",
        "agent_prompt_file": os.path.join("~/.claude/agents", f"paper_math_modeling_{info['name']}.md")
            if stage_num in (1, 2, 3, 9) else
            os.path.join("~/.claude/agents", f"paper_{info['name']}.md")
            if stage_num in (10, 11, 15) else "N/A",
    }


# ── 主入口 ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="数学建模论文 15 阶段流水线（v2）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
阶段说明：
  1-3    求解阶段（agent 执行）
  4,8    pre-write 检查（script 执行）
  5-7    生成阶段（script 执行，tables/figures/manifest）
  9-11   写作阶段（agent 执行，markdown 骨架 → 扩写 → 摘要）
  12     渲染阶段（script 执行，markdown → final.docx）
  13-14  post-render 检查（script 执行）
  15     交付阶段（agent 执行）
        """
    )
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--from-stage", type=int, default=1, help="从指定阶段开始执行 (1-15)")
    parser.add_argument("--to-stage", type=int, default=15, help="执行到指定阶段 (1-15)")
    parser.add_argument("--only", choices=["solve", "generate", "write", "check", "all"],
                        help="只执行指定类别的阶段")
    parser.add_argument("--dry-run", action="store_true", help="只检查依赖和输出，不实际执行")
    parser.add_argument("--skip-check", action="store_true", help="跳过所有 checker（危险）")
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)

    print(_bold("=" * 70))
    print(_bold("  数学建模论文 15 阶段流水线（v2）"))
    print(_bold("=" * 70))
    print("  项目根目录: {}".format(project_root))
    print("  模式: {}".format(_yellow("DRY-RUN") if args.dry_run else _green("EXECUTE")))
    print("  范围: 阶段 {} ~ {}".format(args.from_stage, args.to_stage))
    print()

    results = {}
    stop_on_checker_fail = True

    for stage_num in range(1, 16):
        # 范围过滤
        if stage_num < args.from_stage or stage_num > args.to_stage:
            continue

        # 类别过滤
        if args.only:
            if args.only == "solve" and stage_num not in (1, 2, 3):
                continue
            if args.only == "generate" and stage_num not in (5, 6, 7):
                continue
            if args.only == "write" and stage_num not in (9, 10, 11, 12):
                continue
            if args.only == "check" and stage_num not in (4, 8, 13, 14):
                continue

        info = STAGES[stage_num]
        _print_stage_header(stage_num)

        if args.dry_run:
            # ── Dry-Run 模式 ──
            dr = _dry_run_stage(stage_num, project_root)

            print("  输入文件:")
            for inp, status in dr["inputs"].items():
                icon = {"exists": _green("✓"), "MISSING": _red("✗"), "assumed": _dim("?")}
                print("    {} {}".format(icon.get(status, "?"), inp))

            print("  输出文件:")
            for out, status in dr["outputs"].items():
                icon = {"exists": _green("✓"), "not_generated": _dim("-")}
                print("    {} {}".format(icon.get(status, "-"), out))

            if info["type"] == "agent":
                print("  执行方式: {}".format(_yellow("AGENT（需主智能体调度）")))
            else:
                print("  执行方式: {}".format(_green("SCRIPT（可自动执行）")))

            # checker 特殊处理
            if stage_num in CHECKER_STAGES and not args.skip_check:
                if dr["has_output"]:
                    # 已有报告，读取状态
                    report_files = {
                        4: "consistency_prewrite.json",
                        8: "artifact_prewrite.json",
                        13: "document_verifier.json",
                        14: "quality_gate.json",
                    }
                    rf = report_files.get(stage_num)
                    if rf:
                        rp = os.path.join(project_root, "artifacts", "checker_reports", rf)
                        if os.path.exists(rp):
                            with open(rp, "r", encoding="utf-8") as f:
                                rpt = json.load(f)
                            status = rpt.get("status", "unknown")
                            n_err = len(rpt.get("errors", []))
                            n_warn = len(rpt.get("warnings", []))
                            if status == "passed":
                                print("  检查结果: {}".format(_green("PASSED")))
                            else:
                                print("  检查结果: {}".format(_red("FAILED")))
                            print("    错误: {} | 警告: {}".format(n_err, n_warn))
                            results["stage_{}".format(stage_num)] = rpt
                else:
                    print("  检查结果: {}".format(_dim("未运行（输出文件不存在）")))

            # results_master 字段验证（阶段3之后）
            if stage_num == 3:
                print("\n  results_master.json 字段完整性预检:")
                vr = _validate_results_master(project_root)
                if vr["status"] == "passed":
                    print("    {}".format(_green("所有必需字段已存在")))
                else:
                    print("    {}".format(_red("缺失字段:")))
                    for mf in vr["missing_fields"]:
                        print("      - {}".format(mf))

            results["stage_{}".format(stage_num)] = dr

        else:
            # ── 执行模式 ──
            if info["type"] == "agent":
                # agent 阶段：标记为 NOT_IMPLEMENTED
                agent_info = _agent_stage_info(stage_num)
                print("  {}".format(_yellow("NOT_IMPLEMENTED: Agent阶段需主智能体调度")))
                results["stage_{}".format(stage_num)] = agent_info

            elif stage_num in CHECKER_STAGES:
                # checker 阶段
                if args.skip_check:
                    print("  {}".format(_dim("SKIPPED (--skip-check)")))
                    results["stage_{}".format(stage_num)] = {"status": "skipped"}
                else:
                    report = _run_checker_script(stage_num, project_root)
                    status = report.get("status", "unknown")
                    if status == "passed":
                        print("  {}".format(_green("PASSED")))
                    elif status == "failed":
                        print("  {}".format(_red("FAILED")))
                        for err in report.get("errors", [])[:5]:
                            print("    [{}] {}".format(err.get("type", ""), err.get("claim", "")))
                        if stop_on_checker_fail:
                            print("\n  {}".format(_red("CHECKER FAILED → 停止流水线")))
                            results["stage_{}".format(stage_num)] = report
                            break
                    else:
                        print("  {}".format(_yellow(status.upper())))
                    results["stage_{}".format(stage_num)] = report

            elif stage_num == 3:
                # result_builder: 先验证字段完整性
                vr = _validate_results_master(project_root)
                if vr["status"] == "passed":
                    print("  {}".format(_green("results_master.json 字段完整")))
                else:
                    print("  {}".format(_red("results_master.json 缺失字段:")))
                    for mf in vr["missing_fields"]:
                        print("    - DATA_REQUEST: {}".format(mf))
                    print("  {}".format(_yellow("请先补全缺失字段再继续")))
                results["stage_{}".format(stage_num)] = vr

            elif stage_num == 12:
                # renderer: markdown → final.docx
                try:
                    from renderer import render
                    ok = render(
                        project_root=project_root,
                        chapters_dir="chapters",
                        output_path="output/final.docx",
                    )
                    if ok:
                        print("  {}".format(_green("渲染完成 → output/final.docx")))
                        results["stage_{}".format(stage_num)] = {"status": "passed"}
                    else:
                        print("  {}".format(_red("渲染失败")))
                        results["stage_{}".format(stage_num)] = {"status": "failed"}
                        if stop_on_checker_fail:
                            break
                except ImportError:
                    print("  {}".format(_yellow("renderer.py 未找到，请手动调用")))
                    results["stage_{}".format(stage_num)] = {"status": "pending"}
                except Exception as e:
                    print("  {}".format(_red("渲染错误: {}".format(e))))
                    results["stage_{}".format(stage_num)] = {"status": "error", "reason": str(e)}

            elif stage_num == 5:
                # generate_tables
                try:
                    from generate_tables import generate_all_tables
                    generate_all_tables(project_root)
                    print("  {}".format(_green("表格生成完成")))
                    results["stage_{}".format(stage_num)] = {"status": "passed"}
                except Exception as e:
                    print("  {}".format(_yellow("表格生成跳过: {}".format(e))))
                    results["stage_{}".format(stage_num)] = {"status": "pending"}

            elif stage_num == 6:
                # generate_figures
                try:
                    from generate_figures import generate_all_figures
                    generate_all_figures(project_root)
                    print("  {}".format(_green("图表生成完成")))
                    results["stage_{}".format(stage_num)] = {"status": "passed"}
                except Exception as e:
                    print("  {}".format(_yellow("图表生成跳过: {}".format(e))))
                    results["stage_{}".format(stage_num)] = {"status": "pending"}

            elif stage_num == 7:
                # artifact_manifest_builder
                try:
                    from build_artifact_manifest import build_manifest
                    build_manifest(project_root)
                    print("  {}".format(_green("图表账本生成完成")))
                    results["stage_{}".format(stage_num)] = {"status": "passed"}
                except Exception as e:
                    print("  {}".format(_yellow("图表账本生成跳过: {}".format(e))))
                    results["stage_{}".format(stage_num)] = {"status": "pending"}

            else:
                # 其他 script 阶段
                print("  {}".format(_dim("SCRIPT 阶段（需单独调用对应脚本）")))
                results["stage_{}".format(stage_num)] = {"status": "pending"}

    # ── 汇总 ──
    print("\n" + "=" * 70)
    print(_bold("  流水线汇总"))
    print("=" * 70)

    for stage_num in range(1, 16):
        key = "stage_{}".format(stage_num)
        if key not in results:
            continue
        info = STAGES[stage_num]
        r = results[key]
        status = r.get("status", "unknown")
        tag = "AGT" if info["type"] == "agent" else "SCR"

        if status == "passed":
            s = _green("PASSED")
        elif status == "failed":
            s = _red("FAILED")
        elif status == "NOT_IMPLEMENTED":
            s = _yellow("NOT_IMPL")
        elif status == "exists" or r.get("has_output"):
            s = _green("DONE")
        elif status == "not_generated" or status == "pending":
            s = _dim("PENDING")
        else:
            s = _yellow(status.upper())

        print("  [{:3s}] {:2d}. {:40s} {}".format(tag, stage_num, info["name"], s))

    if args.dry_run:
        print("\n  {}".format(_dim("（dry-run 模式，未实际执行任何操作）")))


if __name__ == "__main__":
    main()
