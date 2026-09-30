"""Preset questions are available without calling OpenAI or reading real secrets."""

from pathlib import Path
from types import SimpleNamespace

import openai
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from chat_logic import load_system_prompt
from manager_guidance import render_manager_questions

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "streamlit_app.py"
PLACEHOLDER = "{{MANAGER_PRESET_QUESTIONS}}"


def test_prompt_template_renders_manager_questions(tmp_path):
    path = tmp_path / "prompt.md"
    path.write_text(f"Review instructions\n{PLACEHOLDER}\nEnd", encoding="utf-8")
    loaded = load_system_prompt(path)
    assert PLACEHOLDER not in loaded
    assert loaded == f"Review instructions\n{render_manager_questions()}\nEnd"


@pytest.mark.parametrize("template", ["Instructions only", PLACEHOLDER * 2])
def test_required_questionnaire_refuses_missing_or_duplicate_placeholder(tmp_path, template):
    path = tmp_path / "prompt.md"
    path.write_text(template, encoding="utf-8")
    with pytest.raises(ValueError, match="exactly one manager-question placeholder"):
        load_system_prompt(path, require_manager_questions=True)


def test_plain_prompt_still_loads_without_questionnaire(tmp_path):
    path = tmp_path / "other_prompt.md"
    path.write_text("  Plain instructions\n", encoding="utf-8")
    assert load_system_prompt(path) == "Plain instructions"


@pytest.fixture
def fake_api(monkeypatch):
    class CallLog(list):
        finish_reason = None

    calls = CallLog()

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

        @staticmethod
        def create(**kwargs):
            calls.append(kwargs)
            if calls.finish_reason:
                from openai.types.chat import ChatCompletionChunk

                return iter([
                    ChatCompletionChunk(
                        id="synthetic", object="chat.completion.chunk", created=0,
                        model="test", choices=[{
                            "index": 0, "delta": {"content": "Partial review"},
                            "finish_reason": None,
                        }],
                    ),
                    ChatCompletionChunk(
                        id="synthetic", object="chat.completion.chunk", created=0,
                        model="test", choices=[{
                            "index": 0, "delta": {}, "finish_reason": calls.finish_reason,
                        }],
                    ),
                ])
            return iter(["Please provide your concept, SOPs, and hourly sales."])

    monkeypatch.setattr(openai, "OpenAI", FakeClient)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    st.cache_resource.clear()
    yield calls
    st.cache_resource.clear()


def make_app(key=""):
    app = AppTest.from_file(APP, default_timeout=30)
    app.secrets["OPENAI_API_KEY"] = key
    app.run()
    assert not app.exception
    return app


def test_questions_are_visible_even_without_an_api_key(fake_api):
    app = make_app()
    assert any(e.label == "Manager preset questions" for e in app.expander)
    assert render_manager_questions() in [m.value for m in app.markdown]
    assert len(app.error) == 1
    assert "No OpenAI API key" in app.error[0].value
    assert fake_api == []


def test_questions_match_api_prompt_and_reruns_make_no_requests(fake_api):
    app = make_app("test-key-not-a-credential")
    app.run()
    assert fake_api == []
    rendered = render_manager_questions()
    assert rendered in [m.value for m in app.markdown]
    app.chat_input[0].set_value("Ask the preset questions for a synthetic review.").run()
    assert not app.exception
    assert len(fake_api) == 1
    system_prompt = fake_api[0]["messages"][0]["content"]
    assert PLACEHOLDER not in system_prompt
    assert system_prompt.count(rendered) == 1
    assert app.session_state.messages[-1]["role"] == "assistant"


def test_clear_keeps_questions_without_resending_a_request(fake_api):
    app = make_app("test-key-not-a-credential")
    app.chat_input[0].set_value("Synthetic review.").run()
    assert len(fake_api) == 1
    next(b for b in app.button if b.label == "Clear conversation").click().run()
    assert not app.exception
    assert app.session_state.messages == []
    assert render_manager_questions() in [m.value for m in app.markdown]
    assert len(fake_api) == 1


def test_truncated_review_is_marked_in_ui_and_retained_context(fake_api):
    fake_api.finish_reason = "length"
    app = make_app("test-key-not-a-credential")
    app.chat_input[0].set_value("Synthetic large-roster review.").run()
    assert not app.exception
    assert any("incomplete" in warning.value.lower() for warning in app.warning)
    assert "incomplete" in app.session_state.messages[-1]["content"].lower()
    assert app.session_state.messages[-1]["content"].startswith("Partial review")
    assert len(fake_api) == 1


def test_sensitive_data_notice_is_visible_before_submission(fake_api):
    app = make_app()
    copy = " ".join(caption.value for caption in app.caption)
    assert "sent to OpenAI as supplied" in copy
    assert "Remove" in copy and "medical" in copy
