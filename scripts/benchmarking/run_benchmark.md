# Benchmarking Guide

A complete, agent-agnostic guide for running skill evaluations. Any AI agent (Claude Code, Copilot, Gemini CLI, Cursor, Windsurf, etc.) can follow these steps.

## Overview

A benchmark measures whether an AI skill improves response quality. It does this by:

1. Running the same prompt **with** and **without** the skill
2. Grading both responses against binary assertions
3. Comparing pass rates to quantify the skill's impact

## Prerequisites

- Python 3.9+ (standard library only -- no pip installs needed)
- Access to the skill files in this repository
- An AI agent that can read/write files and follow instructions

## Directory Structure

All benchmark outputs go in the `workspaces/` directory (gitignored):

```
workspaces/
└── {platform}/                    # e.g. "ios", "android", "react-native"
    └── {skill-name}/              # e.g. "ios-testing", "swift-concurrency"
        └── iteration-{N}/         # Increment for each benchmark run
            ├── benchmark.json     # Aggregated results (generated)
            ├── benchmark.md       # Human-readable summary (generated)
            └── eval-{name}/       # One per eval prompt
                ├── eval_metadata.json  # Prompt + assertions
                ├── with_skill/         # Or "{model}-with"
                │   └── run-1/
                │       ├── outputs/
                │       │   └── response.md
                │       ├── grading.json
                │       └── timing.json (optional)
                └── without_skill/      # Or "{model}-without"
                    └── run-1/
                        ├── outputs/
                        │   └── response.md
                        ├── grading.json
                        └── timing.json (optional)
```

## Step-by-Step Process

### Step 1: Identify Evals

Evals are defined in JSON files under each skill's `evals/` directory:

```
skills/{platform}/{skill-name}/evals/evals.json
```

Each eval file contains an array of eval definitions. Each eval has:
- `eval_name`: Unique identifier (used as directory name)
- `prompt`: The question to ask the AI
- `assertions`: Binary checks to grade the response

If no evals exist yet, create them. See "Creating New Evals" below.

### Step 2: Set Up the Iteration Directory

Create the workspace structure for this benchmark run:

```bash
PLATFORM="ios"
SKILL="ios-testing"
ITERATION=1

mkdir -p workspaces/${PLATFORM}/${SKILL}/iteration-${ITERATION}
```

### Step 3: Run WITH-Skill Responses

For each eval, ask the AI agent to answer the prompt after reading the skill.

#### Prompt Template (WITH skill)

```
Read the skill at: skills/{PLATFORM}/{SKILL}/SKILL.md
Read all reference files mentioned in that SKILL.md.

Then answer the following question using the skill's guidance:

---
{PROMPT FROM EVAL}
---

Save your complete response to:
workspaces/{PLATFORM}/{SKILL}/iteration-{N}/eval-{NAME}/with_skill/run-1/outputs/response.md
```

### Step 4: Run WITHOUT-Skill Responses

For each eval, ask the AI agent to answer the same prompt using only built-in knowledge.

#### Prompt Template (WITHOUT skill)

```
Answer the following question using only your built-in knowledge.
Do NOT read any skill files or reference documents.

---
{PROMPT FROM EVAL}
---

Save your complete response to:
workspaces/{PLATFORM}/{SKILL}/iteration-{N}/eval-{NAME}/without_skill/run-1/outputs/response.md
```

### Step 5: Copy eval_metadata.json

For each eval, copy or create the eval_metadata.json in the eval directory:

```bash
cp skills/${PLATFORM}/${SKILL}/evals/eval-{NAME}.json \
   workspaces/${PLATFORM}/${SKILL}/iteration-${ITERATION}/eval-{NAME}/eval_metadata.json
```

Or if evals are in a single evals.json array, extract the relevant entry.

### Step 6: Grade Responses

You have two options for grading:

#### Option A: Auto-Grader (keyword assertions only)

Run the auto-grader script for keyword_present assertions:

```bash
python scripts/benchmarking/grade_responses.py \
    workspaces/${PLATFORM}/${SKILL}/iteration-${ITERATION}/
```

This handles `keyword_present` assertions automatically. It flags `content_check` and `structure_check` assertions that need AI review.

