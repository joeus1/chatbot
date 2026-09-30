# 📋 PrimeOps Schedule Review

A Streamlit app backed by the OpenAI API. A restaurant manager uploads the
schedule they already made, answers seven business-context questions and ten
preset questions about each person, and gets findings, a proposed fix and
coaching guidance. Questions use concept SOPs, aggregate sales and hourly demand
alongside dated, attributable work samples; store sales do not establish an
individual's productivity. It is not a payroll tool: no
payroll or timeclock analysis is included, and people are named by first
name and last initial only.

Remove payroll, medical/protected personal details and unnecessary identifiers before
submission. Answers and uploads are sent to OpenAI as supplied and held in the review's
session; input is not automatically redacted. Long replies that reach the output limit
are marked incomplete; continue the review or use a smaller roster before acting on it.

The system prompt is `prompts/schedule_review.md`. It is a document, not a
constant: read it before changing what the app does. `manager_guidance.py` is
the canonical B1–B7 / Q1–Q10 question catalog, shown in the app and inserted
into the prompt by `chat_logic.load_system_prompt`. Federal reference sources
and limits are in `docs/federal_productivity_guidance.md`. Observations support
coaching and operational coverage review; unknown evidence stays unknown, and
the app does not score or rank employees or recommend adverse employment actions.
This guidance does not determine legal compliance.

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Configure your OpenAI API key

   ```
   $ cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # then edit .streamlit/secrets.toml and set OPENAI_API_KEY
   ```

   `.streamlit/secrets.toml` is gitignored and must stay that way. Setting
   the `OPENAI_API_KEY` environment variable works too. On Streamlit
   Community Cloud, use the app's Secrets UI.

3. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

4. Upload a schedule from the sidebar (CSV, TSV, TXT, XLSX, or a PNG/JPG/WEBP
   photo or screenshot), or paste it into the chat. The file is sent to OpenAI
   for the review as supplied and held in this review's session; only its name appears in the
   transcript. PDF is not supported yet.

### Running the prompt from the command line

`scripts/run_review.py` drives the same prompt and upload code as the app
without the UI: the schedule upload as turn one, the intake facts and answers
as turn two, both replies printed. `examples/` holds a synthetic schedule and
answer file that exercise the business-context questions, individual work
samples, unknown evidence, naming, pay-column and unreadable-cell rules.

```
$ python scripts/run_review.py --dry-run examples/demo_schedule.csv examples/demo_answers.md
$ OPENAI_API_KEY=... python scripts/run_review.py examples/demo_schedule.csv examples/demo_answers.md
```

### Development

Model (`gpt-4o`; it must accept image input for photo uploads), history
bound, and token limits are constants at the top of `streamlit_app.py`. Pure message, upload and error logic lives in
`chat_logic.py` and is covered by unit tests:

```
$ pip install -r requirements-dev.txt
$ python -m pytest
```
