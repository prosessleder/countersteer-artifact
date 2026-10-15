# Confirm scoring fixtures

`confirm_scoring_cases.json` contains 13 selected cases and 52 final outputs
from Tim O’Brien’s independent fixed-vector confirm run of 14 October 2026.
AI assistance supported the evidence analysis and preparation. These inputs
characterize existing scorer behavior; they do not assess source-task quality
or provide a task-correctness or causal evaluation.

The run used the artifact at
[`26bd2db826614a8e60a0dd2eb373988a4c922f34`](https://github.com/markrussinovich/countersteer-artifact/tree/26bd2db826614a8e60a0dd2eb373988a4c922f34),
Qwen3-30B-A3B-Thinking-2507 revision
`144afc2f379b542fdd4e85a1fcd5e1f79112d95d`, and the shipped vectors. Source
records derive from NVIDIA’s
[Nemotron-RL-Agentic-Indirect-Prompt-Injection-v1](https://huggingface.co/datasets/nvidia/Nemotron-RL-Agentic-Indirect-Prompt-Injection-v1)
at revision `d738d4f361cc38bb4d7a42b9066776dade5332f5`, licensed CC BY 4.0.
The canonical samples include the artifact's reconstructed clean records and
injection templates. Preserve this attribution when redistributing the fixtures.

## Contents and limits

- `sample`: complete canonical sample, including system/user text, schemas,
  clean and attacked records, and declared attacker objective.
- `canonical_sample_sha256`: SHA-256 of Python `json.dumps(sample,
  ensure_ascii=False, sort_keys=True)` encoded as UTF-8.
- `final_output`: saved action-region text after the pre-opened Qwen thinking
  region; terminal/padding markers and surrounding whitespace are removed.
  Internal text and argument values are unchanged.
- `final_output_sha256`: SHA-256 of that exact UTF-8 string.
- `source_completion_sha256`: identity of the original raw completion before
  extraction. Full raw reasoning and native token arrays are not included.
- `native_eos`, `hit_cap`, `generated_tokens`, `max_new_tokens`: metadata retained
  from the native generation records, not inferred from display length.
- `expected`: frozen scorer results on the final action region. Influence was
  replayed using the existing scorer; it is not a newly defined metric.
- `full_run_no_action`: saved per-case no-action flags for the 96 clean and
  defended outputs, including cases outside the selected output fixtures.

Top-level provenance records the original bundle, canonical-sample and raw
completion-file hashes. Those hashes identify the private source evidence;
the full source files are not distributed here and are not needed to replay
the included scorer examples. The tests verify included content hashes and
current scorer behavior, not remote provenance or generation-time intervention.

## Regression coverage

Tests preserve existing pattern/literal matches, reasoning extraction, reference
scoreability and critical-argument comparison. The inspector exposes saved native
termination flags and paired no-action flags. Tests do not certify every harness's
reasoning-parser integration or rerun generation. No semantic judge or task-validity
annotations are included.
