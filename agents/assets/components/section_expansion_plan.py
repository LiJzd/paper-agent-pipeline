# -*- coding: utf-8 -*-
"""
数学建模论文各章节扩写计划
为 evidence_based_expander 提供每章的扩写目标和指导
"""

# 章节扩写计划配置
# 格式: chapter_id -> expansion_plan
SECTION_EXPANSION_PLAN = {
    # ============================================================
    # 一、问题重述 (Chapter 1)
    # ============================================================
    "problem_restatement": {
        "target_words": "800-1200",
        "sections": {
            "background": {
                "target_words": "300-400",
                "expansion_goals": [
                    "说明行业背景和市场现状",
                    "描述自助量贩餐饮模式的特点",
                    "阐述数字化转型的必要性",
                ],
                "allowed_content": [
                    "industry_context",  # 行业背景
                    "pain_points",       # 痛点描述
                    "digital_transformation",  # 数字化转型
                ],
                "forbidden_content": [
                    "specific_numbers",  # 不得出现具体数字
                    "model_results",     # 不得出现模型结果
                ],
            },
            "task_description": {
                "target_words": "500-800",
                "expansion_goals": [
                    "逐条说明五个任务",
                    "说明任务之间的逻辑关系",
                    "说明数据来源和约束",
                ],
                "allowed_content": [
                    "task_list",
                    "task_dependencies",
                    "data_sources",
                ],
                "forbidden_content": [
                    "solution_approach",  # 不得提前透露解法
                    "specific_numbers",
                ],
            },
        },
    },

    # ============================================================
    # 二、问题分析 (Chapter 2)
    # ============================================================
    "problem_analysis": {
        "target_words": "1000-1500",
        "sections": {
            "problem1_analysis": {
                "target_words": "150-250",
                "expansion_goals": [
                    "说明数据分析的核心目标",
                    "说明数据质量评估的必要性",
                    "说明可视化分析的思路",
                ],
                "allowed_content": [
                    "analysis_objectives",
                    "data_quality_concerns",
                    "visualization_strategy",
                ],
            },
            "problem2_analysis": {
                "target_words": "200-300",
                "expansion_goals": [
                    "说明预测目标（就餐人数、营养素、销售额）",
                    "说明时间序列数据的特点",
                    "说明模型选择的考虑因素",
                    "说明评价指标的选择",
                ],
                "allowed_content": [
                    "prediction_targets",
                    "data_characteristics",
                    "model_selection_criteria",
                    "evaluation_metrics",
                ],
            },
            "problem3_analysis": {
                "target_words": "200-300",
                "expansion_goals": [
                    "说明优化目标（利润最大化、浪费最小化）",
                    "说明约束条件（营养、多样性、需求）",
                    "说明午餐/晚餐拆分的必要性",
                    "说明线性规划的适用性",
                ],
                "allowed_content": [
                    "optimization_objectives",
                    "constraint_types",
                    "meal_splitting_logic",
                    "method_suitability",
                ],
            },
            "problem4_analysis": {
                "target_words": "200-300",
                "expansion_goals": [
                    "说明套餐设计的目标",
                    "说明价格约束和营养约束",
                    "说明组合优化的方法",
                    "说明满意度的代理指标",
                ],
                "allowed_content": [
                    "package_objectives",
                    "price_nutrition_constraints",
                    "combinatorial_optimization",
                    "satisfaction_proxy",
                ],
            },
            "problem5_analysis": {
                "target_words": "150-250",
                "expansion_goals": [
                    "说明运营建议的分析框架",
                    "说明建议需要数据支持",
                    "说明建议的可操作性要求",
                ],
                "allowed_content": [
                    "analysis_framework",
                    "data_driven_approach",
                    "actionability_requirements",
                ],
            },
        },
    },

    # ============================================================
    # 三、模型假设 (Chapter 3)
    # ============================================================
    "model_assumptions": {
        "target_words": "600-900",
        "sections": {
            "assumptions": {
                "target_words": "600-900",
                "expansion_goals": [
                    "每条假设后增加合理性说明",
                    "说明假设对模型的影响",
                    "说明假设的局限性",
                ],
                "allowed_content": [
                    "assumption_rationale",
                    "assumption_impact",
                    "assumption_limitations",
                ],
                "forbidden_content": [
                    "unjustified_assumptions",  # 不得列出无解释的假设
                ],
            },
        },
    },

    # ============================================================
    # 四、符号说明 (Chapter 4)
    # ============================================================
    "symbol_definitions": {
        "target_words": "300-500",
        "sections": {
            "symbols": {
                "target_words": "300-500",
                "expansion_goals": [
                    "确保符号与正文一致",
                    "保留符号表格",
                ],
                "allowed_content": [
                    "symbol_table",
                ],
                "note": "不需要强行扩长，保持表格形式",
            },
        },
    },

    # ============================================================
    # 五、问题一：数据预处理与分析 (Chapter 5)
    # ============================================================
    "problem1_solution": {
        "target_words": "1800-2500",
        "sections": {
            "data_overview": {
                "target_words": "300-400",
                "expansion_goals": [
                    "说明数据来源和采集方式",
                    "说明各字段的含义",
                    "说明数据的时间范围和规模",
                ],
                "allowed_content": [
                    "data_source_description",
                    "field_descriptions",
                    "data_scale",
                ],
                "required_source_keys": [
                    "data_overview.total_orders",
                    "data_overview.total_dish_details",
                    "data_overview.unique_dishes",
                    "data_overview.date_range",
                ],
            },
            "data_cleaning": {
                "target_words": "300-400",
                "expansion_goals": [
                    "说明缺失值处理逻辑",
                    "说明异常值检测方法",
                    "说明数据整合过程",
                    "说明衍生字段的创建",
                ],
                "allowed_content": [
                    "missing_value_handling",
                    "outlier_detection",
                    "data_integration",
                    "feature_engineering",
                ],
                "required_source_keys": [
                    "data_overview.missing_values",
                    "data_overview.outliers",
                ],
            },
            "descriptive_statistics": {
                "target_words": "400-500",
                "expansion_goals": [
                    "分析消费金额的分布特征",
                    "分析日维度的就餐人数变化",
                    "分析周维度的工作日/周末差异",
                    "分析月维度的趋势变化",
                ],
                "allowed_content": [
                    "distribution_analysis",
                    "temporal_analysis",
                    "weekday_weekend_comparison",
                ],
                "required_source_keys": [
                    "money_stats.mean",
                    "money_stats.median",
                    "money_stats.std",
                    "daily_stats.avg_orders",
                    "daily_stats.avg_revenue",
                ],
                "required_figures": [
                    "fig1_daily_orders.png",
                    "fig2_weekday_avg.png",
                    "fig3_money_boxplot.png",
                    "fig4_money_hist.png",
                ],
            },
            "dish_analysis": {
                "target_words": "400-500",
                "expansion_goals": [
                    "分析菜品销售的长尾分布",
                    "分析Top菜品的特点",
                    "分析菜品价格与销量的关系",
                    "每个图后增加2-3句读图分析",
                ],
                "allowed_content": [
                    "long_tail_distribution",
                    "top_dishes_analysis",
                    "price_sales_relationship",
                    "figure_interpretation",
                ],
                "required_source_keys": [
                    "top10_dishes",
                ],
                "required_figures": [
                    "fig7_dish_pie.png",
                    "fig8_price_sales.png",
                ],
            },
            "correlation_analysis": {
                "target_words": "300-400",
                "expansion_goals": [
                    "分析营养成分之间的相关性",
                    "解释相关性的业务含义",
                    "分析菜品共现关系",
                ],
                "allowed_content": [
                    "nutrient_correlation",
                    "co_occurrence_analysis",
                    "business_interpretation",
                ],
                "required_source_keys": [
                    "nutrient_corr",
                ],
                "required_figures": [
                    "fig5_nutrient_corr.png",
                    "fig9_nutrient_radar.png",
                ],
            },
        },
    },

    # ============================================================
    # 六、问题二：需求预测 (Chapter 6)
    # ============================================================
    "problem2_solution": {
        "target_words": "2200-3200",
        "sections": {
            "prediction_framework": {
                "target_words": "200-300",
                "expansion_goals": [
                    "说明预测目标的分解",
                    "说明预测思路（人数→营养素→销售额）",
                    "说明数据准备过程",
                ],
                "allowed_content": [
                    "target_decomposition",
                    "prediction_pipeline",
                    "data_preparation",
                ],
            },
            "feature_engineering": {
                "target_words": "200-300",
                "expansion_goals": [
                    "说明特征选择的依据",
                    "说明每个特征的含义",
                    "说明特征工程的方法",
                ],
                "allowed_content": [
                    "feature_selection",
                    "feature_description",
                    "engineering_methods",
                ],
            },
            "model_building": {
                "target_words": "500-700",
                "expansion_goals": [
                    "说明模型的数学原理",
                    "说明模型的参数设置",
                    "说明训练/验证的划分",
                    "说明交叉验证的方法",
                ],
                "allowed_content": [
                    "mathematical_principles",
                    "parameter_settings",
                    "train_test_split",
                    "cross_validation",
                ],
                "required_source_keys": [
                    "method_config.train_test_split",
                    "method_config.cv_folds",
                ],
            },
            "model_evaluation": {
                "target_words": "400-600",
                "expansion_goals": [
                    "定义评价指标（MAE、RMSE、R²、MAPE）",
                    "解释每个指标的含义",
                    "分析模型的评价结果",
                    "进行残差分析",
                    "讨论模型的优缺点",
                ],
                "allowed_content": [
                    "metric_definitions",
                    "metric_interpretation",
                    "residual_analysis",
                    "model_comparison",
                ],
                "required_source_keys": [
                    "model_comparison",
                ],
                "required_figures": [
                    "fig11_model_fit.png",
                    "fig13_residuals.png",
                    "fig14_model_compare.png",
                ],
                "critical_rules": [
                    "必须分别写清楚 MAE、RMSE、R² 的值",
                    "不得把 MAE 写成 R²",
                    "如果 R² 很低（如0.027），必须如实说明模型解释能力有限",
                ],
            },
            "forecast_results": {
                "target_words": "400-600",
                "expansion_goals": [
                    "展示2025年5月工作日完整预测表",
                    "分析预测结果的合理性",
                    "讨论预测的可靠性和局限性",
                    "与历史数据对比",
                ],
                "allowed_content": [
                    "forecast_table",
                    "reasonability_analysis",
                    "reliability_discussion",
                    "historical_comparison",
                ],
                "required_source_keys": [
                    "prediction.may_forecast",
                    "prediction.forecast_summary.avg_daily_orders",
                    "prediction.forecast_summary.avg_daily_revenue",
                ],
                "required_figures": [
                    "fig12_may_forecast.png",
                ],
                "critical_rules": [
                    "必须包含完整5月工作日预测表",
                    "如果缺少数据，必须输出 ARTIFACT_REQUEST",
                ],
            },
        },
    },

    # ============================================================
    # 七、问题三：菜品优化 (Chapter 7)
    # ============================================================
    "problem3_solution": {
        "target_words": "2500-3500",
        "sections": {
            "optimization_model": {
                "target_words": "500-700",
                "expansion_goals": [
                    "定义决策变量",
                    "解释目标函数的每一项",
                    "解释成本、收入、浪费惩罚的业务含义",
                    "说明 max(0, x-d) 的线性化方法",
                    "列出所有约束条件并解释",
                ],
                "allowed_content": [
                    "decision_variables",
                    "objective_function",
                    "cost_revenue_waste",
                    "linearization",
                    "constraints",
                ],
                "required_source_keys": [
                    "method_config.cost_ratio",
                    "method_config.waste_penalty",
                ],
            },
            "constraint_explanation": {
                "target_words": "300-500",
                "expansion_goals": [
                    "解释营养均衡约束",
                    "解释菜品多样性约束",
                    "解释供应量约束",
                    "解释需求约束",
                    "说明午餐/晚餐拆分逻辑",
                ],
                "allowed_content": [
                    "nutrition_constraint",
                    "diversity_constraint",
                    "supply_constraint",
                    "demand_constraint",
                    "meal_split_logic",
                ],
            },
            "solution_process": {
                "target_words": "300-400",
                "expansion_goals": [
                    "说明求解工具和方法",
                    "说明参数估计过程",
                    "说明求解结果",
                ],
                "allowed_content": [
                    "solver_details",
                    "parameter_estimation",
                    "solution_summary",
                ],
            },
            "optimization_results": {
                "target_words": "800-1200",
                "expansion_goals": [
                    "展示2025年5月6日-12日每个工作日的午餐和晚餐方案",
                    "分析每日备菜量的变化",
                    "计算成本、收入、利润、浪费率",
                    "进行灵敏度分析",
                ],
                "allowed_content": [
                    "daily_plans",
                    "cost_revenue_analysis",
                    "waste_analysis",
                    "sensitivity_analysis",
                ],
                "required_source_keys": [
                    "optimization.target_dates",
                    "optimization.plans_summary",
                ],
                "required_figures": [
                    "fig15_dish_structure.png",
                    "fig16_nutrition_radar.png",
                ],
                "critical_rules": [
                    "必须包含5月6日、7日、8日、9日、12日的完整方案",
                    "午餐和晚餐必须分别给出",
                    "如果数据不足，必须输出 ARTIFACT_REQUEST",
                    "不得只给部分日期的方案",
                ],
            },
        },
    },

    # ============================================================
    # 八、问题四：套餐设计 (Chapter 8)
    # ============================================================
    "problem4_solution": {
        "target_words": "1800-2500",
        "sections": {
            "package_model": {
                "target_words": "400-500",
                "expansion_goals": [
                    "说明整数规划模型",
                    "定义决策变量",
                    "解释目标函数",
                    "说明价格、数量、营养约束",
                    "说明满意度代理变量",
                ],
                "allowed_content": [
                    "integer_programming",
                    "decision_variables",
                    "objective_function",
                    "constraints",
                    "satisfaction_proxy",
                ],
            },
            "nutrition_standards": {
                "target_words": "200-300",
                "expansion_goals": [
                    "引用中国居民膳食指南",
                    "说明每餐营养标准",
                    "说明标准的来源和依据",
                ],
                "allowed_content": [
                    "dietary_guidelines",
                    "nutrition_standards",
                    "standard_sources",
                ],
            },
            "package_results": {
                "target_words": "600-800",
                "expansion_goals": [
                    "展示三个价位的套餐方案",
                    "分析每个套餐的营养成分",
                    "对比不同价位的套餐",
                    "讨论套餐的优缺点",
                ],
                "allowed_content": [
                    "package_plans",
                    "nutrition_analysis",
                    "comparison",
                    "pros_cons",
                ],
                "required_source_keys": [
                    "packages.single_packages",
                ],
                "critical_rules": [
                    "如果套餐纤维低于标准、热量超出标准，不得写'均满足营养均衡要求'",
                    "应改为'部分指标满足，部分指标需改进'",
                    "结论必须由 package_nutrition 表支持",
                ],
            },
            "improvement_suggestions": {
                "target_words": "300-400",
                "expansion_goals": [
                    "提出不满足项的改进建议",
                    "讨论套餐的优化方向",
                    "说明套餐设计的局限性",
                ],
                "allowed_content": [
                    "improvement_suggestions",
                    "optimization_directions",
                    "limitations",
                ],
            },
        },
    },

    # ============================================================
    # 九、问题五：运营优化建议 (Chapter 9)
    # ============================================================
    "problem5_solution": {
        "target_words": "1200-1800",
        "sections": {
            "supply_demand_optimization": {
                "target_words": "200-300",
                "expansion_goals": [
                    "基于预测结果提出精准备货建议",
                    "说明动态备货机制",
                    "增加实施路径和风险提示",
                ],
                "allowed_content": [
                    "precise_stocking",
                    "dynamic_mechanism",
                    "implementation_path",
                    "risk_warning",
                ],
                "required_source_keys": [
                    "prediction.forecast_summary",
                ],
            },
            "dish_structure_optimization": {
                "target_words": "200-300",
                "expansion_goals": [
                    "基于菜品分析提出结构调整建议",
                    "说明核心菜品、潜力菜品、低效菜品",
                    "增加数据化监控指标",
                ],
                "allowed_content": [
                    "core_dishes",
                    "potential_dishes",
                    "inefficient_dishes",
                    "monitoring_metrics",
                ],
                "required_source_keys": [
                    "top10_dishes",
                ],
            },
            "pricing_strategy": {
                "target_words": "200-300",
                "expansion_goals": [
                    "基于套餐设计提出定价建议",
                    "说明时段差异化定价",
                    "说明组合捆绑策略",
                ],
                "allowed_content": [
                    "pricing_suggestions",
                    "time_based_pricing",
                    "bundling_strategy",
                ],
                "required_source_keys": [
                    "packages.single_packages",
                ],
            },
            "waste_reduction": {
                "target_words": "200-300",
                "expansion_goals": [
                    "基于优化结果提出减少浪费建议",
                    "说明精准备菜的具体方法",
                    "增加数据化监控指标",
                ],
                "allowed_content": [
                    "waste_reduction_methods",
                    "precise_preparation",
                    "monitoring_metrics",
                ],
                "required_source_keys": [
                    "optimization.plans_summary",
                ],
            },
            "customer_experience": {
                "target_words": "200-300",
                "expansion_goals": [
                    "提出菜品多样性改善建议",
                    "说明个性化推荐的可能性",
                    "说明季节性菜品的引入",
                ],
                "allowed_content": [
                    "diversity_improvement",
                    "personalization",
                    "seasonal_dishes",
                ],
            },
        },
    },

    # ============================================================
    # 十、模型评价与推广 (Chapter 10)
    # ============================================================
    "model_evaluation": {
        "target_words": "1000-1500",
        "sections": {
            "advantages": {
                "target_words": "300-400",
                "expansion_goals": [
                    "说明模型的优点",
                    "说明方法的创新点",
                    "说明结果的可靠性",
                ],
                "allowed_content": [
                    "model_advantages",
                    "method_innovations",
                    "result_reliability",
                ],
            },
            "disadvantages": {
                "target_words": "300-400",
                "expansion_goals": [
                    "说明模型的不足",
                    "说明数据的局限性",
                    "说明参数的敏感性",
                ],
                "allowed_content": [
                    "model_disadvantages",
                    "data_limitations",
                    "parameter_sensitivity",
                ],
            },
            "applicability": {
                "target_words": "200-300",
                "expansion_goals": [
                    "说明模型的适用场景",
                    "说明模型的不适用场景",
                    "说明推广的条件",
                ],
                "allowed_content": [
                    "applicable_scenarios",
                    "inapplicable_scenarios",
                    "generalization_conditions",
                ],
            },
            "improvement_directions": {
                "target_words": "200-300",
                "expansion_goals": [
                    "提出改进方向",
                    "说明未来研究的可能性",
                    "说明技术升级的路径",
                ],
                "allowed_content": [
                    "improvement_directions",
                    "future_research",
                    "technology_upgrade",
                ],
            },
        },
    },
}


