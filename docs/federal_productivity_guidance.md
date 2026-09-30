# Manager observation guidance

The questionnaire supports a manager's coaching conversation and review of an existing
restaurant schedule. It separates business demand (concept SOPs, aggregate sales, hourly
orders and channel mix) from attributable employee work samples. Store sales and scheduled
hours do not establish an individual's productivity or revenue contribution.

`manager_guidance.py` is the shared question catalog shown in the app and inserted into
`prompts/schedule_review.md`. Business questions B1–B7 establish the context once. Questions
Q1–Q10 gather neutral observations for each person. Every person question permits
`Not observed`; insufficient evidence stays unknown. Work samples need dates, a source,
an opportunity count, role/task complexity, operational context and SOP quality/safety
checks. Pace samples also need a limited observation window/duration and communicated
SOP timing if available; this is not collection of whole-shift actual hours or timeclock
records. Separate indicators never become a composite score, ranking or worker quota.

The app may identify operational coverage and confirmed qualification gaps, propose
schedule changes and suggest training or support. It must not use observations to allocate
individual hours or recommend pay changes, discipline or dismissal. Preserve existing
employee total scheduled hours where feasible. These limits are product safeguards, not
a claim that federal law categorically prohibits all employee ratings or software-assisted
employment decisions.

## Federal reference scope

This is federal-law-informed coaching guidance, not a legal-compliance determination.
Which federal obligations apply depends on employer coverage, worker status and the
facts. State/local laws, employment agreements and collective bargaining agreements may
add protections; this app does not check them. A manager and their qualified advisor
handle legal questions outside the review.

Official references checked September 29, 2026:

- [EEOC: conducting performance evaluations](https://www.eeoc.gov/employers/small-business/5-im-conducting-performance-evaluations)
  explains communicating standards, applying them consistently and supporting evaluations
  with relevant facts. The questionnaire asks about communicated SOPs and dated examples,
  rather than personality judgments or recollections of attendance.
- [EEOC: employment tests and selection procedures](https://www.eeoc.gov/laws/guidance/employment-tests-and-selection-procedures)
  explains federal discrimination risks when employment procedures are used for decisions.
  The app does not certify any metric's validity or fairness for an employment decision.
- [EEOC: performance/conduct standards and employees with disabilities](https://www.eeoc.gov/laws/guidance/applying-performance-and-conduct-standards-employees-disabilities)
  addresses job-related standards and reasonable accommodation duties. Record an approved
  operational scheduling limit only; do not request a diagnosis, medical history, disability
  status or the reason for a limit. The app does not decide accommodation obligations.
- [DOL: FLSA hours worked](https://www.dol.gov/agencies/whd/fact-sheets/22-flsa-hours-worked)
  explains compensable work and treatment of breaks. The app must never encourage off-clock
  work, skipped breaks or an unpaid work task to improve a productivity indicator. It does
  not assess actual hours worked or payroll.
- [DOL: FMLA employee protections](https://www.dol.gov/agencies/whd/fact-sheets/28a-fmla-employee-protections)
  explains protections against interference and retaliation for covered FMLA activity.
  The app excludes attendance ratings and must not penalize protected leave or protected
  time in its observations or suggestions.
- [NLRB: protected concerted activity](https://www.nlrb.gov/about-nlrb/rights-we-protect/the-law/employees/concerted-activity)
  explains protections for covered employees acting together about working conditions.
  Do not request union status or protected-activity details, or treat such activity as
  an employee productivity problem.

Do not input protected traits, medical information, reasons for leave or protected activity.
If volunteered, the model is instructed to omit it from the review and not use it. The
existing short-name, pay-data and unsupported-upload boundaries still apply. Aggregate
business sales are allowed; individual wages, payroll and timeclock data are excluded.

## Limits of the implementation

The application inserts the same immutable catalog into the UI and system prompt and
keeps its existing bounded chat history. It does not compute or persist employee scores,
make employment decisions or add a connection to any HR, payroll or scheduling service.
Observation interpretation and sensitive-data omission are model instructions; they are
not a deterministic legal review or guaranteed redaction of submitted content. Managers
should provide only the requested business context and neutral job observations.
