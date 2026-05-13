"""
交互式信息收集器

根据选定的决策框架，动态生成问题序列并收集用户输入
"""

from dataclasses import dataclass, field
from typing import Optional, Callable
import json


# ──────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────

@dataclass
class Question:
    id: str
    text: str
    input_type: str          # text | number | choice | scale | multichoice
    options: list[str] = field(default_factory=list)
    scale_range: tuple = (1, 10)
    hint: str = ""
    required: bool = True
    depends_on: Optional[str] = None    # 条件触发：依赖某个问题的答案
    depends_value: Optional[str] = None


@dataclass
class CollectionSession:
    framework: str
    questions: list[Question]
    answers: dict = field(default_factory=dict)
    current_index: int = 0
    completed: bool = False


# ──────────────────────────────────────────────
# 框架问题库
# ──────────────────────────────────────────────

FRAMEWORK_QUESTIONS: dict[str, list[Question]] = {

    "satisficing": [
        Question(
            id="problem",
            text="请描述你需要做的决定是什么？",
            input_type="text",
            hint="例如：今天午饭吃什么"
        ),
        Question(
            id="options",
            text="你目前能想到的选项有哪些？（列出3-5个即可）",
            input_type="text",
            hint="用逗号分隔，例如：沙县小吃, 麦当劳, 附近的火锅店"
        ),
        Question(
            id="threshold_1",
            text="你的第一个底线要求是什么？（必须满足的条件）",
            input_type="text",
            hint="例如：步行10分钟内"
        ),
        Question(
            id="threshold_2",
            text="还有其他底线要求吗？",
            input_type="text",
            hint="例如：价格低于50元（没有可以跳过）"
        ),
        Question(
            id="time_limit",
            text="你有多长时间做这个决定？",
            input_type="choice",
            options=["5分钟内", "今天内", "本周内", "不紧急"]
        )
    ],

    "10_10_10": [
        Question(
            id="decision",
            text="你面临的决定是什么？请简要描述。",
            input_type="text"
        ),
        Question(
            id="option_a",
            text="选项A是什么？",
            input_type="text"
        ),
        Question(
            id="option_b",
            text="选项B是什么？",
            input_type="text"
        ),
        Question(
            id="10min_a",
            text="如果选择选项A，10分钟后你的感受是什么？",
            input_type="text",
            hint="关注即时情绪：开心、焦虑、后悔、释然……"
        ),
        Question(
            id="10min_b",
            text="如果选择选项B，10分钟后你的感受是什么？",
            input_type="text"
        ),
        Question(
            id="10month_a",
            text="选择选项A，10个月后你的生活/工作会有什么变化？",
            input_type="text"
        ),
        Question(
            id="10month_b",
            text="选择选项B，10个月后会有什么变化？",
            input_type="text"
        ),
        Question(
            id="10year_a",
            text="10年后回头看，选择了选项A的你会是什么状态？",
            input_type="text",
            hint="与你理想中的自己相比，是否一致？"
        ),
        Question(
            id="10year_b",
            text="10年后回头看，选择了选项B的你会是什么状态？",
            input_type="text"
        )
    ],

    "regret_minimization": [
        Question(
            id="decision",
            text="你面临的人生决定是什么？",
            input_type="text"
        ),
        Question(
            id="option_a",
            text="选项A是什么？",
            input_type="text"
        ),
        Question(
            id="option_b",
            text="选项B是什么？",
            input_type="text"
        ),
        Question(
            id="age_80_a",
            text="想象你已经80岁，坐在摇椅上回顾一生。\n你选择了【选项A】，你的感受是什么？",
            input_type="text",
            hint="尽量具体描述那时的生活状态"
        ),
        Question(
            id="regret_score_a",
            text="80岁的你，对选择了A的遗憾程度是多少？",
            input_type="scale",
            scale_range=(0, 10),
            hint="0=没有遗憾，10=极度遗憾"
        ),
        Question(
            id="age_80_b",
            text="同样是80岁，你选择了【选项B】，你的感受是什么？",
            input_type="text"
        ),
        Question(
            id="regret_score_b",
            text="80岁的你，对选择了B的遗憾程度是多少？",
            input_type="scale",
            scale_range=(0, 10)
        ),
        Question(
            id="worse_regret",
            text="这两种遗憾中，哪种你更难以接受？",
            input_type="choice",
            options=["选项A的遗憾更难接受", "选项B的遗憾更难接受", "差不多"]
        )
    ],

    "pros_cons": [
        Question(
            id="decision",
            text="你在考虑的决定是什么？",
            input_type="text"
        ),
        Question(
            id="option_a",
            text="选项A是什么？",
            input_type="text"
        ),
        Question(
            id="pros_a",
            text="选择【选项A】的好处/优势有哪些？",
            input_type="text",
            hint="尽量列出所有能想到的，用逗号分隔"
        ),
        Question(
            id="cons_a",
            text="选择【选项A】的坏处/风险有哪些？",
            input_type="text",
            hint="同样尽量列出所有的"
        ),
        Question(
            id="option_b",
            text="选项B是什么？（如有）",
            input_type="text",
            required=False
        ),
        Question(
            id="pros_b",
            text="选择【选项B】的好处有哪些？",
            input_type="text",
            required=False
        ),
        Question(
            id="cons_b",
            text="选择【选项B】的坏处/风险有哪些？",
            input_type="text",
            required=False
        ),
        Question(
            id="most_important",
            text="在所有的利弊条目中，哪3条对你来说最重要？",
            input_type="text",
            hint="这些会在评分中获得更高权重"
        )
    ],

    "values_matrix": [
        Question(
            id="decision",
            text="你面临的决定是什么？",
            input_type="text"
        ),
        Question(
            id="core_values",
            text="在你的人生中，以下哪些价值观最重要？（选3-5个）",
            input_type="multichoice",
            options=[
                "成就与认可",
                "稳定与安全",
                "自由与探索",
                "家庭与亲密关系",
                "社会影响力",
                "财务自由",
                "意义与贡献",
                "健康与快乐",
                "学习与成长"
            ]
        ),
        Question(
            id="values_rank",
            text="请为你选择的价值观排序（最重要的排第1）",
            input_type="text",
            hint="例如：1.学习与成长 2.自由与探索 3.财务自由"
        ),
        Question(
            id="option_a",
            text="选项A是什么？",
            input_type="text"
        ),
        Question(
            id="option_b",
            text="选项B是什么？",
            input_type="text"
        ),
        Question(
            id="values_score_a",
            text="选项A对你最重要的价值观满足程度如何？",
            input_type="scale",
            scale_range=(1, 5),
            hint="1=完全不满足，5=完全满足。请为每个价值观分别打分"
        ),
        Question(
            id="values_score_b",
            text="选项B对同样的价值观满足程度如何？",
            input_type="scale",
            scale_range=(1, 5)
        )
    ],

    "expected_value": [
        Question(
            id="decision",
            text="你评估的决策/项目是什么？",
            input_type="text"
        ),
        Question(
            id="success_scenario",
            text="如果成功，你会得到什么？（尽量量化）",
            input_type="text",
            hint="例如：年收入增加50万，市场份额达到10%"
        ),
        Question(
            id="failure_scenario",
            text="如果失败，你会损失什么？（尽量量化）",
            input_type="text",
            hint="例如：损失100万投资，3年时间成本"
        ),
        Question(
            id="base_rate",
            text="同类项目/决策的历史成功率大约是多少？",
            input_type="text",
            hint="这是基准率，不是你的主观判断。如不确定，我们可以一起估算"
        ),
        Question(
            id="advantage_factors",
            text="与同类项目相比，你有哪些优势让你高于平均成功率？",
            input_type="text",
            hint="每个因素大约提升多少个百分点？"
        ),
        Question(
            id="disadvantage_factors",
            text="与同类项目相比，你有哪些劣势让你低于平均？",
            input_type="text"
        ),
        Question(
            id="loss_bearable",
            text="如果发生最坏情况（完全失败），你能承受这个损失吗？",
            input_type="choice",
            options=["完全能承受，不影响生活", "勉强能承受，会很困难", "无法承受"]
        ),
        Question(
            id="time_horizon",
            text="这个决策的时间周期是多长？",
            input_type="choice",
            options=["1年内", "1-3年", "3-5年", "5年以上"]
        )
    ],

    "mckinsey_7s": [
        Question(
            id="context",
            text="请简要描述公司当前面临的战略决策或挑战。",
            input_type="text"
        ),
        Question(
            id="strategy_current",
            text="【战略】公司当前的竞争战略是什么？（当前状态1-10分）",
            input_type="scale",
            scale_range=(1, 10),
            hint="1=完全没有清晰战略，10=战略极其清晰且有竞争力"
        ),
        Question(
            id="structure_current",
            text="【结构】现有组织架构是否支持战略执行？（当前状态1-10分）",
            input_type="scale",
            scale_range=(1, 10)
        ),
        Question(
            id="systems_current",
            text="【系统】业务流程和信息系统是否完善？（1-10分）",
            input_type="scale",
            scale_range=(1, 10)
        ),
        Question(
            id="shared_values",
            text="【共同价值观】员工认同的核心文化是什么？（1-10分）",
            input_type="scale",
            scale_range=(1, 10)
        ),
        Question(
            id="skills_current",
            text="【技能】组织核心能力是否匹配战略需求？（1-10分）",
            input_type="scale",
            scale_range=(1, 10)
        ),
        Question(
            id="staff_current",
            text="【人员】团队构成是否满足战略执行需求？（1-10分）",
            input_type="scale",
            scale_range=(1, 10)
        ),
        Question(
            id="style_current",
            text="【风格】领导层的管理风格是否适合当前战略方向？（1-10分）",
            input_type="scale",
            scale_range=(1, 10)
        ),
        Question(
            id="target_state",
            text="战略执行成功后，以上7个要素的目标状态分别是多少分？",
            input_type="text",
            hint="格式：战略9, 结构8, 系统9, 价值观8, 技能9, 人员8, 风格7"
        )
    ],

    "scenario_planning": [
        Question(
            id="context",
            text="请描述你们面临的战略决策和时间范围。",
            input_type="text"
        ),
        Question(
            id="uncertainty_1",
            text="影响这个决策的最关键的不确定因素是什么？（第1个）",
            input_type="text",
            hint="例如：AI技术的普及速度"
        ),
        Question(
            id="uncertainty_2",
            text="第2个关键不确定因素是什么？",
            input_type="text",
            hint="例如：监管政策的宽松或收紧"
        ),
        Question(
            id="scenario_1",
            text="情景1（因素1高 × 因素2高）：描述这种世界会是什么样子？",
            input_type="text"
        ),
        Question(
            id="scenario_2",
            text="情景2（因素1高 × 因素2低）：描述这种世界？",
            input_type="text"
        ),
        Question(
            id="scenario_3",
            text="情景3（因素1低 × 因素2高）：描述这种世界？",
            input_type="text"
        ),
        Question(
            id="scenario_4",
            text="情景4（因素1低 × 因素2低）：描述这种世界？",
            input_type="text"
        ),
        Question(
            id="prob_distribution",
            text="你认为4个情景的发生概率分别是多少？（总和=100%）",
            input_type="text",
            hint="例如：情景1: 30%, 情景2: 20%, 情景3: 30%, 情景4: 20%"
        ),
        Question(
            id="early_signals",
            text="哪些早期信号可以告诉你，现实在向哪个情景发展？",
            input_type="text"
        )
    ]
}


