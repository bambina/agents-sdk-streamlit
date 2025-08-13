# 🤖 OpenAI Agents SDK - Streamlit Playground

A minimal chat UI built with Streamlit using the OpenAI Agents SDK.

Streamlit is an open-source Python framework to build interactive data apps. Unlike a game engine, Streamlit does not run in an event loop. 
Instead, it executes the entire Python script from top to bottom each time the app is opened or the user interacts with it (e.g., clicking a button, entering text, or triggering a rerender).
This makes it well-suited for building PoCs and prototypes.  
`st.session_state` allows variables and data to persist across reruns.

## Environment Variables

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_DEFAULT_MODEL="gpt-5-nano"  # optional
```

## How to Run (with uv)

```bash
git clone <repository-url>
cd <repository-name>

# Install uv if needed (macOS/Homebrew)
brew install uv

# Create and activate a virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install streamlit openai-agents

# Run the app
streamlit run app.py
```

The app will be available at: http://localhost:8501

---

## References

- [App model summary](https://docs.streamlit.io/get-started/fundamentals/summary)
- [Streamlit's client-server architecture](https://docs.streamlit.io/develop/concepts/architecture/architecture)
