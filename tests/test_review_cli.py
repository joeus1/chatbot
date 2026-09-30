"""The CLI must not report success for an incomplete review."""

from types import SimpleNamespace

import openai
import pytest

from scripts import run_review


@pytest.mark.parametrize("truncated_turn", [1, 2])
def test_cli_stops_with_nonzero_status_on_truncation(monkeypatch, tmp_path, capsys, truncated_turn):
    calls = []

    class FakeClient:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

        @staticmethod
        def create(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(
                message=SimpleNamespace(content="Synthetic reply"),
                finish_reason="length" if len(calls) == truncated_turn else "stop",
            )])

    monkeypatch.setattr(openai, "OpenAI", FakeClient)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-a-credential")
    schedule = tmp_path / "schedule.csv"
    schedule.write_text("Day,Start,End,Role,Person\nMon,09:00,17:00,Lead,Alex A.\n")
    answers = tmp_path / "answers.md"
    answers.write_text("Synthetic observations: Not observed.")
    assert run_review.main([str(schedule), str(answers)]) != 0
    assert "incomplete" in capsys.readouterr().err.lower()
    assert len(calls) == truncated_turn
