# iOS Security Audit

Enterprise-grade security auditing skill for iOS codebases aligned with OWASP MASVS v2.1.0. Detects vulnerabilities across storage, cryptography, networking, platform integration, and code quality in both Swift and Objective-C.

## Benchmark Results

Tested on **17 scenarios** with **37 discriminating assertions**.

### Results Summary

| Model | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| **Sonnet 4.6** | 37/37 (100%) | 11/37 (29.7%) | **+70.3%** | **9W 15T 0L** (avg 9.3 vs 8.9) |
| **GPT-5.4** | 37/37 (100%) | 34/37 (91.9%) | **+8.1%** | 2W 15T 0L |
| **Gemini 3.1 Pro** | 16/16 (100%) | 2/16 (12.5%) | **+87.5%** | **10W** 0T 0L (avg 9.1 vs 6.0) |

> A/B Quality: blind judge scores each response 0–10 and picks the better one without knowing which used the skill. Position (A/B) is randomized across evals to prevent bias. "—" = not yet collected.

### Results (Sonnet 4.6)

| Metric | Value |
| --- | --- |
| With Skill | 37/37 (100%) |
| Without Skill | 11/37 (29.7%) |
| Delta | **+70.3%** |
| A/B Quality | **9W 15T 0L** (avg 9.3 vs 8.9) |

**Interpretation:** Sonnet 4.6 without the skill misses 26 of 37 discriminating assertions — it answers questions correctly but omits OWASP MASVS control citations, MASWE identifiers, L2-vs-L1 requirement boundaries, HIPAA/PCI section numbers, `memset_s` key zeroing, `SecAccessControl` biometric binding patterns, and explicit BLOCK/RELEASE recommendations. The skill provides the structured audit vocabulary Sonnet lacks by default. A/B confirms with 9 wins and zero losses. (Graded: Claude Sonnet 4.6, strict, iteration-7)

### Results (GPT-5.4)

| Metric | Value |
| --- | --- |
| With Skill | 37/37 (100%) |
| Without Skill | 34/37 (91.9%) |
| Delta | **+8.1%** |
| A/B | 2W 15T 0L |

**Interpretation:** GPT-5.4 naturally includes OWASP MASVS citations and audit terminology — 91.9% without the skill. The 3 gaps are in nuanced areas: ObjC NSKeyedUnarchiver severity labeling, explicit WebView BLOCK recommendation for banking apps, and `memset_s` for key material zeroing. The skill closes these to 100%. (Graded: Claude Sonnet 4.6, strict, iteration-6)

### Results (Gemini 3.1 Pro)

| Metric | Value |
| --- | --- |
| With Skill | 16/16 (100%) |
| Without Skill | 2/16 (12.5%) |
| Delta | **+87.5%** |
| A/B Quality | — (not collected) |

> **Coverage note:** 10/17 evals graded. The 7 remaining evals (objc-medium, objc-complex, compliance-simple, compliance-medium, compliance-complex, appstore-medium, audit-process-complex) had empty `eval_name` in the outputs file — the responses were from a different skill run and could not be matched. Pass rates above are computed over the 16 assertions in the 10 graded evals only.

**Interpretation:** Gemini 3.1 Pro without the skill almost completely fails discriminating assertions — only 2/16 pass (both are CR1.2 and CR2.3, which require common binary extraction knowledge and Keychain recommendation). It correctly identifies security issues in plain language but never cites OWASP MASVS controls, MASWE identifiers, kSecAttrAccessible hierarchies, URLSessionDelegate pinning code, or `.nonPersistent()` websiteDataStore. The skill lifts it from 12.5% to 100% on graded evals. (Graded: Claude Sonnet 4.6, strict, iteration-1)

### Key Discriminating Assertions (missed without skill)

