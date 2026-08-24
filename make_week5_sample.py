"""Create the auditable Week 5 random sample and report skeletons from JSONL traces."""

import argparse
import json
import random
from pathlib import Path


REQUIRED_FIELDS = {
    "trace_id", "question", "prompt_version", "retrieved_chunks", "generation",
    "raw_output", "final_output", "threshold",
}


def load_traces(path):
    traces = []
    with Path(path).open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, 1):
            if not line.strip():
                continue
            trace = json.loads(line)
            missing = REQUIRED_FIELDS - trace.keys()
            if missing:
                raise ValueError(f"Line {line_number} is not replayable; missing {sorted(missing)}")
            traces.append(trace)
    if len(traces) < 20:
        raise ValueError(f"Need at least 20 traces; found {len(traces)}.")
    return traces


def short(text, limit=500):
    text = (text or "[none]").replace("\n", " ")
    return text if len(text) <= limit else text[:limit] + "..."


def main():
    parser = argparse.ArgumentParser(description="Create Week 5's seeded random sample.")
    parser.add_argument("--traces", default="traces/requests.jsonl")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output-dir", default="week5")
    args = parser.parse_args()

    traces = load_traces(args.traces)
    sample = random.Random(args.seed).sample(traces, 20)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "sample.json").write_text(json.dumps({
        "seed": args.seed, "population_size": len(traces),
        "trace_ids": [trace["trace_id"] for trace in sample],
    }, indent=2), encoding="utf-8")

    lines = [
        "# Week 5 — Open-coding notes",
        "",
        f"Seed: `{args.seed}`  ",
        f"Population: `{len(traces)}` traces  ",
        "Selection method: `random.Random(seed).sample(all_traces, 20)`.",
        "",
        "Do not change the app while completing the 20 observations below. Replace each bracketed line with one sentence stating only what you saw.",
        "",
        "## Seeded sample and observations",
        "",
    ]
    for number, trace in enumerate(sample, 1):
        lines.extend([
            f"### {number}. `{trace['trace_id']}`",
            f"Question: {short(trace['question'], 240)}",
            f"Final output: {short(trace['final_output'])}",
            "Observation: [Write one honest sentence describing what you saw.]",
            "",
        ])
    lines.extend([
        "## Replay evidence",
        "",
        f"Random replay target: `{sample[0]['trace_id']}` (selected from the same seeded sample).",
        "Run `python replay_trace.py --trace-file traces/requests.jsonl --trace-id <id>` and paste its original-versus-replayed output here.",
        "",
        "## Dated falsifiable prediction",
        "",
        "After clustering—not before—write one dated prediction with a baseline, exact change, and expected post-change percentage. Commit it before implementing that change, then paste the commit hash here.",
        "",
        "## Why a public benchmark would miss these modes",
        "",
        "[Write exactly three sentences after identifying the top three modes.]",
    ])
    (output_dir / "notes.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    taxonomy = """# Week 5 — Ranked failure taxonomy

Complete this only after open-coding all 20 traces in `notes.md`.

| Rank | Failure mode (plain language) | Count | Frequency | Severity | Example trace_id |
|---:|---|---:|---:|---|---|
| 1 | [name what happens] | [n] | [n/20%] | [poisons/ruins dish or merely annoys cook] | [id] |
| 2 | [name what happens] | [n] | [n/20%] | [severity] | [id] |
| 3 | [name what happens] | [n] | [n/20%] | [severity] | [id] |
| 4 | [name what happens] | [n] | [n/20%] | [severity] | [id] |
"""
    (output_dir / "taxonomy.md").write_text(taxonomy, encoding="utf-8")
    print(f"Wrote seeded sample and report skeletons to {output_dir}")


if __name__ == "__main__":
    main()
