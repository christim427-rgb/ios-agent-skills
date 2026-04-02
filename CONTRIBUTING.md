# Contributing a Skill

## What you'll build

An Agent Skill is a set of structured instruction files that make AI coding assistants generate production-grade code instead of generic suggestions. You package your engineering expertise — the things you catch in code reviews, the patterns you teach juniors, the mistakes you've debugged at 3 AM — into files that AI reads before generating code.

This is not documentation. Documentation is passive — developers must find and read it. A skill is active — it intercepts at the point of code generation and applies your knowledge automatically, every time.

## Before you start

- [ ] Fork and clone `https://github.com/rusel95/ios-agent-skills`
- [ ] A topic you know deeply from production experience (not from tutorials)
- [ ] Claude Code (recommended) — it will scaffold the skill from your input

## The flow: You provide expertise, AI structures it

You do not need to write Markdown files by hand. The process:

```
YOU dump your expertise in any format (bullet lists, code review comments, notes)
 ↓
Claude Code scaffolds the full skill: SKILL.md, README.md, reference files
 ↓
YOU review — correct mistakes, add what AI missed, adjust tone
 ↓
Claude Code incorporates feedback, registers skill in config files
 ↓
YOU test: compare AI output with and without the skill
 ↓
YOU submit a PR
```

Your raw input can be any combination of:
- **Do's and Don'ts lists** — "Always use X", "Never do Y"
- **Code review comments** — the things you keep repeating in PRs
- **Code snippets** — good vs bad examples, even incomplete
- **Architecture notes** — how layers connect, what depends on what
- **Anti-patterns** — bugs you've seen, mistakes juniors make
- **Migration checklists** — steps for moving from old to new pattern
- **Rough ideas** — "something feels off about how we do X" — AI will help shape it

The messier your input, the more iterations you'll need — but AI handles the formatting.

## What you own, what AI handles

| You (human expertise) | Claude Code (structure and formatting) |
| --- | --- |
| Domain expertise and rules | File structure and formatting |
| "What This Skill Changes" table in README.md | SKILL.md sections and decision trees |
| Reviewing and correcting generated content | Registering in all config files |
| Testing skill output | Filling in boilerplate |
| Deciding what matters in production | |

---

## Step 1: Choose your topic

A good skill topic is something where AI consistently gets it wrong in your domain, and you consistently fix it in code reviews.

**Right-sized examples:**

| Too small | Right-sized | Too broad |
| --- | --- | --- |
| "Use guard" | UIKit MVVM with Combine | iOS Development |
| One naming convention | Swift Concurrency patterns | Mobile Architecture |
| DRY principle | iOS Security audit (OWASP MASVS) | Security |

**Quick test — answer YES to at least 4:**

- [ ] Does AI regularly produce wrong code here without guidance?
- [ ] Would a senior engineer learn at least one thing from this skill?
- [ ] Can you write 15+ actionable rules (not opinions)?
- [ ] Does this topic come up in code reviews at least monthly?
- [ ] Is there a production incident or compliance requirement behind this?
- [ ] Would this take a junior engineer 2+ hours to learn from scratch?

If fewer than 4, your topic is either too small (combine with related topics) or too generic (AI already knows it).

## Step 2: Feed your expertise to Claude Code

Open this repo in Claude Code and give it your raw material.

**Example prompt:**

```
Create a new iOS skill called <your-skill-name>,
following the structure of existing skills (e.g. skills/swiftui-mvvm/).

Here's what I know about this topic:

Do's:
- Always use X when...
- Every new screen must have...

Don'ts:
- Never call X from Y because...
- Don't use Z pattern, it causes...

Anti-patterns I keep catching in code review:
- Junior devs always forget to...
- Copy-pasted code from tutorials usually misses...

Ideas / things I'm not sure how to phrase yet:
- Something feels wrong about how we handle X...
- I always end up fixing Y in PRs but don't know the rule name...

[paste any code snippets, notes, links]
```

Claude Code will create `skills/<your-skill-name>/` and generate `SKILL.md`, `README.md`, and reference files from your input.

## Step 3: Review and refine