| Topic | Assertion | Why It Matters |
| --- | --- | --- |
| appstore | `NSPrivacyAccessedAPITypes` must declare API usage reasons | Privacy manifest completeness |
| appstore | `NSPrivacyTrackingDomains` for tracking domains | App Store privacy enforcement |
| audit-process | Maps finding to `MASVS-STORAGE-1` | Audit traceability to MASVS control |
| audit-process | Includes MASWE ID such as `MASWE-0005` | Vulnerability taxonomy precision |
| compliance | Missing biometric auth with server binding for L2 | Correct L2 control boundary |
| objc-medium | Did not label `unarchiveObjectWithData` as CRITICAL severity; missed false security of `decodeObjectForKey:` without type-safe class parameter | NSKeyedUnarchiver deserialization severity precision |
| platform-complex | No explicit BLOCK recommendation for banking app WebView configuration | WebView release-gate enforcement for regulated apps |

### Topic Breakdown

| Topic | Simple | Medium | Complex |
| --- | --- | --- | --- |
| storage | **+33%** | 0% | **+75%** |
| crypto | 0% | **+25%** | **+40%** |
| network | 0% | **+50%** | 0% |
| platform | 0% | **+25%** | **+60%** |
| objc | 0% | **+25%** | **+40%** |
| compliance | **+33%** | **+25%** | **+20%** |
| appstore | 0% | **+25%** | **+40%** |
| audit-process | 0% | 0% | **+40%** |

> Raw data:
> `ios-security-audit-workspace/iteration-1/benchmark-gpt-5-4.json`

### Benchmark Cost Estimate

| Step | Formula | Tokens |
| --- | --- | --- |
| Eval runs (with_skill) | 24 × 35k | 840k |
| Eval runs (without_skill) | 24 × 12k | 288k |
| Grading (48 runs × 5k) | 48 × 5k | 240k |
| **Total** | | **~1.4M** |
| **Est. cost (Sonnet 4.6)** | ~$5.4/1M | **~$8** |

> Token estimates based on sampled timing.json files. Blended rate ~$5.4/1M for Sonnet 4.6 ($3 input + $15 output, ~80/20 ratio).

---

## What This Skill Changes

| Without Skill | With Skill |
| --- | --- |
| Ad-hoc security reviews with inconsistent coverage | Structured audit against 24 MASVS controls |
| Missed hardcoded secrets and insecure storage | Pattern-first detection of CRITICAL vulnerabilities |
| No compliance mapping for regulated apps | HIPAA, PCI DSS, GDPR, SOC 2 requirement mapping |
| Generic security advice | Concrete vulnerable/secure code pairs with MASVS traceability |
| Same checklist for all apps | L1/L2/R testing profile-aware severity classification |

## Install

```bash
npx skills add rusel95/ios-agent-skills --skill ios-security-audit
```

Verify by asking your AI assistant to "run a security audit on this iOS project".

## Testing From a Feature Branch

To test a skill before it's merged:

```bash
# 1. Clone the repo (or use an existing clone)
git clone https://github.com/anthropics/agent-skills.git
cd agent-skills
git checkout skill/iOS-security-audit  # or your feature branch

# 2. Copy the skill into your target project
cp -r skills/ios/ios-security-audit /path/to/your-ios-project/.claude/skills/

# 3. Add the skill to your project's CLAUDE.md (or .cursorrules, .github/copilot-instructions.md)
# Add this line to the skills section:
# - **ios-security-audit** — Read `skills/ios/ios-security-audit/SKILL.md` for full instructions.
```

For Claude Code, you can also symlink instead of copying:

```bash
mkdir -p /path/to/your-ios-project/.claude/skills/
ln -s "$(pwd)/skills/ios/ios-security-audit" /path/to/your-ios-project/.claude/skills/ios-security-audit
```

This way your local changes are immediately reflected without re-copying. Remove the symlink after testing.

## When to Use

- Reviewing iOS code for security vulnerabilities
- Pre-release security gate checks
- Auditing Keychain usage and data storage patterns
- Checking ATS configuration and certificate pinning
- Detecting hardcoded secrets, weak cryptography, or insecure randomness
- Reviewing Objective-C runtime attack surface
- Mapping compliance requirements (HIPAA, PCI DSS, GDPR, SOC 2)
- Validating WebView security and URL scheme handlers