def get_expansion_plan(chapter_id: str) -> dict:
    """获取指定章节的扩写计划"""
    return SECTION_EXPANSION_PLAN.get(chapter_id, {})


def get_all_chapter_ids() -> list:
    """获取所有章节ID"""
    return list(SECTION_EXPANSION_PLAN.keys())


def get_expansion_targets(chapter_id: str) -> dict:
    """获取章节的扩写目标字典"""
    plan = SECTION_EXPANSION_PLAN.get(chapter_id, {})
    targets = {}
    for section_id, section_config in plan.get("sections", {}).items():
        targets[section_id] = {
            "target_words": section_config.get("target_words", "unknown"),
            "expansion_goals": section_config.get("expansion_goals", []),
            "required_source_keys": section_config.get("required_source_keys", []),
            "required_figures": section_config.get("required_figures", []),
            "critical_rules": section_config.get("critical_rules", []),
        }
    return targets


if __name__ == "__main__":
    # 测试输出
    for chapter_id in get_all_chapter_ids():
        plan = get_expansion_plan(chapter_id)
        print(f"\n{'='*60}")
        print(f"Chapter: {chapter_id}")
        print(f"Target words: {plan.get('target_words', 'N/A')}")
        print(f"Sections: {list(plan.get('sections', {}).keys())}")
