"""
决策树 + 结构化报告渲染器

将计算结果转化为多种可视化输出格式
"""

from dataclasses import dataclass
from typing import Optional
import sys
import os

# 添加当前目录到路径，以便导入 score_calculator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from score_calculator import ScoreResult
except ImportError:
    # 如果无法导入，定义一个简单的替代类
    @dataclass
    class ScoreResult:
        framework: str
        winner: Optional[str]
        scores: dict
        details: dict
        recommendation: str
        confidence_level: str
        bias_warnings: list[str]


# ──────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────

@dataclass
class TreeNode:
    label: str
    value: Optional[str] = None
    score: Optional[float] = None
    children: list = None
    is_winner: bool = False
    note: str = ""

    def __post_init__(self):
        if self.children is None:
            self.children = []


# ──────────────────────────────────────────────
# 渲染器
# ──────────────────────────────────────────────

class DecisionTreeRenderer:
    """将决策结果渲染为 Markdown 决策树"""

    def render(self, result: ScoreResult, context: dict) -> str:
        """主渲染入口，根据框架类型选择渲染方式"""
        renderers = {
            "satisficing": self._render_satisficing,
            "10_10_10": self._render_10_10_10,
            "regret_minimization": self._render_regret,
            "pros_cons": self._render_pros_cons,
            "values_matrix": self._render_values_matrix,
            "expected_value": self._render_expected_value,
            "mckinsey_7s": self._render_7s,
            "scenario_planning": self._render_scenario
        }

        renderer = renderers.get(result.framework, self._render_generic)
        return renderer(result, context)

    def _render_header(self, title: str, framework_ref: str) -> str:
        return (
            f"# 🎯 决策分析报告\n\n"
            f"**分析框架**：{title}  \n"
            f"**文献出处**：{framework_ref}\n\n"
            f"---\n\n"
        )

    def _render_bias_section(self, bias_warnings: list[str]) -> str:
        if not bias_warnings:
            return ""

        lines = ["## ⚠️ 认知偏见提示\n"]
        for warning in bias_warnings:
            lines.append(f"- {warning}\n")

        lines.append("\n")
        return "".join(lines)

    def _render_recommendation_section(self, recommendation: str, winner: str, confidence: str) -> str:
        winner_str = f"\n\n**推荐选择**：{winner}" if winner else ""
        confidence_str = f"\n\n**置信度**：{confidence}" if confidence else ""

        return (
            f"## 💡 推荐建议\n\n"
            f"{recommendation}"
            f"{winner_str}"
            f"{confidence_str}\n\n"
        )

    def _render_generic(self, result: ScoreResult, context: dict) -> str:
        """通用渲染器"""
        content = self._render_header(result.framework, "参见各框架文献")

        content += "## 📊 评分详情\n\n"
        for key, value in result.scores.items():
            content += f"- **{key}**：{value}\n"
        content += "\n"

        content += self._render_recommendation_section(result.recommendation, result.winner, result.confidence_level)
        content += self._render_bias_section(result.bias_warnings)

        return content

    def _render_satisficing(self, result: ScoreResult, context: dict) -> str:
        """满意解渲染器"""
        content = self._render_header("满意解理论", "Simon, H. (1947). Administrative Behavior")

        content += "## 🎯 满意解分析\n\n"

        thresholds = result.details.get("thresholds", [])
        if thresholds:
            content += "### 设定的阈值标准\n\n"
            for thresh in thresholds:
                if thresh:
                    content += f"- [x] {thresh}\n"
            content += "\n"

        content += "### 选项检验结果\n\n"
        for option, status in result.scores.items():
            mark = "✅" if "候选" in status else "🔄"
            content += f"{mark} **{option}**：{status}\n"

        content += "\n"

        content += self._render_recommendation_section(result.recommendation, result.winner, result.confidence_level)
        content += self._render_bias_section(result.bias_warnings)

        return content

    def _render_pros_cons(self, result: ScoreResult, context: dict) -> str:
        """利弊分析渲染器"""
        content = self._render_header("加权利弊清单法", "Franklin, B. (1772). Letter to Joseph Priestley")

        content += "## 📊 利弊对比\n\n"

        pros_a = result.details.get("pros_a", [])
        cons_a = result.details.get("cons_a", [])
        pros_b = result.details.get("pros_b", [])
        cons_b = result.details.get("cons_b", [])

        # 选项A
        content += "### 选项A\n\n"
        if pros_a:
            content += "**优势**：\n"
            for desc, weight in pros_a:
                content += f"- {desc} (+{weight})\n"
        if cons_a:
            content += "\n**劣势**：\n"
            for desc, weight in cons_a:
                content += f"- {desc} (-{weight})\n"
        content += f"\n**净得分**：{result.scores.get('选项A', 0)}\n\n"

        # 选项B（如果存在）
        if pros_b or cons_b:
            content += "---\n\n### 选项B\n\n"
            if pros_b:
                content += "**优势**：\n"
                for desc, weight in pros_b:
                    content += f"- {desc} (+{weight})\n"
            if cons_b:
                content += "\n**劣势**：\n"
                for desc, weight in cons_b:
                    content += f"- {desc} (-{weight})\n"
            content += f"\n**净得分**：{result.scores.get('选项B', 0)}\n\n"

        content += self._render_recommendation_section(result.recommendation, result.winner, result.confidence_level)
        content += self._render_bias_section(result.bias_warnings)

        return content

    def _render_regret(self, result: ScoreResult, context: dict) -> str:
        """遗憾最小化渲染器"""
        content = self._render_header("遗憾最小化框架", "Bezos, J. (2010). Princeton Commencement Address")

        content += "## 👴 80岁视角分析\n\n"

        # 绘制简单的决策树
        content += "```mermaid\ngraph TD\n    A[面临决策] --> B[选择A]\n    A --> C[选择B]\n    B --> D[80岁视角]\n    C --> D\n    D --> E{遗憾程度}\n```\n\n"

        content += "### 遗憾评分\n\n"
        scores = result.scores
        for option, data in scores.items():
            regret = data.get("regret_score", 0)
            bars = "█" * int(regret) + "░" * (10 - int(regret))
            content += f"- **{option}**：{bars} ({regret}/10)\n"
        content += "\n"

        interpretation = result.details.get("interpretation", "")
        if interpretation:
            content += f"### 解读\n\n{interpretation}\n\n"

        content += self._render_recommendation_section(result.recommendation, result.winner, result.confidence_level)
        content += self._render_bias_section(result.bias_warnings)

        return content

    def _render_expected_value(self, result: ScoreResult, context: dict) -> str:
        """期望值渲染器"""
        content = self._render_header("期望值模型 + Prospect Theory", 
                                      "Von Neumann & Morgenstern (1944); Kahneman & Tversky (1979)")

        content += "## 📈 期望值分析\n\n"

        content += "### 核心指标\n\n"
        scores = result.scores
        for key, value in scores.items():
            content += f"- **{key}**：{value}\n"
        content += "\n"

        # 绘制期望损益图
        details = result.details
        if details:
            content += "### 损益情况\n\n"
            success_gain = details.get("success_gain", 0)
            failure_loss = details.get("failure_loss", 0)
            calibrated_prob = details.get("calibrated_prob", 0.5)

            content += (
                f"- 成功收益：+{success_gain}\n"
                f"- 失败损失：-{failure_loss}\n"
                f"- 成功概率：{calibrated_prob:.1%}\n\n"
            )

            # 简单的决策树
            content += "```mermaid\ngraph TD\n    A[执行决策] --> B{成功?}\n    B -->|是| C[+{success_gain}]\n    B -->|否| D[-{failure_loss}]\n```\n\n"

        content += self._render_recommendation_section(result.recommendation, result.winner, result.confidence_level)
        content += self._render_bias_section(result.bias_warnings)

        return content

    def _render_7s(self, result: ScoreResult, context: dict) -> str:
        """7S渲染器"""
        content = self._render_header("麦肯锡7S框架", "Peters & Waterman (1982). In Search of Excellence")

        content += "## 🏢 7S要素分析\n\n"

        scores = result.scores
        content += "| 要素 | 现状 | 目标 | 差距 | 优先级 |\n"
        content += "|------|------|------|------|--------|\n"

        elements = ["战略", "结构", "系统", "共同价值观", "技能", "人员", "风格"]
        for element in elements:
            if element in scores:
                data = scores[element]
                current = data.get("current", 0)
                target = data.get("target", 0)
                gap = data.get("gap", 0)
                priority = data.get("priority", 0)

                gap_str = f"+{gap}" if gap > 0 else str(gap)
                content += f"| {element} | {current}/10 | {target}/10 | {gap_str} | {priority} |\n"

        content += "\n"

        details = result.details
        if details:
            top_priority = details.get("top_priority_element", "")
            difficulty = details.get("transformation_difficulty", "")
            avg_gap = details.get("average_gap", 0)

            content += f"### 关键发现\n\n"
            content += f"- **最优先改进**：{top_priority}\n"
            content += f"- **转型难度**：{difficulty}\n"
            content += f"- **平均差距**：{avg_gap:.1f}分\n\n"

            # 优先级排序
            sorted_priorities = details.get("sorted_priorities", [])
            if sorted_priorities:
                content += "### 改进优先级排序\n\n"
                for elem, weight in sorted_priorities:
                    content += f"1. {elem} (加权差距：{weight:.1f})\n"
                content += "\n"

        content += self._render_recommendation_section(result.recommendation, result.winner, result.confidence_level)
        content += self._render_bias_section(result.bias_warnings)

        return content

    def _render_10_10_10(self, result: ScoreResult, context: dict) -> str:
        """10-10-10渲染器"""
        content = self._render_header("10-10-10时间维度法", "Welch, S. (2009). 10-10-10: A Life-Transforming Idea")

        content += "## ⏱️ 时间维度分析\n\n"

        content += (
            "| 时间点 | 选项A | 选项B |\n"
            "|--------|-------|-------|\n"
            "| 10分钟后 | - | - |\n"
            "| 10个月后 | - | - |\n"
            "| 10年后 | - | - |\n\n"
        )

        content += self._render_recommendation_section(result.recommendation, result.winner, result.confidence_level)
        content += self._render_bias_section(result.bias_warnings)

        return content

    def _render_values_matrix(self, result: ScoreResult, context: dict) -> str:
        """价值观矩阵渲染器"""
        content = self._render_header("价值观矩阵", "Covey, S. (1989); Schwartz, S. (1992)")

        content += "## 🌟 价值观对齐分析\n\n"
        content += self._render_recommendation_section(result.recommendation, result.winner, result.confidence_level)
        content += self._render_bias_section(result.bias_warnings)

        return content

    def _render_scenario(self, result: ScoreResult, context: dict) -> str:
        """情景规划渲染器"""
        content = self._render_header("情景规划法", "Shell (1970s); Schwartz, P. (1991)")

        content += "## 🎭 情景分析\n\n"
        content += self._render_recommendation_section(result.recommendation, result.winner, result.confidence_level)
        content += self._render_bias_section(result.bias_warnings)

        return content


# ──────────────────────────────────────────────
# 演示
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=== 决策树渲染器 ===")
    print("可用于生成 Markdown 格式的决策分析报告")
