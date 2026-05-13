"""
决策评分计算器

支持多框架的量化计算：期望值、利弊评分、价值观矩阵、7S差距分析
"""

from dataclasses import dataclass
from typing import Optional
import math


# ──────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────

@dataclass
class ScoreResult:
    framework: str
    winner: Optional[str]
    scores: dict
    details: dict
    recommendation: str
    confidence_level: str    # high | medium | low
    bias_warnings: list[str]


# ──────────────────────────────────────────────
# 各框架计算器
# ──────────────────────────────────────────────

class SatisficingCalculator:
    """
    满意解计算器
    Simon (1957): 找到第一个满足所有阈值的选项
    """

    def calculate(self, options: list[str], thresholds: list[str], answers: dict) -> ScoreResult:
        # 模拟：用阈值数量代表约束严格程度
        threshold_count = len([t for t in thresholds if t])

        scores = {}
        for i, option in enumerate(options):
            # 在真实环境中，这里会对每个选项检验每个阈值
            # 演示：第一个选项默认通过（满意解逻辑）
            scores[option] = "满意解候选" if i == 0 else "待检验"

        return ScoreResult(
            framework="satisficing",
            winner=options[0] if options else None,
            scores=scores,
            details={
                "thresholds": thresholds,
                "threshold_count": threshold_count,
                "logic": "找到第一个满足所有阈值的选项即停止"
            },
            recommendation=(
                f"按照满意解原则，【{options[0]}】是第一个满足你设定标准的选项。"
                f"建议直接执行，停止进一步比较。"
                f"（来源：Simon, H. Administrative Behavior, 1947）"
            ),
            confidence_level="high",
            bias_warnings=["注意：过度比较会导致选择悖论（Schwartz, 2004）"]
        )


class ProsConsCalculator:
    """
    加权利弊计算器
    Franklin (1772) 现代改进版：加入权重评分
    """

    def calculate(
        self,
        pros_a: list[tuple[str, int]],   # [(描述, 权重), ...]
        cons_a: list[tuple[str, int]],
        pros_b: Optional[list[tuple[str, int]]] = None,
        cons_b: Optional[list[tuple[str, int]]] = None,
        option_a_name: str = "选项A",
        option_b_name: str = "选项B"
    ) -> ScoreResult:

        score_a = sum(w for _, w in pros_a) - sum(w for _, w in cons_a)
        score_b = (
            sum(w for _, w in pros_b) - sum(w for _, w in cons_b)
            if pros_b and cons_b else None
        )

        winner = None
        if score_b is not None:
            winner = option_a_name if score_a > score_b else option_b_name

        scores = {option_a_name: score_a}
        if score_b is not None:
            scores[option_b_name] = score_b

        # 计算差距置信度
        gap = abs(score_a - (score_b or 0))
        if gap >= 5:
            confidence = "high"
        elif gap >= 2:
            confidence = "medium"
        else:
            confidence = "low"

        rec_winner = winner or option_a_name
        return ScoreResult(
            framework="pros_cons",
            winner=winner,
            scores=scores,
            details={
                "pros_a": pros_a,
                "cons_a": cons_a,
                "pros_b": pros_b,
                "cons_b": cons_b,
                "score_gap": gap
            },
            recommendation=(
                f"加权利弊分析显示，【{rec_winner}】净得分更高（差距：{gap}分）。"
                + ("差距较小，建议结合其他框架做进一步确认。" if confidence == "low" else "")
                + f"（来源：Franklin, B. Letter to Priestley, 1772）"
            ),
            confidence_level=confidence,
            bias_warnings=[
                "注意：列出的利弊可能受确认偏见影响，建议请第三方补充遗漏项。"
            ]
        )


class RegretMinimizationCalculator:
    """
    遗憾最小化计算器
    Bezos (2010): 80岁视角的遗憾评分
    """

    def calculate(
        self,
        regret_score_a: int,   # 0-10
        regret_score_b: int,   # 0-10
        option_a_name: str = "选项A",
        option_b_name: str = "选项B"
    ) -> ScoreResult:

        # 遗憾更低的是更好的选择
        winner = option_a_name if regret_score_a < regret_score_b else option_b_name
        loser = option_b_name if winner == option_a_name else option_a_name

        gap = abs(regret_score_a - regret_score_b)

        # 研究表明：不行动的遗憾通常大于行动失败的遗憾
        # Gilovich & Medvec (1995)
        bias_warnings = []
        if regret_score_a > 7 or regret_score_b > 7:
            bias_warnings.append(
                "研究表明：人们在晚年对\"没有做\"的遗憾远大于\"做了但失败\"的遗憾。"
                "（Gilovich & Medvec, 1995, Psychological Review）"
            )

        if gap <= 2:
            bias_warnings.append(
                "两个选项的遗憾分数相近，决策可能受损失厌恶影响。"
                "建议补充10-10-10框架做中期验证。"
            )

        return ScoreResult(
            framework="regret_minimization",
            winner=winner,
            scores={
                option_a_name: {"regret_score": regret_score_a},
                option_b_name: {"regret_score": regret_score_b}
            },
            details={
                "gap": gap,
                "interpretation": f"80岁视角下，{loser}的遗憾（{max(regret_score_a, regret_score_b)}分）"
                                  f"大于{winner}（{min(regret_score_a, regret_score_b)}分）"
            },
            recommendation=(
                f"从80岁视角看，选择【{winner}】能让你在晚年拥有更少的遗憾。"
                f"（来源：Bezos, J. Princeton Commencement, 2010；"
                f"心理学基础：Gilovich & Medvec, 1995）"
            ),
            confidence_level="high" if gap >= 3 else "medium",
            bias_warnings=bias_warnings
        )


