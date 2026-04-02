# Benchmarking Process — How It Works End-to-End

This document explains the full benchmarking process from the perspective of the AI assistant running it. It covers what happens at each stage, why each design decision exists, and what the assistant can and cannot do.

---

## Overview

The benchmarking system measures whether a skill makes an AI model's responses better for the specific task the skill was built for.

```mermaid
flowchart TB
    subgraph Generation["Stage 1: Response Generation"]
        Prompt[Eval Prompt] --> WithAgent["WITH-skill subagent<br/>(reads SKILL.md + references)"]
        Prompt --> WithoutAgent["WITHOUT-skill subagent<br/>(training data only)"]
        WithAgent --> WithResp["response.md<br/>(with skill)"]
        WithoutAgent --> WithoutResp["response.md<br/>(without skill)"]
    end

    subgraph Evaluation["Stage 2: Evaluation"]
        WithResp & WithoutResp --> Grader["Method 1: Binary Assertion Grading<br/>PASS/FAIL per assertion"]
        WithResp & WithoutResp --> ABJudge["Method 2: Blind A/B Comparison<br/>0-10 quality scores"]
    end

    subgraph Aggregation["Stage 3: Aggregation"]
        Grader --> Delta["Binary delta<br/>e.g. +17.8%"]
        ABJudge --> ABResult["A/B wins/ties/losses<br/>e.g. 20/24 wins (8.5↑7.4)"]
        Delta & ABResult --> Topics["Topic breakdown<br/>per skill knowledge area"]
    end

    Topics --> README["README tables"]

    style Generation fill:#e8f4fd,stroke:#4a90d9
    style Evaluation fill:#fef3e8,stroke:#d9904a
    style Aggregation fill:#e8fde8,stroke:#4ad94a
```

---

## Stage 1: Response Generation

```mermaid
sequenceDiagram
    participant Main as Main Agent
    participant W as WITH Subagent
    participant WO as WITHOUT Subagent

    Main->>W: Eval prompt + SKILL.md + references
    Main->>WO: Eval prompt only (no skill files)

    Note over W: Reads SKILL.md<br/>Reads references/*.md<br/>Answers prompt
    Note over WO: Answers from<br/>training data only

    W-->>Main: response.md (with skill)
    WO-->>Main: response.md (without skill)

    Note over Main: Context isolation:<br/>subagents cannot leak<br/>skill knowledge to each other
```

### Why subagents, not the main agent

Each subagent has an **isolated context window**. The WITH subagent cannot "leak" skill knowledge to the WITHOUT subagent. If the main agent answered both, it would have skill knowledge in context when answering the WITHOUT variant — contaminating the baseline.

### What requires human action

Generating responses for non-Claude models (GPT, Gemini, etc.) — these must be generated externally and placed manually at the workspace paths.

---

## Stage 2: Method 1 — Binary Assertion Grading

### What it measures

Whether the response **explicitly states** specific technical claims.

```mermaid
flowchart LR
    Response["response.md"] --> Grader["Isolated Grader<br/>(never sees SKILL.md)"]
    Assertions["Assertions from<br/>evals.json"] --> Grader
    Grader --> Result["grading.json<br/>PASS + quote evidence<br/>or FAIL + 'not found'"]

    style Grader fill:#fff3cd,stroke:#856404
```

### Grading rules — evidence only, no charity

```mermaid
flowchart TD
    Check["Does the response<br/>explicitly state the claim?"] -->|"Yes, with direct quote"| PASS["PASS<br/>+ evidence quote"]
    Check -->|"Implied but not stated"| FAIL1["FAIL"]
    Check -->|"Close but missing exact API/term"| FAIL2["FAIL"]
    Check -->|"Not mentioned at all"| FAIL3["FAIL"]

    Example1["'use a task group'"] --> FAIL4["FAIL<br/>(missing exact symbol)"]
    Example2["'use withTaskGroup'"] --> PASS2["PASS"]

    style PASS fill:#d4edda,stroke:#155724
    style PASS2 fill:#d4edda,stroke:#155724
    style FAIL1 fill:#f8d7da,stroke:#721c24
    style FAIL2 fill:#f8d7da,stroke:#721c24
    style FAIL3 fill:#f8d7da,stroke:#721c24
    style FAIL4 fill:#f8d7da,stroke:#721c24
```

### Why this strictness matters

1. **Reproducibility** — two graders given the same response produce the same score
2. **No inflation** — vague responses don't get credit
3. **Real signal** — the delta only appears when the skill teaches something concrete

### Limitations

Binary assertions cannot tell the difference between a one-line mention and a full explanation with code. Both score PASS. This is why Method 2 (A/B) exists.

---

## Stage 3: Method 2 — Blind A/B Quality Comparison

### What it measures

Which response is **qualitatively better** — deeper, more structured, more actionable.

