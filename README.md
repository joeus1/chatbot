# 📋 PrimeOps Schedule Review

A Streamlit app backed by the OpenAI API. A restaurant manager uploads the
schedule they already made, answers seven preset questions about each person,
and gets findings, a proposed fix and feedback. It is not a payroll tool: no
pay, hours worked or timeclock data is read, and people are named by first
name and last initial only.

The system prompt is `prompts/schedule_review.md`. It is a document, not a
constant: read it before changing what the app does. Its design and a
hand-worked example live in the platform repo at
`primeops-aei/docs/product/schedule_brain/`; keep the two copies the same.

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
   for the review and is not stored by the app; only its name appears in the
   transcript. PDF is not supported yet.

### Development

Model, history bound, and token limits are constants at the top of
`streamlit_app.py`. Pure message, upload and error logic lives in
`chat_logic.py` and is covered by unit tests:

```
$ pip install -r requirements-dev.txt
$ python -m pytest
```
