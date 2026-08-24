"""Replay a generation directly from a saved Week 5 trace; no vector store is read."""

import argparse
import json
from pathlib import Path

from huggingface_hub import InferenceClient
from hf_config import ensure_hf_token


def find_trace(path, trace_id):
    with Path(path).open(encoding="utf-8") as file:
        for line in file:
            trace = json.loads(line)
            if trace.get("trace_id") == trace_id:
                return trace
    raise ValueError(f"Trace {trace_id} was not found in {path}")


def main():
    parser = argparse.ArgumentParser(description="Replay one saved trace from its prompt and generation settings.")
    parser.add_argument("--trace-file", default="traces/requests.jsonl")
    parser.add_argument("--trace-id", required=True)
    parser.add_argument("--token", default=None)
    args = parser.parse_args()

    trace = find_trace(args.trace_file, args.trace_id)
    prompt = trace.get("prompt")
    if not prompt:
        print("This trace did not reach generation (no prompt/raw output); its final output was produced by the threshold/no-results guard.")
        print(f"Original final output: {trace['final_output']}")
        return

    generation = trace["generation"]
    client = InferenceClient(token=args.token or ensure_hf_token())
    response = client.chat.completions.create(
        model=generation["model"],
        messages=[{"role": "user", "content": prompt}],
        **generation["params"],
    )
    replayed = response.choices[0].message.content.strip()
    print(f"Trace ID: {trace['trace_id']}")
    print(f"Prompt version: {trace['prompt_version']}")
    print(f"Model and params: {json.dumps(generation)}")
    print("\nORIGINAL RAW OUTPUT:\n" + (trace.get("raw_output") or "[none]"))
    print("\nREPLAYED OUTPUT:\n" + replayed)
    print("\nExact match: " + str(replayed == trace.get("raw_output")))


if __name__ == "__main__":
    main()
