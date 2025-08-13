import os
import uuid
import asyncio
import streamlit as st

# OpenAI Agents SDK
from agents import Agent, Runner, SQLiteSession, function_tool

# =============================
# Settings
# =============================
API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5-nano")

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Agents SDK Playground",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 OpenAI Agents SDK - Streamlit Playground")
st.caption("Minimal chat UI to try Agents.")

# -----------------------------
# Helpers
# -----------------------------


@function_tool
def get_current_time() -> str:
  """Return the current UTC time in ISO 8601 format."""
  import datetime as _dt
  ts = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()
  return ts.replace("+00:00", "Z")


@st.cache_resource(show_spinner=False)
def make_agent(name: str, instructions: str, model: str, use_time_tool: bool) -> Agent:
  tools = [get_current_time] if use_time_tool else []
  return Agent(name=name, instructions=instructions, model=model, tools=tools)


@st.cache_resource(show_spinner=False)
def make_session(session_id: str) -> SQLiteSession:
  return SQLiteSession(session_id)


def run_async_task(agent: Agent, prompt: str, session: SQLiteSession):
  """
  Execute async task safely in Streamlit environment.
  """
  try:
    return asyncio.run(Runner.run(agent, input=prompt, session=session))
  except RuntimeError as e:
    # Check if it's the specific event loop error we can handle
    if "cannot be called from a running event loop" in str(e):
      # Create new event loop to avoid conflict with existing loop
      loop = asyncio.new_event_loop()
      try:
        return loop.run_until_complete(Runner.run(agent, input=prompt, session=session))
      finally:
        loop.close()
    else:
      # Re-raise unexpected RuntimeErrors
      raise


# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Settings")

if not API_KEY:
  st.sidebar.error(
      "Set OPENAI_API_KEY in your environment before chatting.")
  st.stop()

# Session management
if "session_id" not in st.session_state:
  st.session_state.session_id = str(uuid.uuid4())

if st.sidebar.button("🔄 New session", help="Start a fresh conversation (new session id)"):
  st.session_state.session_id = str(uuid.uuid4())
  st.session_state.messages = []

st.sidebar.write("**Session ID**")
st.sidebar.code(st.session_state.session_id)

# Behavior
use_time_tool = st.sidebar.toggle("Enable time tool", value=True,
                                  help="Adds a simple function tool that returns the current time")

# System / instructions
default_instructions = "You are a concise, helpful assistant."
instructions = st.sidebar.text_area(
    "System instructions", value=default_instructions, height=120)

# Agent name
agent_name = st.sidebar.text_input("Agent name", value="Assistant")

# -----------------------------
# Build agent + session
# -----------------------------
agent = make_agent(agent_name, instructions, MODEL, use_time_tool)
session = make_session(st.session_state.session_id)

# Chat history for UI only
if "messages" not in st.session_state:
  # messages: list[tuple[str, str]] where each tuple = (role, content)
  st.session_state.messages = []

# Render past messages
for role, content in st.session_state.messages:
  with st.chat_message(role):
    st.markdown(content)

# Input box
prompt = st.chat_input("Type a message…", disabled=not API_KEY)

if prompt:
  # Show user message immediately
  st.session_state.messages.append(("user", prompt))
  with st.chat_message("user"):
    st.markdown(prompt)

  # Run the agent
  with st.spinner("Thinking..."):
    try:
      result = run_async_task(agent, prompt, session)
      reply = result.final_output or "(No output)"
    except Exception as e:
      reply = f"⚠️ Error: {type(e).__name__}: {e}"

  st.session_state.messages.append(("assistant", reply))
  with st.chat_message("assistant"):
    st.markdown(reply)

# Footer tips
st.markdown(
    """
    ---
    **Tips**
    - Use the sidebar to change system instructions.
    - Toggle the time tool and ask: *"What time is it?"* to see tool calling.
    - Click **New session** to start a fresh conversation with separate memory.
    """
)
