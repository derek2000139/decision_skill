"""
意图识别器 + 框架路由

基于用户输入，识别决策场景类型并推荐适用框架
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IntentResult:
    scene_type: str                          # daily_life | career | venture | strategy
    complexity: str                          # low | medium | high
    time_sensitivity: str                    # urgent | normal | long_term
    stakeholders: str                        # individual | team | organization
    detected_keywords: list[str]
    recommended_frameworks: list[str]
    detected_biases_risk: list[str]
    confidence: float                        # 0.0 - 1.0
    explanation: str


# ──────────────────────────────────────────────
# 规则配置
# ──────────────────────────────────────────────

SCENE_RULES = {
    "daily_life": {
        "keywords": [
            "吃什么", "去哪", "买哪个", "选哪个", "今天", "要不要",
            "穿什么", "看什么", "玩什么", "订哪个", "要哪个"
        ],
        "frameworks": ["satisficing", "10_10_10", "random_weighted"],
        "complexity": "low",
        "time_sensitivity": "urgent",
        "stakeholders": "individual"
    },
    "career": {
        "keywords": [
            "考研", "深造", "留学", "跳槽", "转行", "辞职", "创业",
            "婚姻", "结婚", "要不要去", "职业", "工作", "升职",
            "继续还是", "是否应该"
        ],
        "frameworks": ["regret_minimization", "pros_cons", "values_matrix", "10_10_10"],
        "complexity": "high",
        "time_sensitivity": "long_term",
        "stakeholders": "individual"
    },
    "venture": {
        "keywords": [
            "创业", "投资", "可行性", "成功率", "概率", "值不值得",
            "风险", "回报", "收益", "融资", "产品", "市场", "机会"
        ],
        "frameworks": ["expected_value", "rice_scoring", "base_rate", "scenario_planning"],
        "complexity": "high",
        "time_sensitivity": "normal",
        "stakeholders": "team"
    },
    "strategy": {
        "keywords": [
            "战略", "竞争", "转型", "扩张", "市场进入", "公司决策",
            "风险评估", "业务", "战略规划", "组织", "并购", "布局"
        ],
        "frameworks": ["mckinsey_7s", "swot", "scenario_planning", "expected_value"],
        "complexity": "high",
        "time_sensitivity": "long_term",
        "stakeholders": "organization"
    }
}

BIAS_RULES = {
    "status_quo_bias": {
        "triggers": ["一直在", "习惯了", "不想改变", "稳定", "不想折腾", "保持现状"],
        "reference": "Samuelson & Zeckhauser (1988); Kahneman (2011) Ch.28"
    },
    "loss_aversion": {
        "triggers": ["万一失败", "风险太大", "损失", "亏了", "赔了", "承担不起"],
        "reference": "Kahneman & Tversky (1979); Plous (1993) Ch.6"
    },
    "overconfidence": {
        "triggers": ["肯定", "一定", "没问题", "必然", "绝对"],
        "reference": "Fischhoff et al. (1977); Plous (1993) Ch.14"
    },
    "sunk_cost_fallacy": {
        "triggers": ["已经投入", "花了这么多", "不能白费", "已经做了这么久", "放弃太可惜"],
        "reference": "Arkes & Blumer (1985); Plous (1993) Ch.11"
    },
    "availability_heuristic": {
        "triggers": ["我认识的人", "我听说", "身边", "我见过", "最近看到"],
        "reference": "Tversky & Kahneman (1973); Plous (1993) Ch.8"
    },
    "planning_fallacy": {
        "triggers": ["很快就能", "用不了多久", "大概一年", "应该不难", "简单的"],
        "reference": "Kahneman & Tversky (1977); Flyvbjerg (2008)"
    },
    "anchoring": {
        "triggers": ["第一个报价", "最开始说的", "参考了", "对比了"],
        "reference": "Tversky & Kahneman (1974); Plous (1993) Ch.10"
    },
    "framing_effect": {
        "triggers": ["这样说的话", "换个说法", "从损失角度", "从收益角度"],
        "reference": "Kahneman & Tversky (1979); Plous (1993) Ch.7"
    },
    "representativeness": {
        "triggers": ["看起来像", "感觉符合", "这种类型", "典型的"],
        "reference": "Kahneman & Tversky (1972); Plous (1993) Ch.9"
    }
}


# ──────────────────────────────────────────────
# 核心函数
# ──────────────────────────────────────────────

def classify_intent(user_input: str) -> IntentResult:
    """
    主入口：对用户输入执行意图识别
    
    Args:
        user_input: 用户的原始输入文本
    
    Returns:
        IntentResult: 结构化的意图识别结果
    """
    text = user_input.lower()
    
    scene_scores = _calculate_scene_scores(text)
    scene_type = max(scene_scores, key=scene_scores.get)
    confidence = _normalize_confidence(scene_scores[scene_type], sum(scene_scores.values()))
    
    detected_keywords = _extract_keywords(text, scene_type)
    detected_biases = _detect_biases(text)
    rule = SCENE_RULES[scene_type]
    
    explanation = _build_explanation(scene_type, detected_keywords, detected_biases)
    
    return IntentResult(
        scene_type=scene_type,
        complexity=rule["complexity"],
        time_sensitivity=rule["time_sensitivity"],
        stakeholders=rule["stakeholders"],
        detected_keywords=detected_keywords,
        recommended_frameworks=rule["frameworks"],
        detected_biases_risk=detected_biases,
        confidence=round(confidence, 2),
        explanation=explanation
    )


def _calculate_scene_scores(text: str) -> dict[str, int]:
    """计算每个场景类型的关键词匹配分数"""
    scores = {scene: 0 for scene in SCENE_RULES}
    for scene, config in SCENE_RULES.items():
        for kw in config["keywords"]:
            if kw in text:
                scores[scene] += 1
    # 避免全0时的歧义：给 career 一个默认微小偏好
    if sum(scores.values()) == 0:
        scores["career"] = 0.1
    return scores


def _normalize_confidence(top_score: float, total_score: float) -> float:
    """将匹配分数归一化为置信度"""
    if total_score == 0:
        return 0.5
    raw = top_score / total_score
    # 压缩到 0.5 - 0.99 区间，避免极端值
    return 0.5 + raw * 0.49


def _extract_keywords(text: str, scene_type: str) -> list[str]:
    """提取命中的关键词"""
    found = []
    for kw in SCENE_RULES[scene_type]["keywords"]:
        if kw in text:
            found.append(kw)
    return found


def _detect_biases(text: str) -> list[str]:
    """检测潜在认知偏见"""
    detected = []
    for bias, config in BIAS_RULES.items():
        for trigger in config["triggers"]:
            if trigger in text:
                detected.append(bias)
                break
    return detected


def _build_explanation(
    scene_type: str,
    keywords: list[str],
    biases: list[str]
) -> str:
    """生成中文解释文本"""
    scene_labels = {
        "daily_life": "日常生活决策",
        "career": "职业/人生规划决策",
        "venture": "创业/投资决策",
        "strategy": "企业战略决策"
    }
    label = scene_labels.get(scene_type, scene_type)
    kw_str = "、".join(keywords) if keywords else "语义分析"
    bias_str = "、".join(biases) if biases else "未检测到明显偏见"
    
    return (
        f"根据输入内容，识别为【{label}】场景。"
        f"触发关键词：{kw_str}。"
        f"潜在认知偏见风险：{bias_str}。"
    )


def format_output(result: IntentResult) -> str:
    """格式化输出，用于展示给用户"""
    framework_display = {
        "satisficing": "满意解理论（Simon, 1957）",
        "10_10_10": "10-10-10时间维度法（Welch, 2009）",
        "random_weighted": "加权随机决策",
        "regret_minimization": "遗憾最小化框架（Bezos, 2010）",
        "pros_cons": "利弊清单法（Franklin, 1772）",
        "values_matrix": "价值观矩阵（Covey, 1989）",
        "expected_value": "期望值模型（Von Neumann, 1944）",
        "rice_scoring": "RICE评分模型（Intercom）",
        "base_rate": "基准率校准法（Kahneman & Tetlock）",
        "mckinsey_7s": "麦肯锡7S框架（Peters & Waterman, 1982）",
        "swot": "SWOT/TOWS分析（Humphrey, 1960s）",
        "scenario_planning": "情景规划法（Shell, 1970s）"
    }
    
    bias_display = {
        "status_quo_bias": "现状偏见",
        "loss_aversion": "损失厌恶",
        "overconfidence": "过度自信",
        "sunk_cost_fallacy": "沉没成本谬误",
        "availability_heuristic": "可得性启发",
        "planning_fallacy": "计划谬误",
        "anchoring": "锚定效应",
        "framing_effect": "框架效应",
        "representativeness": "代表性启发"
    }
    
    frameworks_str = "\n".join([
        f"  {i+1}. {framework_display.get(f, f)}"
        for i, f in enumerate(result.recommended_frameworks)
    ])
    
    biases_str = (
        "\n".join([f"  ⚠️  {bias_display.get(b, b)}" for b in result.detected_biases_risk])
        if result.detected_biases_risk
        else "  ✅ 未检测到明显认知偏见风险"
    )
    
    return f"""
╔═══════════════════════════════════════════════════╗
║              意图识别结果                         ║
╠═══════════════════════════════════════════════════╣
║ 场景类型：{result.scene_type:<37} ║
║ 复杂度：  {result.complexity:<37} ║
║ 时间维度：{result.time_sensitivity:<37} ║
║ 置信度：  {result.confidence:<37} ║
╠═══════════════════════════════════════════════════╣
║ 推荐决策框架：                                    ║
{frameworks_str}
╠═══════════════════════════════════════════════════╣
║ 认知偏见风险预警：                                ║
{biases_str}
╠═══════════════════════════════════════════════════╣
║ 说明：{result.explanation[:44]}
╚═══════════════════════════════════════════════════╝
"""


# ──────────────────────────────────────────────
# 入口
# ──────────────────────────────────────────────

if __name__ == "__main__":
    test_cases = [
        "我今天要吃什么，好纠结",
        "我是继续深造还是直接工作？我已经准备了一年了不想放弃",
        "我的创业项目成功的可能性有多大？我认识的人里有好几个做这个成功了",
        "公司现在面临战略转型，风险怎么评估？"
    ]
    
    for case in test_cases:
        print(f"\n输入：{case}")
        result = classify_intent(case)
        print(format_output(result))
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