This is where your expertise matters most. Claude Code structures well, but may:
- **Miss domain nuances** — patterns that only matter in your specific stack
- **Over-generalize** — "use dependency injection" instead of your specific DI approach
- **Include too much code** — full implementations instead of skeletons
- **Skip edge cases** — the 3 AM bugs that only you've seen

Review each generated file and tell Claude Code what to fix. Common feedback:
- "Add more Don'ts — here's what else I catch in reviews: ..."
- "This code example is too detailed — make it a skeleton"
- "Missing coverage of X pattern, very common in our legacy codebase"
- "The decision tree is wrong — in our case, Y comes before Z"

Iterate until the skill captures your actual code review voice. **2-3 rounds is normal.**

## Step 4: Register the skill

Ask Claude Code to register the skill:

```
Register this skill in all config files.
```

It will update:

| File | Purpose | Used by |
| --- | --- | --- |
| `AGENTS.md` | Available skills listing | Claude Code |
| `agents/openai.yaml` | Skill listing | OpenAI Codex |
| `.cursorrules` | Skill listing | Cursor |
| `README.md` (root) | Human-facing skills table | GitHub visitors |

## Step 5: Test your skill

Before submitting a PR, verify that your skill actually changes the AI output.

**Quick test (5 min):**

1. Ask Claude Code a question your skill covers — **without** the skill in context
2. Save the output
3. Add your skill to context (`#File skills/<your-skill>/SKILL.md`) and ask the same question
4. Compare: Is the output measurably different and better?

If the outputs are nearly identical, your skill isn't adding value — it's restating what AI already knows. Go back and add more production-specific patterns, edge cases, and pitfalls.

**What "better" means:**
- Code compiles and follows project conventions (not tutorial-grade)
- Security patterns are correct (no hardcoded secrets, PII handled)
- Architecture matches production standards (not generic examples)

## Step 6: Submit a PR

**Title:** `feat(skills): add <skill-name>`

**PR checklist:**

- [ ] `SKILL.md` has frontmatter with `name` + `description`
- [ ] `README.md` has a "What This Skill Changes" before/after table (write by hand)
- [ ] `README.md` ends with an `## Author` section
- [ ] All registration files updated (`AGENTS.md`, `agents/openai.yaml`, `.cursorrules`, root `README.md`)
- [ ] Quick test shows measurable improvement in AI output
- [ ] Code examples are skeletons, not full implementations
- [ ] No client-specific code, project names, or proprietary implementations

---

## Skill file structure

```
skills/your-skill-name/
├── SKILL.md       <- Instructions for the AI agent
├── README.md      <- Description for humans (with benchmark results)
└── references/    <- Deep-dive files (optional)
     ├── topic-a.md
     ├── topic-b.md
     └── anti-patterns.md
```

**SKILL.md frontmatter** — only two fields:
```yaml
---
name: your-skill-name
description: "What + when. Include trigger keywords for AI activation."
---
```

**Reference files:** 100-300 lines each, one sub-topic per file, skeleton code only.

**README.md** must include a "What This Skill Changes" before/after table — this is what sells the skill to other developers. Write it by hand, do not auto-generate.

## Benchmarking (optional, recommended)

After creating a skill, benchmark it to prove value with data:

1. Create eval prompts in `evals/ios/<skill-name>/evals.json`
2. Run with/without skill comparisons using Claude Code
3. Grade against discriminating assertions
4. Add results to your skill's `README.md` and the root `README.md`

See [BENCHMARKING.md](BENCHMARKING.md) for the full methodology.

## Common mistakes

- **Trying to write everything by hand.** Let Claude Code scaffold from your raw notes.
- **Providing too little input.** "Make a skill about React" gives AI nothing. Dump your actual rules and anti-patterns.
- **Accepting the first draft.** Claude Code's first pass is a starting point. 2-3 rounds of feedback is normal.
- **Too much code in reference files.** Use skeletons (signatures + comments). Full code gets copy-pasted without adaptation.
- **Restating what AI already knows.** If AI gives the same answer without your skill, you're wasting context window.
- **Scope creep.** If `SKILL.md` exceeds 500 lines, split into a focused `SKILL.md` + reference files.

## IP safety

Skills encode patterns and principles ("always use circuit breakers for external service calls"), not proprietary implementations. No client names, no internal URLs, no proprietary algorithms.