#### Option B: AI-Agent Grader (all assertion types)

For semantic assertions, use the grader prompt with any AI agent.

**Grading prompt to give an AI agent:**

```
Follow the grading instructions in: scripts/benchmarking/grader-prompt.md

Grade this response:
- Response file: workspaces/{PLATFORM}/{SKILL}/iteration-{N}/eval-{NAME}/{CONFIG}/run-1/outputs/response.md
- Assertions: (paste the assertions array from eval_metadata.json)
- Output directory: workspaces/{PLATFORM}/{SKILL}/iteration-{N}/eval-{NAME}/{CONFIG}/run-1/outputs/

Write grading.json to: workspaces/{PLATFORM}/{SKILL}/iteration-{N}/eval-{NAME}/{CONFIG}/run-1/grading.json
```

### Step 7: A/B Blind Judging (Optional)

For subjective quality comparison beyond binary assertions:

1. **Randomize**: Flip a coin to decide which response is "A" and which is "B"
2. **Give the AI agent this prompt:**

```
You are a blind judge. Compare these two responses to the same prompt.

Prompt: {PROMPT FROM EVAL}

Response A: (paste or path to one response)
Response B: (paste or path to other response)

Follow the A/B judging instructions in: scripts/benchmarking/grader-prompt.md

Score each response 0-10 on: Correctness, Completeness, Specificity, Structure, Best Practices.
Pick a winner or declare a tie (if within 3 points).

Output the result as JSON.
```

3. Record which config (with/without skill) mapped to A/B after judging

### Step 8: Aggregate Results

Once all grading.json files are in place, run aggregation:

```bash
python scripts/benchmarking/aggregate_benchmark.py \
    workspaces/${PLATFORM}/${SKILL}/iteration-${ITERATION}/ \
    --skill-name "${SKILL}" \
    --skill-path "skills/${PLATFORM}/${SKILL}"
```

This generates:
- `benchmark.json` -- Machine-readable results
- `benchmark.md` -- Human-readable summary table

### Step 9: Review Results

Open `benchmark.md` to see the summary:

| Metric | With Skill | Without Skill | Delta |
|--------|-----------|---------------|-------|
| Pass Rate | 95% +/- 5% | 60% +/- 12% | +0.35 |
| Time | 45.2s +/- 8.1s | 32.1s +/- 5.4s | +13.1s |

A positive delta in pass rate means the skill improved results.

---

## Agent-Specific Examples

### Claude Code

```bash
# Run with-skill eval (spawns subagent)
claude -p "Read skills/ios/ios-testing/SKILL.md and all its references. Then answer: $(cat eval_prompt.txt). Save response to workspaces/ios/ios-testing/iteration-1/eval-observable-viewmodel/with_skill/run-1/outputs/response.md"

# Run without-skill eval
claude -p "Using only built-in knowledge, answer: $(cat eval_prompt.txt). Save response to workspaces/ios/ios-testing/iteration-1/eval-observable-viewmodel/without_skill/run-1/outputs/response.md"

# Grade
claude -p "Follow scripts/benchmarking/grader-prompt.md to grade the response at workspaces/ios/ios-testing/iteration-1/eval-observable-viewmodel/with_skill/run-1/outputs/response.md against these assertions: $(cat eval_metadata.json | jq '.assertions'). Write grading.json to the run-1/ directory."

# Aggregate
python scripts/benchmarking/aggregate_benchmark.py workspaces/ios/ios-testing/iteration-1/ --skill-name ios-testing
```

### GitHub Copilot (VS Code Chat)

```
@workspace Read skills/ios/ios-testing/SKILL.md and all reference files it mentions.
Then answer this question and save the response to
workspaces/ios/ios-testing/iteration-1/eval-observable-viewmodel/with_skill/run-1/outputs/response.md:

I have a ProfileViewModel that uses @Observable, loads user data async via a
UserRepository protocol, and sets a ViewState enum. Can you write a full test suite for it?
```

### Gemini CLI