# ──────────────────────────────────────────────
# 收集器核心逻辑
# ──────────────────────────────────────────────

class InteractiveCollector:

    def __init__(self, framework: str):
        if framework not in FRAMEWORK_QUESTIONS:
            raise ValueError(f"未知框架：{framework}。可用框架：{list(FRAMEWORK_QUESTIONS.keys())}")
        self.session = CollectionSession(
            framework=framework,
            questions=FRAMEWORK_QUESTIONS[framework]
        )

    def get_next_question(self) -> Optional[Question]:
        """获取下一个待回答的问题"""
        while self.session.current_index < len(self.session.questions):
            q = self.session.questions[self.session.current_index]
            
            # 检查条件依赖
            if q.depends_on and q.depends_on in self.session.answers:
                if self.session.answers[q.depends_on] != q.depends_value:
                    self.session.current_index += 1
                    continue
            
            # 跳过非必填且用户已选择跳过
            return q
        
        self.session.completed = True
        return None

    def submit_answer(self, question_id: str, answer) -> dict:
        """提交一个问题的回答"""
        self.session.answers[question_id] = answer
        self.session.current_index += 1
        
        next_q = self.get_next_question()
        
        return {
            "submitted": question_id,
            "next_question": next_q,
            "progress": self._get_progress(),
            "completed": self.session.completed
        }

    def _get_progress(self) -> dict:
        total = len(self.session.questions)
        done = len(self.session.answers)
        return {
            "total": total,
            "completed": done,
            "percentage": round(done / total * 100)
        }

    def get_all_answers(self) -> dict:
        """获取所有已收集的答案"""
        return {
            "framework": self.session.framework,
            "answers": self.session.answers,
            "completed": self.session.completed
        }

    def format_current_question(self, question: Question) -> str:
        """格式化当前问题，用于展示"""
        progress = self._get_progress()
        output = f"\n[{progress['completed'] + 1}/{progress['total']}] {question.text}"
        
        if question.hint:
            output += f"\n  💡 {question.hint}"
        
        if question.input_type == "choice":
            for i, opt in enumerate(question.options):
                output += f"\n  {i+1}. {opt}"
        elif question.input_type == "multichoice":
            for i, opt in enumerate(question.options):
                output += f"\n  {chr(65+i)}. {opt}"
        elif question.input_type == "scale":
            lo, hi = question.scale_range
            output += f"\n  （{lo} = 最低，{hi} = 最高）"
        
        if not question.required:
            output += "\n  （可跳过，直接按回车）"
        
        return output


# ──────────────────────────────────────────────
# 命令行交互演示
# ──────────────────────────────────────────────

def run_interactive_session(framework: str):
    """运行一个完整的交互式收集会话（命令行演示）"""
    collector = InteractiveCollector(framework)
    print(f"\n🎯 启动框架：{framework}")
    print("─" * 50)
    
    while True:
        question = collector.get_next_question()
        if question is None:
            break
        
        print(collector.format_current_question(question))
        answer = input("\n你的回答：").strip()
        
        if not answer and not question.required:
            answer = None
        
        result = collector.submit_answer(question.id, answer)
        print(f"  ✓ 已记录（进度 {result['progress']['percentage']}%）")
    
    print("\n✅ 信息收集完成")
    print("\n收集结果：")
    print(json.dumps(collector.get_all_answers(), ensure_ascii=False, indent=2))
    return collector.get_all_answers()


if __name__ == "__main__":
    run_interactive_session("regret_minimization")
