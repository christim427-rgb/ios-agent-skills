# ios-logging Benchmark (Opus 4.6)

## Summary

| Config | Pass | Total | Rate |
|--------|------|-------|------|
| **With Skill** | 57 | 58 | 98.3% |
| **Without Skill** | 33 | 58 | 56.9% |
| **Delta** | | | **+41.4%** |

## By Reference

| Reference | With Skill | Without Skill | Delta |
|-----------|-----------|--------------|-------|
| crash-sdk-integration | 100.0% | 63.6% | +36.4% |
| enterprise-patterns | 91.7% | 66.7% | +25.0% |
| logger-setup | 100.0% | 63.6% | +36.4% |
| metrickit | 100.0% | 25.0% | +75.0% |
| objc-exceptions | 100.0% | 100.0% | +0.0% |
| pii-compliance | 100.0% | 25.0% | +75.0% |
| silent-failures | 100.0% | 46.2% | +53.8% |

## Per Eval

| Eval | Reference | With Skill | Without Skill | Delta |
|------|-----------|-----------|--------------|-------|
| silent-failures-simple | silent-failures | 100.0% | 25.0% | +75.0% |
| silent-failures-medium | silent-failures | 100.0% | 66.7% | +33.3% |
| silent-failures-complex | silent-failures | 100.0% | 50.0% | +50.0% |
| logger-setup-simple | logger-setup | 100.0% | 75.0% | +25.0% |
| logger-setup-medium | logger-setup | 100.0% | 100.0% | +0.0% |
| logger-setup-complex | logger-setup | 100.0% | 25.0% | +75.0% |
| crash-sdk-simple | crash-sdk-integration | 100.0% | 33.3% | +66.7% |
| crash-sdk-medium | crash-sdk-integration | 100.0% | 50.0% | +50.0% |
| crash-sdk-complex | crash-sdk-integration | 100.0% | 100.0% | +0.0% |
| enterprise-simple | enterprise-patterns | 66.7% | 33.3% | +33.4% |
| enterprise-medium | enterprise-patterns | 100.0% | 75.0% | +25.0% |
| enterprise-complex | enterprise-patterns | 100.0% | 80.0% | +20.0% |
| metrickit-simple | metrickit | 100.0% | 25.0% | +75.0% |
| objc-exceptions-simple | objc-exceptions | 100.0% | 100.0% | +0.0% |
| pii-compliance-simple | pii-compliance | 100.0% | 25.0% | +75.0% |
