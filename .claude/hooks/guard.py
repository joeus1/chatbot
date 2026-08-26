#!/usr/bin/env python3
"""HalalWay Toolkit PreToolUse guard.

Blocks (exit 2) two classes of accidents before they happen:
  1. Destructive shell commands (recursive force-deletes of roots, force
     pushes, curl|sh, world-writable chmod).
  2. Writing likely-real secrets into the repo, or creating an .env-style
     file that git would track.

Reads the hook payload from stdin. Fails open (exit 0) on any internal
error so a broken guard can never lock up a session.
"""
import json
import re
import subprocess
import sys

DANGEROUS_BASH = [
    # rm -rf (any flag spelling) aimed at /, ~, $HOME, ., .. or a bare *
    (r"\brm\s+(-[a-zA-Z]+\s+)*-[a-zA-Z]*[rR][a-zA-Z]*[fF][a-zA-Z]*\s+(--\s+)?([\"']?)(/|~|\$HOME|\.\.?|\*)\3(\s|$)",
     "Recursive force-delete of a root path. Name the exact directory you mean instead."),
    (r"\brm\s+(-[a-zA-Z]+\s+)*-[a-zA-Z]*[fF][a-zA-Z]*[rR][a-zA-Z]*\s+(--\s+)?([\"']?)(/|~|\$HOME|\.\.?|\*)\3(\s|$)",
     "Recursive force-delete of a root path. Name the exact directory you mean instead."),
    # force push without lease
    (r"\bgit\s+push\b(?![^\n]*--force-with-lease)[^\n]*(\s--force\b|\s-f\b)",
     "Force push blocked. Use --force-with-lease, and only on branches you own - never main/master."),
    # pipe-from-internet-to-shell
    (r"\b(curl|wget)\b[^\n|;&]*\|\s*(sudo\s+)?(ba|z|da)?sh\b",
     "Piping a download straight into a shell. Download to a file, inspect it, then run it."),
    # world-writable
    (r"\bchmod\s+(-[a-zA-Z]+\s+)*777\b",
     "chmod 777 makes files world-writable. Use the narrowest permission that works."),
    # hard reset that throws away local work on shared branches
    (r"\bgit\s+reset\s+--hard\s+origin/(main|master)\b",
     "Hard reset to origin/main discards local commits. Prefer merge/rebase, or confirm explicitly."),
]

SECRET_PATTERNS = [
    (r"sk-[A-Za-z0-9_\-]{20,}", "an OpenAI/Anthropic-style API key"),
    (r"sk_live_[A-Za-z0-9]{10,}", "a live Stripe secret key"),
    (r"rk_live_[A-Za-z0-9]{10,}", "a live Stripe restricted key"),
    (r"AKIA[0-9A-Z]{16}", "an AWS access key id"),
    (r"ghp_[A-Za-z0-9]{36}", "a GitHub personal access token"),
    (r"github_pat_[A-Za-z0-9_]{22,}", "a GitHub fine-grained token"),
    (r"xox[baprs]-[A-Za-z0-9\-]{10,}", "a Slack token"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "a private key block"),
]

ENV_FILE = re.compile(r"(^|/)(\.env(\.[A-Za-z0-9_.-]+)?|secrets\.toml)$")
EXEMPT_FILE = re.compile(r"\.(example|sample|template)$|(^|/)guard\.py$")


def block(message: str) -> None:
    print(f"BLOCKED by HalalWay Toolkit guard: {message}", file=sys.stderr)
    sys.exit(2)


def check_bash(command: str) -> None:
    for pattern, message in DANGEROUS_BASH:
        if re.search(pattern, command):
            block(message)


def is_git_ignored(path: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", path],
            capture_output=True, timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return True  # can't tell -> fail open


def check_write(file_path: str, content: str) -> None:
    if EXEMPT_FILE.search(file_path):
        return
    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, content):
            block(
                f"This write to {file_path} contains what looks like {label}. "
                "Secrets belong in environment variables or a gitignored secrets file. "
                "If this value is real, treat it as leaked and rotate it."
            )
    if ENV_FILE.search(file_path) and not is_git_ignored(file_path):
        block(
            f"{file_path} is an env/secrets file that git does NOT ignore. "
            "Add it to .gitignore first, then write it."
        )


def main() -> None:
    payload = json.load(sys.stdin)
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}

    if tool == "Bash":
        check_bash(tool_input.get("command", "") or "")
    elif tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        content = (
            (tool_input.get("content") or "")
            + "\n" + (tool_input.get("new_string") or "")
            + "\n" + "\n".join(
                (edit or {}).get("new_string", "")
                for edit in (tool_input.get("edits") or [])
            )
        )
        check_write(tool_input.get("file_path", "") or "", content)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # never break the session because the guard broke
