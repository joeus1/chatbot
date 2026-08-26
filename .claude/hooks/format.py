#!/usr/bin/env python3
"""HalalWay Toolkit PostToolUse auto-format.

Runs `ruff format` on the Python file a Write/Edit just touched, so formatting
drift never reaches CI. Fail-open by design: any internal error, missing tool,
or non-Python target exits 0 and changes nothing. PostToolUse cannot block the
edit - this only tidies after it.
"""
import json
import shutil
import subprocess
import sys


def main() -> None:
    payload = json.load(sys.stdin)
    if payload.get("tool_name") not in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        return
    file_path = (payload.get("tool_input") or {}).get("file_path", "") or ""
    if not file_path.endswith(".py"):
        return
    if shutil.which("ruff") is None:
        return
    subprocess.run(
        ["ruff", "format", "--quiet", file_path],
        capture_output=True,
        timeout=30,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
