# 💬 Chatbot

A Streamlit chat app backed by the OpenAI API: secrets-based key handling,
bounded history, streaming responses, and friendly error handling.

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

### Development

Model, history bound, and token limits are constants at the top of
`streamlit_app.py`. Pure message/error logic lives in `chat_logic.py` and is
covered by unit tests:

```
$ pip install -r requirements-dev.txt
$ python -m pytest
```
