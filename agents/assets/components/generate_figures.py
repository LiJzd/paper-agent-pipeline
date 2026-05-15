"""
generate_figures.py — 从 figure_data CSV 生成图表 PNG

读取 artifacts/figure_data/*.csv 中的数据，使用 matplotlib 生成图表。
每个图表必须有对应的 figure_data CSV，禁止手工编造图表数据。

用法：
    python generate_figures.py --project-root .
    python generate_figures.py --manifest artifacts/artifact_manifest.json
"""

import argparse
import csv
import json
import os
import sys


def generate_figures(manifest_path: str, project_root: str = ".") -> dict:
    """根据 manifest 生成所有图表"""
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    generated = []
    errors = []

    for fig in manifest.get("figures", []):
        fid = fig.get("figure_id", "unknown")
        data_path = fig.get("data_path", "")
        image_path = fig.get("image_path", "")
        fig_type = fig.get("type", "bar")

        if not data_path or not image_path:
            errors.append({"type": "missing_path", "figure_id": fid, "message": "缺少 data_path 或 image_path"})
            continue

        abs_data = os.path.join(project_root, data_path) if not os.path.isabs(data_path) else data_path
        abs_image = os.path.join(project_root, image_path) if not os.path.isabs(image_path) else image_path

        if not os.path.exists(abs_data):
            errors.append({"type": "data_file_missing", "figure_id": fid, "message": "数据文件不存在: {}".format(data_path)})
            continue

        try:
            data = _read_csv(abs_data)
            os.makedirs(os.path.dirname(abs_image), exist_ok=True)
            _plot_figure(data, abs_image, fig)
            generated.append({"figure_id": fid, "image_path": image_path, "data_path": data_path})
        except Exception as e:
            errors.append({"type": "generation_error", "figure_id": fid, "message": str(e)})

    # 自动登记生成的文件到 manifest
    try:
        from artifact_manifest import ArtifactManifest
        manifest_obj = ArtifactManifest(manifest_path)
        for g in generated:
            manifest_obj.update_figure_entry(
                g["figure_id"],
                image_path=g["image_path"],
                data_path=g["data_path"],
                generated_by="generate_figures.py"
            )
    except Exception:
        pass

    return {"generated": generated, "errors": errors}


def _read_csv(path: str) -> dict:
    """读取 CSV 返回 {columns: [...], rows: [[...], ...]}"""
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return {"columns": [], "rows": []}
    return {"columns": rows[0], "rows": rows[1:]}


def _plot_figure(data: dict, image_path: str, fig_def: dict):
    """根据数据和类型生成图表"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm

        # 中文字体
        fm._load_fontmanager(try_read_cache=False)
        plt.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False
    except ImportError:
        raise ImportError("需要 matplotlib: pip install matplotlib")

    fig_type = fig_def.get("type", "bar")
    title = fig_def.get("title", "")
    columns = data.get("columns", [])
    rows = data.get("rows", [])

    if not rows:
        raise ValueError("CSV 数据为空")

    fig, ax = plt.subplots(figsize=(8, 5))

    if fig_type == "bar" and len(columns) >= 2:
        labels = [r[0] for r in rows if len(r) > 0]
        values = []
        for r in rows:
            try:
                values.append(float(r[1]) if len(r) > 1 else 0)
            except ValueError:
                values.append(0)
        ax.bar(labels, values)
        ax.set_xlabel(columns[0] if columns else "")
        ax.set_ylabel(columns[1] if len(columns) > 1 else "")

    elif fig_type == "line" and len(columns) >= 2:
        x = list(range(len(rows)))
        for col_idx in range(1, min(len(columns), len(rows[0]) + 1)):
            values = []
            for r in rows:
                try:
                    values.append(float(r[col_idx]) if col_idx < len(r) else 0)
                except ValueError:
                    values.append(0)
            ax.plot(x, values, label=columns[col_idx] if col_idx < len(columns) else "")
        ax.legend()
        ax.set_xlabel(columns[0] if columns else "")

    elif fig_type == "scatter" and len(columns) >= 3:
        x_vals, y_vals = [], []
        for r in rows:
            try:
                x_vals.append(float(r[1]))
                y_vals.append(float(r[2]))
            except (ValueError, IndexError):
                pass
        ax.scatter(x_vals, y_vals)
        ax.set_xlabel(columns[1] if len(columns) > 1 else "")
        ax.set_ylabel(columns[2] if len(columns) > 2 else "")

    else:
        # 默认: 简单柱状图
        labels = [r[0] for r in rows if len(r) > 0]
        values = []
        for r in rows:
            try:
                values.append(float(r[1]) if len(r) > 1 else 0)
            except ValueError:
                values.append(0)
        ax.bar(labels, values)

    if title:
        ax.set_title(title)
    plt.tight_layout()
    plt.savefig(image_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="从 figure_data 生成图表")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--manifest", default=None)
    args = parser.parse_args()

    root = os.path.abspath(args.project_root)
    manifest = args.manifest or os.path.join(root, "artifacts", "artifact_manifest.json")

    report = generate_figures(manifest, root)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