```bash
# With skill
gemini -p "Read skills/ios/ios-testing/SKILL.md and all referenced files. Answer: $(cat eval_prompt.txt)" > workspaces/ios/ios-testing/iteration-1/eval-observable-viewmodel/with_skill/run-1/outputs/response.md

# Without skill
gemini -p "Using only built-in knowledge: $(cat eval_prompt.txt)" > workspaces/ios/ios-testing/iteration-1/eval-observable-viewmodel/without_skill/run-1/outputs/response.md

# Auto-grade
python scripts/benchmarking/grade_responses.py workspaces/ios/ios-testing/iteration-1/

# Aggregate
python scripts/benchmarking/aggregate_benchmark.py workspaces/ios/ios-testing/iteration-1/ --skill-name ios-testing
```

### Cursor / Windsurf / Any Agent

The pattern is the same for any AI coding agent:

1. Ask it to read the skill, then answer the prompt, saving to the with_skill path
2. Ask it to answer the prompt without reading the skill, saving to the without_skill path
3. Run `grade_responses.py` or ask the agent to grade using `grader-prompt.md`
4. Run `aggregate_benchmark.py` to get the summary

---

## Creating New Evals

### eval_metadata.json Schema

```json
{
  "eval_id": 0,
  "eval_name": "eval-descriptive-name",
  "prompt": "The full question to ask the AI agent",
  "assertions": [
    {
      "id": "A0.1",
      "description": "Human-readable description of what is being checked",
      "type": "keyword_present",
      "check": "output contains '@Test' or '@Suite'"
    },
    {
      "id": "A0.2",
      "description": "Response includes error handling for network failures",
      "type": "content_check",
      "check": "output includes a test or code block handling network errors"
    },
    {
      "id": "A0.3",
      "description": "Code is organized with MARK comments or clear sections",
      "type": "structure_check",
      "check": "output has organized sections with headers or MARK comments"
    }
  ]
}
```

### Assertion Types

| Type | Auto-Gradable | Description |
|------|:---:|-------------|
| `keyword_present` | Yes | Check if specific keywords/patterns appear in the response |
| `content_check` | Partial | Check if described content exists (may need AI review) |
| `structure_check` | Partial | Check if structural elements are present (may need AI review) |

### Writing Good Assertions

- **Be specific**: "output contains '@MainActor'" is better than "uses proper annotations"
- **Be discriminating**: The assertion should fail when the response is genuinely wrong
- **Cover failure modes**: Include assertions for error handling, edge cases, not just happy paths
- **Test the skill's value-add**: Focus on things the skill teaches that baseline knowledge might miss
- **Use keyword_present** when possible -- it enables reliable auto-grading

---

## Multiple Runs

For statistical confidence, run each eval multiple times (recommended: 3 runs).

Increment the run number in the path:

```
eval-{NAME}/{CONFIG}/run-1/outputs/response.md
eval-{NAME}/{CONFIG}/run-2/outputs/response.md
eval-{NAME}/{CONFIG}/run-3/outputs/response.md
```

The aggregation script calculates mean, stddev, min, max across runs.

---

## Multi-Model Benchmarks

To compare models, use model name in the config directory:

```
eval-{NAME}/
├── claude-opus-with/run-1/outputs/response.md
├── claude-opus-without/run-1/outputs/response.md
├── gemini-pro-with/run-1/outputs/response.md
├── gemini-pro-without/run-1/outputs/response.md
├── gpt4-with/run-1/outputs/response.md
└── gpt4-without/run-1/outputs/response.md
```

The aggregation script discovers config names dynamically -- no code changes needed.

---

## Troubleshooting

**"No eval directories found"**
- Ensure eval directories are named `eval-*` (with the `eval-` prefix)
- Check that they are directly under the iteration directory

**"No response files found"**
- Response must be at `run-N/outputs/response.md`
- Verify the directory structure matches the expected layout

**Auto-grader shows "[needs-ai-review]"**
- This is expected for `content_check` and `structure_check` assertions
- Use an AI agent with `grader-prompt.md` to grade these accurately
- Or convert assertions to `keyword_present` type with specific patterns

**Aggregation shows 0% pass rate**
- Check that `grading.json` files exist in each `run-N/` directory
- Verify the JSON is valid (not truncated or malformed)