```mermaid
flowchart TB
    subgraph Randomization["Position Randomization"]
        Odd["Odd evals:<br/>A = with-skill<br/>B = without-skill"]
        Even["Even evals:<br/>A = without-skill<br/>B = with-skill"]
    end

    Randomization --> Judge["Blind Judge<br/>(does NOT know which is which)"]

    Judge --> Score["Scores each 0-10 on:<br/>Correctness · Completeness<br/>Specificity · Structure · Actionability"]

    Score --> Winner{"Score gap > 0.5?"}
    Winner -->|"Yes"| Win["Winner declared"]
    Winner -->|"No (within 0.5)"| Tie["Tie"]

    style Judge fill:#e8d4f0,stroke:#6a1b9a
    style Win fill:#d4edda,stroke:#155724
    style Tie fill:#fff3cd,stroke:#856404
```

### How to read A/B results

```mermaid
pie title "mvvm-uikit: 20/24 A/B (9.1↑8.2)"
    "Skill wins" : 20
    "Ties" : 2
    "Skill losses" : 2
```

- **20/24** = skill response won 20 blind comparisons
- **Ties** = both responses equally good (score gap ≤ 0.5)
- **Losses** = without-skill was genuinely better (rare — 2 out of 132 total across all skills)
- **(9.1↑8.2)** = average scores: with-skill 9.1, without-skill 8.2

### Why A/B matters more than binary for strong models

For models that pass 95-100% of binary assertions at baseline (Sonnet 4.6), the binary delta is near zero. But A/B reveals quality differences invisible to pass/fail:

- Structured severity rankings
- Specific API references and code examples
- Edge cases and migration paths
- Organized findings with clear remediation steps

---

## Stage 4: Aggregation and Topic Analysis

Evals are grouped by topic. This shows WHICH knowledge areas the skill improves:

```mermaid
flowchart LR
    subgraph Topics["Topic Groups"]
        TopicA["Topic A<br/>Core concept"]
        TopicB["Topic B<br/>Framework detail"]
        TopicC["Topic C<br/>Advanced workflow"]
    end

    TopicA --> A_Result["Baseline may already be strong<br/>if the model knows this area"]
    TopicB --> B_Result["Skill starts differentiating<br/>in specific framework details"]
    TopicC --> C_Result["Largest gains often appear<br/>in niche or advanced topics"]

    style TopicA fill:#d4edda,stroke:#155724
    style TopicB fill:#fff3cd,stroke:#856404
    style TopicC fill:#f8d7da,stroke:#721c24
```

---

## Grading Integrity — Why It's Model-Agnostic

```mermaid
flowchart TB
    subgraph Generator["Generator Context"]
        Skill["SKILL.md + references"] --> Gen["Model generates response"]
        Gen --> Resp["response.md"]
    end

    subgraph Grader["Grader Context (ISOLATED)"]
        Assertions["Assertions only"] --> Grade["Grader checks for<br/>explicit quotes"]
        Resp2["response.md"] --> Grade
        NoSkill["NO access to SKILL.md"]
        Grade --> GradingJSON["grading.json"]
    end

    Resp --> Resp2

    style NoSkill fill:#f8d7da,stroke:#721c24
    style Grader fill:#fff3cd,stroke:#856404
```

### Why the grading is trustworthy

1. **Evidence-based, not opinion-based** — the grader checks for explicit quotes, not whether the response "feels right"
2. **The grader never sees the skill** — it cannot know what the "expected" answer is
3. **Same grader for both variants** — any bias affects WITH and WITHOUT equally, so the delta is unbiased
4. **A/B cross-validates** — if binary grading were charitable, A/B would show all ties. Instead it shows clear winners
5. **Verifiable** — every PASS includes a direct quote anyone can check

### When to add harder assertions

If a new model passes 95%+ at baseline, the assertions were designed for a weaker model. The correct response:
- Keep running A/B (this always discriminates)
- Optionally: add deeper assertions testing specific API signatures or multi-step reasoning

---

## What the Assistant Can Do

```mermaid
flowchart LR
    subgraph Can["What the assistant handles"]
        R["Response generation<br/>(Claude models)"]
        G["Binary grading<br/>(any model's responses)"]
        AB["Blind A/B judging"]
        Agg["Aggregation + topic analysis"]
        Rep["README updates"]
    end

    subgraph Cannot["Requires human action"]
        NonClaude["Generate responses for<br/>GPT, Gemini, etc."]
        Evals["Create new eval prompts<br/>(needs domain expertise)"]
        Limits["Override rate limits"]
    end

    style Can fill:#d4edda,stroke:#155724
    style Cannot fill:#f8d7da,stroke:#721c24
```

---

## Recommended Workflow

```mermaid
flowchart TD
    Start["New model to benchmark"] --> Gen["1. Generate responses<br/>(1 skill at a time)"]
    Gen --> Grade["2. Grade responses<br/>(1 grader subagent)"]
    Grade --> Spot["Spot-check evidence quotes"]
    Spot --> AB["3. Run A/B comparison<br/>(1 judge subagent)"]
    AB --> Agg["4. Aggregate + topic analysis"]
    Agg --> Update["5. Update READMEs"]

    Gen -.->|"Max 2-3 subagents<br/>in parallel"| Warning["Rate limits are the bottleneck.<br/>Predictable > fast."]

    style Warning fill:#fff3cd,stroke:#856404
```

**Key lesson:** Never run more than 2-3 subagents in parallel. Predictable sequential execution beats fast parallel execution that hits limits and produces zero results.