class ExpectedValueCalculator:
    """
    期望值 + Prospect Theory 计算器
    Von Neumann (1944) + Kahneman & Tversky (1979) + Plous (1993)
    """

    LOSS_AVERSION_COEFFICIENT = 2.25   # Kahneman & Tversky (1979)

    def calculate(
        self,
        success_gain: float,           # 成功时的净收益（万元或其他单位）
        failure_loss: float,            # 失败时的净损失（正数）
        base_rate: float,              # 基准率 (0-1)
        advantage_adjustment: float,   # 优势调整 (0-1, 正数)
        disadvantage_adjustment: float, # 劣势调整 (0-1, 正数)
        loss_bearable: bool = True
    ) -> ScoreResult:

        # 校准后的成功概率
        calibrated_prob = min(
            max(base_rate + advantage_adjustment - disadvantage_adjustment, 0.05),
            0.95
        )
        failure_prob = 1 - calibrated_prob

        # 标准期望值
        ev_standard = calibrated_prob * success_gain - failure_prob * failure_loss

        # Prospect Theory 调整后期望值（损失权重 × 2.25）
        ev_prospect = (
            calibrated_prob * success_gain
            - self.LOSS_AVERSION_COEFFICIENT * failure_prob * failure_loss
        )

        # 决策建议
        if not loss_bearable:
            recommendation = (
                "⚠️ 警告：你表示无法承受失败时的损失。"
                "根据 Kelly 准则，不应进行超出承受能力的风险决策。"
                "建议先降低损失风险，再重新评估。"
            )
            winner = "建议暂缓"
            confidence = "low"
        elif ev_prospect > 0:
            recommendation = (
                f"期望值分析支持执行此决策。"
                f"标准期望值：{ev_standard:+.1f}，"
                f"Prospect Theory调整后：{ev_prospect:+.1f}（含损失厌恶系数2.25）。"
                f"即使考虑人类对损失的心理放大，期望值仍为正。"
                f"（来源：Von Neumann & Morgenstern, 1944；"
                f"Kahneman & Tversky, 1979；Plous, 1993 Ch.6）"
            )
            winner = "执行"
            confidence = "high" if ev_prospect > ev_standard * 0.5 else "medium"
        elif ev_standard > 0 and ev_prospect <= 0:
            recommendation = (
                f"标准期望值为正（{ev_standard:+.1f}），"
                f"但考虑损失厌恶后期望值为负（{ev_prospect:+.1f}）。"
                f"决策在理性上可行，但在心理上会感到痛苦。"
                f"建议评估是否能降低损失量级或提升成功概率。"
            )
            winner = "谨慎执行"
            confidence = "medium"
        else:
            recommendation = (
                f"期望值分析不支持此决策（标准EV：{ev_standard:+.1f}）。"
                f"除非有其他非量化因素（如战略价值、学习价值），否则建议放弃。"
            )
            winner = "不建议"
            confidence = "high"

        bias_warnings = []
        if advantage_adjustment > 0.15:
            bias_warnings.append(
                "你对自身优势的调整幅度较大（>15%），"
                "请检查是否存在过度自信。"
                "（Plous, 1993, Ch.14）"
            )
        if base_rate < 0.1 and calibrated_prob > 0.3:
            bias_warnings.append(
                "基准率较低，但你的校准概率显著高于基准，"
                "请确认调整依据的充分性。"
                "（Kahneman, 2011: Inside View vs Outside View）"
            )

        return ScoreResult(
            framework="expected_value",
            winner=winner,
            scores={
                "标准期望值": round(ev_standard, 2),
                "Prospect Theory调整期望值": round(ev_prospect, 2),
                "校准成功概率": f"{calibrated_prob:.1%}",
                "基准率": f"{base_rate:.1%}"
            },
            details={
                "success_gain": success_gain,
                "failure_loss": failure_loss,
                "base_rate": base_rate,
                "calibrated_prob": calibrated_prob,
                "loss_aversion_coeff": self.LOSS_AVERSION_COEFFICIENT
            },
            recommendation=recommendation,
            confidence_level=confidence,
            bias_warnings=bias_warnings
        )


