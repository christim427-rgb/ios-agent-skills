# Grading Rules

These rules apply to every grading call. Follow them without exception.

---

## Core Contract

**An assertion PASSES if and only if the response EXPLICITLY states the required content.**

Not implied. Not adjacent. Not "the reader would infer." The words must be there.

---

## Pass Criteria

PASS when:
- The specific claim in the assertion text is directly stated in the response
- A user reading only the response (with no prior context) would receive that specific guidance

FAIL when:
- The assertion's content is absent from the response
- The response gives correct but different advice that does not address the assertion
- The response mentions the topic but misses the specific claim
- The response hedges ("this might be an issue") but doesn't confirm the assertion's claim

---

## Examples

**Assertion**: "Identifies os_unfair_lock as stored property causes memory corruption"

PASS: "Using `os_unfair_lock` as a stored value type (struct) in a class will cause memory corruption because it must remain at a fixed memory address."

FAIL: "Be careful with lock types in Swift." ← too vague  
FAIL: "Use NSLock instead." ← doesn't address stored property  
FAIL: "os_unfair_lock has some limitations." ← not specific enough

---

**Assertion**: "References WWDC 2017-706 or recommends 3-4 subsystem queues"

PASS: "As Apple recommended in WWDC 2017 session 706, limit your app to 3-4 serial queues organized by subsystem."  
PASS: "Create only 3-4 serial queues organized by subsystem — one per major concern, not one per network call."

FAIL: "Avoid creating too many queues." ← no specific count, no session reference

---

## Anti-Charity Rules

1. **No benefit of the doubt.** Ambiguous? FAIL.
2. **No partial credit.** Each assertion is binary: passed or failed. There is no "mostly passed."
3. **No inferring intent.** The response must state it, not imply it.
4. **No cross-assertion credit.** Passing one assertion never contributes to another.
5. **Adjacent ≠ correct.** Mentioning a related concept does not satisfy an assertion about a specific one.
6. **Hedges and qualifiers fail.** "You might want to..." or "this could be..." does not count as an explicit identification.

---

## Grader Isolation

The grader operates under double-blind conditions:

- Receives ONLY: the response text + assertion list
- Does NOT receive: the skill's SKILL.md, reference files, or any description of what the skill teaches
- Does NOT know whether the response was generated with or without skill context
- Does NOT adjust expectations based on the apparent capability of the model

If you are the grader and you have already read the skill being tested, you cannot grade this run. Stop and use a fresh context.

---

## Output Format

```json
{
  "eval_id": 1,
  "variant": "<model-slug>-with OR <model-slug>-without",
  "assertions": [
    {
      "id": "X1.1",
      "passed": true,
      "notes": "Exact quote: 'Using os_unfair_lock as a stored value type causes memory corruption'"
    },
    {
      "id": "X1.2",
      "passed": false,
      "notes": "Response mentions lock types but does not address the stored property issue"
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 1,
    "total": 2,
    "pass_rate": 0.5
  }
}
```

For `notes` on a PASS: include a short direct quote from the response that satisfies the assertion.  
For `notes` on a FAIL: state specifically what was missing or why the response fell short.
