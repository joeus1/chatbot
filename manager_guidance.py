"""Shared manager question catalog for the UI and review prompt."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ManagerQuestion:
    code: str
    question: str
    answers: str


BUSINESS_QUESTIONS: tuple[ManagerQuestion, ...] = (
    ManagerQuestion(
        "B1",
        "What is the concept, service-channel mix and each role's SOP quality/safety "
        "standard? Which SOP version and role training have been communicated?",
        "Concept; channels; roles; SOP/version date; training provided, or Unknown",
    ),
    ManagerQuestion(
        "B2",
        "What are the overall aggregate net sales and order counts for this review period? "
        "Give dates, source, currency and exclusions such as refunds, discounts, tax and tips.",
        "Period; aggregate net sales/orders; source; exclusions; missing data, or Unknown",
    ),
    ManagerQuestion(
        "B3",
        "What are sales and orders by local date/hour and service channel, in which timezone? "
        "Label each series actual or forecast and identify peaks, source and missing hours.",
        "Dated hourly sales/orders; channel mix; timezone; actual/forecast; source, or Unknown",
    ),
    ManagerQuestion(
        "B4",
        "What are the daypart clock times and minimum coverage by role/station in each "
        "daypart? Which operational qualifications are needed to open, close or cover it?",
        "Dayparts; stated station minimums; required qualifications, or Unknown",
    ),
    ManagerQuestion(
        "B5",
        "What practical station capacity and workload conditions have you observed? Include "
        "task complexity, equipment/stock, safety, support and break-coverage needs.",
        "Observed capacity/context; dated source; safety and break-coverage needs, or Unknown",
    ),
    ManagerQuestion(
        "B6",
        "Who is available on the bench for this period, in which confirmed roles and "
        "days/times? State approved availability or role limits only, without their reasons.",
        "First name/last initial; confirmed roles; available days/times; limits, or Unknown",
    ),
    ManagerQuestion(
        "B7",
        "What rest gap and consecutive-day limit do you want this schedule review to use? "
        "These review preferences do not establish a legal requirement.",
        "Rest hours; maximum consecutive scheduled days, or Unknown",
    ),
)

EMPLOYEE_QUESTIONS: tuple[ManagerQuestion, ...] = (
    ManagerQuestion(
        "Q1",
        "For <name>'s scheduled or bench role, which SOPs and training have been "
        "communicated, and which role sign-offs are confirmed?",
        "Role; SOP/version; training/sign-offs; dated source / Not observed / Not applicable",
    ),
    ManagerQuestion(
        "Q2",
        "Which assigned tasks has <name> demonstrated independently to SOP quality and "
        "safety standards, and which required support?",
        "Tasks; observed result; support; dates/source / Not observed / Not applicable",
    ),
    ManagerQuestion(
        "Q3",
        "In <name>'s peak task sample, what were the observation window/duration and "
        "communicated SOP service-time target, if any? What tasks were completed out of "
        "assigned opportunities, with what complexity, support and quality/safety result?",
        "Sample window/duration; completed/assigned opportunities; SOP timing; context; "
        "dates/source / Not observed / Not applicable",
    ),
    ManagerQuestion(
        "Q4",
        "In work samples attributable to <name>, how many eligible items met the accuracy "
        "SOP out of how many observed, and how many needed rework? What blockers were observed?",
        "Correct/observed eligible items; rework count; context; dates/source / Not observed / "
        "Not applicable",
    ),
    ManagerQuestion(
        "Q5",
        "Which assigned prep, service or handoff tasks did <name> complete by the SOP "
        "checkpoint during the paid shift, and what support or blockers were observed?",
        "Completed/assigned tasks; SOP checkpoint; context; dates/source / Not observed / "
        "Not applicable",
    ),
    ManagerQuestion(
        "Q6",
        "Which opening or closing checklist tasks has <name> demonstrated to SOP standard "
        "during the paid shift, independently or with stated support?",
        "Open/close tasks; checklist result; support; dates/source / Not observed / Not applicable",
    ),
    ManagerQuestion(
        "Q7",
        "Which other roles is <name> signed off to cover, and what specific training or "
        "mentoring tasks have you observed them complete to the SOP?",
        "Confirmed roles; observed mentoring tasks; dates/source / Not observed / Not applicable",
    ),
    ManagerQuestion(
        "Q8",
        "What approved availability, certification or role limits apply to <name> for this "
        "period? Give only the operational limit, never a personal, medical or leave reason.",
        "Limit and valid period, or None confirmed / Not observed / Not applicable",
    ),
    ManagerQuestion(
        "Q9",
        "What observed equipment, stock, workload, training or station-support barriers "
        "affected <name>'s assigned tasks, and what practical support could address them?",
        "Operational facts; support; dates/source / Not observed / Not applicable",
    ),
    ManagerQuestion(
        "Q10",
        "What is your observed job-related feedback about <name>, supported by which SOP "
        "task and dated example? What paid coaching/support and follow-up sample do you propose?",
        "Strength/concern; SOP/evidence; support; follow-up plan / Not observed / Not applicable",
    ),
)


def render_manager_questions() -> str:
    """Return the shared question tables shown to the manager and model."""
    sections = []
    for title, questions in (
        ("Business context — once per review", BUSINESS_QUESTIONS),
        ("Per-person observations — repeat for each person", EMPLOYEE_QUESTIONS),
    ):
        rows = [f"#### {title}", "", "| # | Question | Answers |", "|---|---|---|"]
        rows.extend(
            f"| {question.code} | {question.question} | {question.answers} |"
            for question in questions
        )
        sections.append("\n".join(rows))
    return "\n\n".join(sections)
