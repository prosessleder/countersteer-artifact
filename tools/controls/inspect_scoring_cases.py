#!/usr/bin/env python3
"""Inspect saved confirm examples without generation or changes to frozen scores.

This command imports the installed scorer dependencies but loads no model.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src import scoring  # noqa: E402

DEFAULT_FIXTURES = ROOT / "tests/fixtures/confirm_scoring_cases.json"


def inspect_observation(sample, clean_output, observation):
    """Score a saved final action region and expose separate outcome metadata."""
    output = observation["final_output"]
    calls = scoring.parse_tool_calls(output)
    agreement = scoring.behavioural_score(clean_output, output)
    influence = scoring.influence_score(sample, clean_output, output)
    metrics = {
        "asr": scoring.attack_influenced(sample, output),
        "strict_asr": scoring.attack_fired(sample, output),
        "influenced": influence["influenced"],
        "in_other_tool": influence["in_other_tool"],
        "scoreable": agreement["scoreable"],
        "structured_agreement": agreement.get("struct_exact"),
        "no_action": scoring.took_no_action(sample, output),
        "parsed_calls": calls,
    }
    # Use native termination metadata, never displayed/rectangular output length.
    capped = observation["hit_cap"]
    eos = observation["native_eos"]
    if capped and eos:
        raise ValueError("A native-EOS completion cannot also be capped")
    if capped:
        status = "capped_after_call" if calls else "capped_without_complete_call"
    elif eos:
        status = "complete_with_call" if calls else "complete_without_call"
    else:
        status = "unresolved_termination"
    return {
        "metrics": metrics,
        "completion_status": status,
        "hit_cap": capped,
        "native_eos": eos,
        # A cap cannot erase a known positive. Negative at a cap is unresolved.
        "unresolved_target_outcome": (capped or not eos) and not metrics["asr"],
    }


def no_action_transitions(clean, defended):
    """Preserve case identities even when no-action marginal counts are equal."""
    if clean.keys() != defended.keys():
        raise ValueError("No-action comparisons require identical sample IDs")
    return {
        "n": len(clean),
        "clean_no_action": sum(clean.values()),
        "defended_no_action": sum(defended.values()),
        "stopped_acting": sorted(k for k in clean if not clean[k] and defended[k]),
        "started_acting": sorted(k for k in clean if clean[k] and not defended[k]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--case", action="append", dest="case_ids", help="Repeat to select cases")
    parser.add_argument("--json", action="store_true", help="Emit existing metrics and completion metadata")
    args = parser.parse_args()
    fixtures = json.loads(args.fixtures.read_text())
    cases = {case["id"]: case for case in fixtures["cases"]}
    selected = args.case_ids or list(cases)
    missing = sorted(set(selected) - cases.keys())
    if missing:
        parser.error("Unknown case IDs: " + ", ".join(missing))
    rows = []
    for case_id in selected:
        case = cases[case_id]
        clean = case["arms"]["clean"]["final_output"]
        for arm, observation in case["arms"].items():
            rows.append({"case": case_id, "arm": arm,
                         **inspect_observation(case["sample"], clean, observation)})
    transitions = no_action_transitions(**fixtures["full_run_no_action"])
    result = {
        "scope": "Selected regression examples, not an efficacy estimate or task-correctness evaluation.",
        "observations": rows,
        "full_run_no_action_transitions": transitions,
    }
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    else:
        print(result["scope"])
        print("case       arm            ASR strict influence agreement status")
        for row in rows:
            m = row["metrics"]
            agreement = "excluded" if not m["scoreable"] else str(int(m["structured_agreement"]))
            print(f"{row['case']:10} {row['arm']:14} {int(m['asr']):3} {int(m['strict_asr']):6} "
                  f"{int(m['influenced']):9} {agreement:9} {row['completion_status']}")
        print("Full 96-case run no-action transitions: " + json.dumps(transitions))


if __name__ == "__main__":
    main()
