# 意图识别 → 框架路由映射表

## 分类规则

### 关键词触发器

| 场景类型 | 触发关键词/语义 | 优先框架 | 备选框架 |
|---------|--------------|---------|---------|
| daily_life | 吃什么、去哪、买哪个、今天、要不要 | satisficing | 10_10_10, random_weighted |
| career | 考研、深造、留学、跳槽、转行、辞职、创业、婚姻、结婚、要不要去、职业、工作、升职、继续还是、是否应该 | regret_minimization | pros_cons, values_matrix, 10_10_10 |
| venture | 创业、投资、可行性、成功率、概率、值不值得、风险、回报、收益、融资、产品、市场、机会 | expected_value | base_rate, scenario_planning |
| strategy | 战略、竞争、转型、扩张、市场进入、公司决策、风险评估、业务、战略规划、组织、并购、布局 | mckinsey_7s | swot, scenario_planning, expected_value |

### 复杂度判断规则

LOW:
  - 影响范围：个人 + 短期
  - 可逆程度：高（可以反悔）
  - 示例：吃什么、买哪件衣服

MEDIUM:
  - 影响范围：个人/小团队 + 中期
  - 可逆程度：中
  - 示例：要不要跳槽、选哪个产品方向

HIGH:
  - 影响范围：组织/人生 + 长期
  - 可逆程度：低（难以逆转）
  - 示例：公司战略转型、是否考研、创业方向

### 偏见风险预判

status_quo_bias（现状偏见）:
  - 触发：用户描述中包含"一直在"、"习惯了"、"不想改变"

loss_aversion（损失厌恶）:
  - 触发：用户过度强调"风险"、"万一失败"、"损失"

overconfidence（过度自信）:
  - 触发：用户使用"肯定"、"一定"、"没问题"

sunk_cost_fallacy（沉没成本谬误）:
  - 触发：用户提到"已经投入"、"花了这么多"

availability_heuristic（可得性启发）:
  - 触发：用户以身边案例作为主要判断依据

planning_fallacy（计划谬误）:
  - 触发：用户低估时间/资源/风险

anchoring（锚定效应）:
  - 触发：用户决策强烈依赖第一个获得的数字或信息
  - 文献：Plous, S. (1993) Chapter 10 - Anchoring and Adjustment

framing_effect（框架效应）:
  - 触发：用户描述方式明显偏向"得"或"失"的角度
  - 文献：Plous, S. (1993) Chapter 7 - The Perception of Risk

representativeness（代表性启发）:
  - 触发：用户以"看起来像"、"感觉符合"代替概率判断
  - 文献：Plous, S. (1993) Chapter 9 - Heuristics and Biases
