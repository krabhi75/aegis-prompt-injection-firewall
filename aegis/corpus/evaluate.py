"""Attack / benign corpus evaluation for D2 reliability proof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from firewall.engine import AegisFirewall
from firewall.models import GateDecision

ROOT = Path(__file__).resolve().parent


def _load_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for folder, label in (("benign", "benign"), ("malicious", "malicious")):
        for path in sorted((ROOT / folder).glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_file"] = path.name
            data["_label"] = label
            cases.append(data)
    return cases


def evaluate_corpus() -> dict[str, Any]:
    fw = AegisFirewall()
    cases = _load_cases()
    tp = fp = tn = fn = 0
    by_attack: dict[str, dict[str, int]] = {}
    details = []

    for i, case in enumerate(cases):
        session = f"corpus-{i}-{case['_file']}"
        verdict = fw.scan(session, case.get("user_message", ""), case.get("attachments"))
        predicted_bad = verdict.decision != GateDecision.ALLOW
        actual_bad = case["_label"] == "malicious"

        if predicted_bad and actual_bad:
            tp += 1
        elif predicted_bad and not actual_bad:
            fp += 1
        elif not predicted_bad and not actual_bad:
            tn += 1
        else:
            fn += 1

        expected = case.get("expected_attacks") or []
        for a in expected:
            by_attack.setdefault(a, {"hit": 0, "total": 0})
            by_attack[a]["total"] += 1
            detected = {x.value for x in verdict.attack_types}
            if a in detected or predicted_bad:
                by_attack[a]["hit"] += 1

        details.append(
            {
                "file": case["_file"],
                "label": case["_label"],
                "decision": verdict.decision.value,
                "risk": verdict.risk_score,
                "attacks": [a.value for a in verdict.attack_types],
                "ok": predicted_bad == actual_bad,
            }
        )

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    accuracy = (tp + tn) / len(cases) if cases else 0.0

    return {
        "n": len(cases),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "accuracy": round(accuracy, 4),
        "by_attack": by_attack,
        "details": details,
        "claim": "F3/D2",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate_corpus()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"Corpus n={result['n']}  precision={result['precision']:.3f}  "
            f"recall={result['recall']:.3f}  f1={result['f1']:.3f}  "
            f"accuracy={result['accuracy']:.3f}"
        )
        for attack, stats in result["by_attack"].items():
            rate = stats["hit"] / stats["total"] if stats["total"] else 0
            print(f"  - {attack}: {stats['hit']}/{stats['total']} ({rate:.0%})")


if __name__ == "__main__":
    main()
