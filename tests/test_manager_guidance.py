"""The visible questionnaire and prompt share a stable, immutable catalog."""

from dataclasses import FrozenInstanceError

import pytest

from manager_guidance import (
    BUSINESS_QUESTIONS,
    EMPLOYEE_QUESTIONS,
    render_manager_questions,
)


def test_question_codes_are_unique_and_stable_for_manager_answers():
    codes = [question.code for question in BUSINESS_QUESTIONS + EMPLOYEE_QUESTIONS]
    assert codes == [f"B{i}" for i in range(1, 8)] + [f"Q{i}" for i in range(1, 11)]
    assert len(codes) == len(set(codes))


def test_manager_question_records_and_collections_cannot_be_changed_on_reruns():
    assert BUSINESS_QUESTIONS and EMPLOYEE_QUESTIONS
    assert isinstance(BUSINESS_QUESTIONS, tuple)
    assert isinstance(EMPLOYEE_QUESTIONS, tuple)
    with pytest.raises(FrozenInstanceError):
        EMPLOYEE_QUESTIONS[0].answers = "Always / Rarely"
    with pytest.raises(TypeError):
        EMPLOYEE_QUESTIONS[0] = BUSINESS_QUESTIONS[0]


def test_renderer_keeps_every_answerable_row_once_and_in_catalog_order():
    rendered = render_manager_questions()
    rows = [line for line in rendered.splitlines() if line.startswith(("| B", "| Q"))]
    questions = BUSINESS_QUESTIONS + EMPLOYEE_QUESTIONS
    assert questions
    assert len(rows) == len(questions)
    for row, question in zip(rows, questions, strict=True):
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        assert cells == [question.code, question.question, question.answers]
    assert render_manager_questions() == rendered


def test_every_person_question_can_be_left_unknown_without_an_employee_rating():
    assert EMPLOYEE_QUESTIONS
    assert all("Not observed" in question.answers for question in EMPLOYEE_QUESTIONS)
    assert all("<name>" in question.question for question in EMPLOYEE_QUESTIONS)
