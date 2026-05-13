"""
论文图表生成工具集
从数学建模图表智能体和通用图表智能体中提取的绘图函数。

使用方法：
    import sys, os
    sys.path.insert(0, os.path.expanduser('~/.claude/agents/assets/components'))
    from paper_figure_utils import (
        plot_distribution, plot_time_series, plot_comparison,
        plot_heatmap, plot_flowchart, plot_radar, plot_error_analysis,
        init_matplotlib_chinese,
    )

所有图表默认 300 DPI，PNG 格式，中文标签。
"""

import numpy as np


def _get_plt():
    """延迟导入 matplotlib 并配置中文。"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except OSError:
        try:
            plt.style.use('seaborn-whitegrid')
        except OSError:
            pass
    return plt


def _save_fig(plt, fig, filename, dpi=300):
    """保存图表。"""
    import os
    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    plt.close(fig)


# ============================================================
# 数据探索类
# ============================================================

def plot_distribution(data, title, xlabel, ylabel, filename):
    """数据分布图：直方图 + 箱线图。"""
    plt = _get_plt()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].hist(data, bins=30, edgecolor='black', alpha=0.7)
    axes[0].set_title(f'{title} - 直方图')
    axes[0].set_xlabel(xlabel)
    axes[0].set_ylabel(ylabel)

    axes[1].boxplot(data)
    axes[1].set_title(f'{title} - 箱线图')
    axes[1].set_ylabel(ylabel)

    fig.tight_layout()
    _save_fig(plt, fig, filename)


def plot_heatmap(data, title, filename, annot=True, fmt='.2f', cmap='YlOrRd'):
    """热力图。"""
    plt = _get_plt()
    import seaborn as sns
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(data, annot=annot, fmt=fmt, cmap=cmap, ax=ax, linewidths=0.5)
    ax.set_title(title, fontsize=14)
    _save_fig(plt, fig, filename)


# ============================================================
# 时序与预测类
# ============================================================

def plot_time_series(x, y_true, y_pred, title, filename,
                     true_label='真实值', pred_label='预测值'):
    """时序预测图：真实值 vs 预测值 + 误差阴影。"""
    plt = _get_plt()
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(x, y_true, 'b-', label=true_label, linewidth=2)
    ax.plot(x, y_pred, 'r--', label=pred_label, linewidth=2)
    ax.fill_between(x, y_true, y_pred, alpha=0.3, color='gray')

    ax.set_title(title, fontsize=14)
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel('数值', fontsize=12)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)

    _save_fig(plt, fig, filename)


# ============================================================
# 对比类
# ============================================================

def plot_comparison(methods, metrics, title, filename):
    """方法对比柱状图。

    Args:
        methods: 方法名称列表
        metrics: dict {指标名: {方法名: 数值}}
        filename: 输出路径
    """
    plt = _get_plt()
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(metrics))
    width = 0.8 / len(methods)

    for i, method in enumerate(methods):
        values = [metrics[m].get(method, 0) for m in metrics]
        ax.bar(x + i * width, values, width, label=method)

    ax.set_title(title, fontsize=14)
    ax.set_xticks(x + width * len(methods) / 2)
    ax.set_xticklabels(list(metrics.keys()))
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    _save_fig(plt, fig, filename)


# ============================================================
# 流程与结构类
# ============================================================

def plot_flowchart(steps, title, filename):
    """垂直流程图。"""
    plt = _get_plt()
    fig, ax = plt.subplots(figsize=(12, 8))

    n = len(steps)
    y_positions = np.linspace(0.9, 0.1, n)

    for i, (step, y) in enumerate(zip(steps, y_positions)):
        rect = plt.Rectangle((0.3, y - 0.03), 0.4, 0.06,
                              fill=True, facecolor='lightblue',
                              edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(0.5, y, step, ha='center', va='center',
                fontsize=12, fontweight='bold')
        if i < n - 1:
            ax.annotate('', xy=(0.5, y_positions[i + 1] + 0.03),
                        xytext=(0.5, y - 0.03),
                        arrowprops=dict(arrowstyle='->', lw=2))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(title, fontsize=14)
    ax.axis('off')

    _save_fig(plt, fig, filename)


# ============================================================
# 评价类
# ============================================================

def plot_radar(categories, values, title, filename):
    """雷达图。"""
    plt = _get_plt()
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    values_plot = values + values[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, values_plot, 'o-', linewidth=2)
    ax.fill(angles, values_plot, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_title(title, fontsize=14, pad=20)

    _save_fig(plt, fig, filename)


# ============================================================
# 误差分析类
# ============================================================

def plot_error_analysis(y_true, y_pred, title, filename):
    """误差分析三联图：误差分布 + 误差时序 + 真实vs预测散点。"""
    plt = _get_plt()
    errors = np.array(y_true) - np.array(y_pred)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # 误差分布
    axes[0].hist(errors, bins=30, edgecolor='black', alpha=0.7)
    axes[0].set_title('误差分布')
    axes[0].set_xlabel('误差值')
    axes[0].set_ylabel('频数')

    # 误差时序
    axes[1].plot(errors, 'b-', alpha=0.7)
    axes[1].axhline(y=0, color='r', linestyle='--')
    axes[1].set_title('误差时序')
    axes[1].set_xlabel('样本')
    axes[1].set_ylabel('误差')

    # 真实值 vs 预测值
    axes[2].scatter(y_true, y_pred, alpha=0.5)
    min_val = min(np.min(y_true), np.min(y_pred))
    max_val = max(np.max(y_true), np.max(y_pred))
    axes[2].plot([min_val, max_val], [min_val, max_val], 'r--')
    axes[2].set_title('真实值 vs 预测值')
    axes[2].set_xlabel('真实值')
    axes[2].set_ylabel('预测值')

    fig.suptitle(title, fontsize=14)
    fig.tight_layout()
    _save_fig(plt, fig, filename)


# ============================================================
# 学术配色方案
# ============================================================

COLOR_SCHEMES = {
    'academic_blue': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B'],
    'academic_green': ['#2D6A4F', '#40916C', '#52B788', '#74C69D', '#95D5B2'],
    'academic_grey': ['#212529', '#495057', '#6C757D', '#ADB5BD', '#DEE2E6'],
    'nature_style': ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F'],
}