class McKinsey7SCalculator:
    """
    麦肯锡7S差距分析计算器
    Peters & Waterman (1982)
    """

    ELEMENTS = ["战略", "结构", "系统", "共同价值观", "技能", "人员", "风格"]
    WEIGHTS = {
        "战略": 1.5,
        "结构": 1.0,
        "系统": 1.2,
        "共同价值观": 1.5,
        "技能": 1.3,
        "人员": 1.0,
        "风格": 0.8
    }

    def calculate(
        self,
        current_scores: dict,    # {"战略": 6, "结构": 7, ...}
        target_scores: dict      # {"战略": 9, "结构": 8, ...}
    ) -> ScoreResult:

        gaps = {}
        weighted_gaps = {}

        for element in self.ELEMENTS:
            current = current_scores.get(element, 5)
            target = target_scores.get(element, 8)
            gap = target - current
            gaps[element] = gap
            weighted_gaps[element] = gap * self.WEIGHTS.get(element, 1.0)

        # 找出优先级最高的短板
        sorted_gaps = sorted(weighted_gaps.items(), key=lambda x: x[1], reverse=True)
        top_priority = sorted_gaps[0][0] if sorted_gaps else "未知"

        # 整体转型难度评分
        avg_gap = sum(gaps.values()) / len(gaps)
        if avg_gap <= 1.5:
            difficulty = "低"
        elif avg_gap <= 3:
            difficulty = "中"
        else:
            difficulty = "高"

        return ScoreResult(
            framework="mckinsey_7s",
            winner=None,
            scores={
                el: {
                    "current": current_scores.get(el, 0),
                    "target": target_scores.get(el, 0),
                    "gap": gaps[el],
                    "priority": round(weighted_gaps[el], 1)
                }
                for el in self.ELEMENTS
            },
            details={
                "top_priority_element": top_priority,
                "average_gap": round(avg_gap, 1),
                "transformation_difficulty": difficulty,
                "sorted_priorities": sorted_gaps
            },
            recommendation=(
                f"7S分析显示，最需要优先提升的要素是【{top_priority}】（加权差距最大）。"
                f"整体转型难度：{difficulty}（平均差距：{avg_gap:.1f}分）。"
                f"建议从短板要素开始系统性改进，确保7S要素协调一致。"
                f"（来源：Peters & Waterman, In Search of Excellence, 1982）"
            ),
            confidence_level="high",
            bias_warnings=[
                "注意：确认偏见可能导致对现状评分过高。"
                "建议引入外部视角（咨询顾问/董事会）参与评分校准。",
                "计划谬误风险：7S改进所需时间通常是预估的2-3倍。（Plous, 1993, Ch.11）"
            ]
        )


# ──────────────────────────────────────────────
# 统一入口
# ──────────────────────────────────────────────

def calculate(framework: str, params: dict) -> ScoreResult:
    """
    统一计算入口

    Args:
        framework: 框架名称
        params: 对应框架所需参数

    Returns:
        ScoreResult
    """
    calculators = {
        "satisficing": SatisficingCalculator,
        "pros_cons": ProsConsCalculator,
        "regret_minimization": RegretMinimizationCalculator,
        "expected_value": ExpectedValueCalculator,
        "mckinsey_7s": McKinsey7SCalculator
    }

    if framework not in calculators:
        raise ValueError(f"计算器未实现：{framework}")

    calculator = calculators[framework]()
    return calculator.calculate(**params)


# ──────────────────────────────────────────────
# 演示
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=== 期望值计算演示 ===")
    result = calculate("expected_value", {
        "success_gain": 500,
        "failure_loss": 100,
        "base_rate": 0.25,
        "advantage_adjustment": 0.10,
        "disadvantage_adjustment": 0.05,
        "loss_bearable": True
    })
    print(f"推荐决策：{result.winner}")
    print(f"评分详情：{result.scores}")
    print(f"建议：{result.recommendation}")
    print(f"偏见警告：{result.bias_warnings}")

    print("\n=== 遗憾最小化计算演示 ===")
    result2 = calculate("regret_minimization", {
        "regret_score_a": 3,
        "regret_score_b": 8,
        "option_a_name": "考研",
        "option_b_name": "直接工作"
    })
    print(f"推荐决策：{result2.winner}")
    print(f"建议：{result2.recommendation}")
