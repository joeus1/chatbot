"""Run the SessionStart autoprompt's shell test suite under pytest.

The hook is POSIX sh and its behaviour is asserted in sh, where the failure
modes actually live. This wrapper exists so `pytest` executes that suite:
a test nothing runs protects nothing, and the hook runs at the start of every
session in this repo.
"""

import subprocess
from pathlib import Path

SUITE = Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "session-prompt.test.sh"


def test_session_prompt_hook_suite():
    assert SUITE.is_file(), f"missing shell suite at {SUITE}"
    result = subprocess.run(
        ["sh", str(SUITE)], capture_output=True, text=True, timeout=180
    )
    assert result.returncode == 0, result.stdout + result.stderr
