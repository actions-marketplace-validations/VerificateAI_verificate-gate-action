"""Contract tests for gate.py verdict classification (no network). Run: python test_gate.py"""
import os
import sys

os.environ.setdefault("GITHUB_REPOSITORY", "example/repo")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gate  # noqa: E402

fails = []


def check(name, cond):
    print(("  OK   " if cond else "  FAIL ") + name)
    if not cond:
        fails.append(name)


quota = {"valid": False, "score": 0, "validation_type": "quota", "provider": "quota-gate",
         "issues": ["[quota] You've used all 25 free validations."], "suggestions": ["Start a free trial at https://verificate.ai/auth/signup"],
         "quota": {"tier": "free", "used": 25, "limit": 25, "reason": "free_limit"}}
badkey = dict(quota, quota={"tier": "key", "reason": "invalid_key"})
unreviewed = {"valid": False, "score": 100.0, "review_unavailable": True, "protection": {"vetoed": False}, "issues": ["[gate] high|review_unavailable|..."]}
veto = {"valid": False, "score": 0, "protection": {"vetoed": True, "vetoed_by": ["code_reality_gate"]}, "issues": ["[code_reality_gate] Mock implementation detected"]}
rejected = {"valid": False, "score": 41.0, "protection": {"vetoed": False}, "issues": ["[llm] critical|L2|SQL injection"]}
approved = {"valid": True, "score": 92.0, "protection": {"vetoed": False}, "issues": []}

for name, obj, kind in (("exhausted free tier", quota, "access"), ("invalid / expired key", badkey, "access"),
                        ("gate-side review timeout", unreviewed, "review")):
    m = gate._not_a_verdict(obj)
    check(f"{name} is NOT a verdict on the code (never blocks a merge)", bool(m) and m["_unavailable"] and m["kind"] == kind)
check("an invalid key is distinguished from an exhausted quota", gate._not_a_verdict(badkey)["reason"] == "invalid_key")
for name, obj in (("a deterministic veto", veto), ("a model rejection", rejected), ("an approval", approved)):
    check(f"{name} IS a verdict and is passed through untouched", gate._not_a_verdict(obj) is None)
check("junk input never crashes the classifier", gate._not_a_verdict(None) is None and gate._not_a_verdict([1]) is None)

print("\nGATE ACTION CONTRACT: " + ("FAILED %d" % len(fails) if fails else "PASSED"))
sys.exit(1 if fails else 0)
