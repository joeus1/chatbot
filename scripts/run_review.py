"""Run the Schedule Review prompt end to end from the command line.

Drives the same code path as the Streamlit app (prompt file, upload
conversion, bounded history) without the UI, so a review can be executed and
read in a terminal or captured to a file. Two turns: the schedule upload,
then the manager's intake facts and answers.

    OPENAI_API_KEY=... python scripts/run_review.py examples/demo_schedule.csv examples/demo_answers.md
    python scripts/run_review.py --dry-run examples/demo_schedule.csv examples/demo_answers.md

--dry-run prints the messages that would be sent and makes no API call.
The key comes from the environment only; it is never read from a file here.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from chat_logic import (  # noqa: E402 - path set above
    append_message,
    build_api_messages,
    load_system_prompt,
    upload_to_turn,
)

MODEL = "gpt-4o"
MAX_HISTORY_TURNS = 20
MAX_COMPLETION_TOKENS = 4096
PROMPT_PATH = ROOT / "prompts" / "schedule_review.md"


def describe(messages):
    for m in messages:
        content = m["content"]
        if isinstance(content, list):
            kinds = ", ".join(part["type"] for part in content)
            text = next((p["text"] for p in content if p["type"] == "text"), "")
            print(f"--- {m['role']} [{kinds}]\n{text[:400]}{'…' if len(text) > 400 else ''}\n")
        else:
            print(f"--- {m['role']}\n{content[:400]}{'…' if len(content) > 400 else ''}\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("schedule", type=Path, help="schedule file: csv, tsv, txt, md, xlsx, png, jpg, webp")
    parser.add_argument("answers", type=Path, help="text file with the intake facts and Q1-Q7 answers")
    parser.add_argument("--dry-run", action="store_true", help="print the payload, make no API call")
    parser.add_argument("--model", default=MODEL)
    args = parser.parse_args(argv)

    system_prompt = load_system_prompt(PROMPT_PATH)
    history = []
    content, display = upload_to_turn(args.schedule.name, args.schedule.read_bytes())
    append_message(history, "user", content, display=display)
    answers = args.answers.read_text(encoding="utf-8").strip()

    if args.dry_run:
        print(f"# dry run: model {args.model}, prompt {len(system_prompt)} chars\n")
        describe(build_api_messages(history, system_prompt, MAX_HISTORY_TURNS))
        print("--- user (turn 2, sent after the read-back)\n" + answers[:400] + "\n")
        return 0

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("OPENAI_API_KEY is not set; use --dry-run to see the payload.", file=sys.stderr)
        return 2
    from openai import OpenAI  # noqa: PLC0415 - only needed for a live run

    client = OpenAI(api_key=api_key)

    def reply():
        response = client.chat.completions.create(
            model=args.model,
            messages=build_api_messages(history, system_prompt, MAX_HISTORY_TURNS),
            max_tokens=MAX_COMPLETION_TOKENS,
        )
        text = response.choices[0].message.content or ""
        append_message(history, "assistant", text)
        return text

    print(f"# {display}\n")
    print("## Turn 1: read-back\n")
    print(reply(), "\n")
    append_message(history, "user", answers)
    print("## Turn 2: review\n")
    print(reply())
    return 0


if __name__ == "__main__":
    sys.exit(main())
