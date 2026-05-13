[English](README.en.md) | [中文](README.md)

# Decision Advisor - Life Decision Maker

> A professional decision-making advisor integrating psychology, behavioral economics, and management consulting methodologies.

**Decision Advisor** won't make decisions for you. Instead, it helps you **clarify your thoughts, weigh pros and cons, and identify cognitive biases** through structured frameworks, ultimately leading to more rational decisions.

---

## Core Features

| Feature | Description |
|---------|-------------|
| 🎯 **Intelligent Intent Recognition** | Automatically analyzes decision scenarios and recommends the most suitable decision framework |
| 🧠 **Professional Methodologies** | Integrates Nobel Prize-level decision-making theories |
| ⚠️ **Bias Detection** | Identifies 9 common cognitive biases and provides correction suggestions |
| 📋 **Structured Output** | Generates professional documents including decision trees, scorecards, and risk reports |
| 🔄 **Interactive Guidance** | Step-by-step questioning to gradually deepen understanding without information overload |

---

## Applicable Scenarios

| Scenario Type | Typical Questions | Recommended Framework |
|--------------|-------------------|----------------------|
| **Daily Life** | Which one to choose, buy or not, go or not | Satisficing, 10-10-10 Rule |
| **Career Development** | Graduate school, job change, entrepreneurship, career switch | Regret Minimization, Values Matrix |
| **Entrepreneurship & Investment** | Project feasibility, risk assessment | Expected Value Model, Scenario Planning |
| **Corporate Strategy** | Transformation, expansion, competitive strategy | McKinsey 7S, SWOT Analysis |

---

## Decision Frameworks

### Regret Minimization Framework
> *Jeff Bezos, Princeton University Commencement Address, 2010*

Look back from the future and choose the path that minimizes regret.

### 10-10-10 Decision Making
> *Suzy Welch, 2009*

Examine decisions from three time dimensions: 10 minutes, 10 months, and 10 years.

### Satisficing Theory
> *Herbert Simon, 1957 (Nobel Laureate in Economics)*

Don't pursue the optimal solution; stop searching once you find the first option that meets all criteria.

### Expected Value Model
> *Von Neumann & Morgenstern, 1944*

Quantitative calculation: Probability of success × Benefit - Probability of failure × Loss.

### Prospect Theory
> *Kahneman & Tversky, 1979 (Nobel Laureates)*

The psychological weight of losses is approximately 2.25 times that of gains.

### McKinsey 7S Framework
> *Peters & Waterman, 1982*

Seven elements work together to determine organizational strategy execution effectiveness.

---

## Project Structure

```
decision-advisor/
│
├── SKILL.md                          # Main Skill configuration file
│
├── assets/
│   ├── templates/
│   │   └── report.md                 # Decision report template
│   └── schema/
│       ├── intent_schema.json        # Intent recognition format
│       └── decision_output.json      # Decision output format
│
├── references/
│   ├── intent_map.md                 # Intent→Framework mapping table
│   ├── psychology_biases.md          # Cognitive bias guide
│   └── frameworks/
│       ├── daily_life/
│       │   ├── 10-10-10.md
│       │   └── satisficing.md
│       └── career/
│           └── regret_minimization.md
│
└── scripts/
    ├── intent_classifier.py          # Intent recognition and framework routing
    ├── interactive_collector.py      # Interactive information collection
    ├── score_calculator.py           # Multi-framework scoring calculation
    └── decision_tree_render.py       # Decision tree visualization
```

---

## Cognitive Bias Detection

The system can identify the following 9 common cognitive biases:

| Bias Type | Typical Manifestation | Theoretical Basis |
|-----------|----------------------|-------------------|
| Status Quo Bias | "I'm used to it, don't want to change" | Samuelson & Zeckhauser (1988) |
| Loss Aversion | "What if it fails" | Kahneman & Tversky (1979) |
| Overconfidence | "It will definitely work" | Fischhoff et al. (1977) |
| Sunk Cost | "I've already invested so much" | Arkes & Blumer (1985) |
| Availability Heuristic | "Someone I know..." | Tversky & Kahneman (1973) |
| Planning Fallacy | "It will be done quickly" | Kahneman & Tversky (1977) |
| Anchoring Effect | "What was first said..." | Tversky & Kahneman (1974) |
| Framing Effect | "Put it another way..." | Kahneman & Tversky (1979) |
| Representativeness Heuristic | "It looks like..." | Kahneman & Tversky (1972) |

---

## How to Use

1. **Describe Your Decision Problem** - Explain your dilemma in natural language
2. **Get Framework Recommendation** - The system automatically matches the most suitable decision-making method
3. **Answer Guided Questions** - 1-2 questions at a time, gradually going deeper
4. **Receive Analysis Report** - Get structured decision recommendations

---

## Output Example

```markdown
# 🎯 Decision Analysis Report

> **Generated**: 2026-05-13
> **Analysis Framework**: Regret Minimization Framework
> **Literature Basis**: Bezos (2010); Gilovich & Medvec (1995)

---

## 📊 Core Conclusion
**Recommended Option**: Graduate School
**Confidence Level**: High

---

## ⚠️ Bias Alerts
- Sunk Cost Fallacy: Detected "already prepared for a year"
- Status Quo Bias: Detected "used to the stable environment"

---

## 📚 References
- Bezos, J. (2010). Princeton University Commencement Address
- Gilovich, T. & Medvec, V.H. (1995). The experience of regret
```

---

## Target Audience

- 🎓 **Students and professionals** facing major life choices
- 💼 **Entrepreneurs** and **investors**
- 🏢 **Corporate managers**
- 🤔 **Decision-makers** who need to clarify their thinking

---

## Design Principles

1. **Guide Rather Than Replace** - Help users reach their own conclusions
2. **Methodology-Driven** - Every recommendation has academic support
3. **Interactive Collection** - Step-by-step questioning without assumptions
4. **Real-time Bias Correction** - Identify and alert cognitive biases
5. **Tiered Output** - Provide reports of different depths based on complexity

---

## License

[Apache License 2.0](LICENSE) © 2026 derek2000139
