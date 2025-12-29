import streamlit as st
import os
import time
from dotenv import load_dotenv
from google import genai
from ai_engine import get_gemini_response, get_mock_response

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# -- UI Setup
st.set_page_config(page_title="My AI App", page_icon="TK")
st.title("Gemini based Chat")

# -- Initialize Session State
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""


# -- Sidebar (Mode, Temp, Mock switch)
with st.sidebar:
    st.title("Settings")
    mode = st.selectbox(
        "AI MODE",
        (
            "Casual Assistant",
            "Professional Interviewer",
            "English Teacher",
            "Code Reviewer",
        ),
        disabled=st.session_state.is_generating,
    )
    temp_value = st.sidebar.slider(
        "Creativity",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.1,
        # disable during generating
        disabled=st.session_state.is_generating,
    )
    use_mock = st.checkbox(
        "Enable Mock Mode", value=False, disabled=st.session_state.is_generating
    )
    if st.button("Clear History", disabled=st.session_state.is_generating):
        st.session_state.chat_history = []
        st.rerun()

# -- Logic for System Instructions
match mode:
    case "Professional Interviewer":
        instructions = "You are senior tech interviewer..."
    case "English Teacher":
        instructions = "You are an English teacher..."
    case "Code Reviewer":
        instructions = "You are an excellent code reviewer."
    case _:  # Default value
        instructions = "You are a helpful assistant."

# Mode Switch Logic
if "current_mode" not in st.session_state:
    st.session_state.current_mode = mode

if mode != st.session_state.current_mode:
    st.session_state.chat_history = []
    st.session_state.current_mode = mode
    st.rerun()

# -- Display History
for msg in st.session_state.chat_history:
    display_role = "assistant" if msg["role"] == "model" else msg["role"]
    with st.chat_message(display_role):
        st.markdown(msg["parts"][0]["text"])

# -- User Input & AI Response
if prompt := st.chat_input(
    "Ask me anything...", disabled=st.session_state.is_generating
):
    st.session_state.is_generating = True
    st.session_state.last_prompt = prompt
    st.rerun()

# -- Generating logic excutes
if st.session_state.is_generating:
    current_prompt = st.session_state.last_prompt

    st.session_state.chat_history.append(
        {"role": "user", "parts": [{"text": current_prompt}]}
    )
    with st.chat_message("user"):
        st.markdown(current_prompt)

    with st.chat_message("assistant"):
        timer_placeholder = st.empty()
        start_time = time.time()
        st.caption(f"Settings: Temerature = {temp_value}")

        try:
            if use_mock:
                # Mock Mode
                full_response = st.write_stream(get_mock_response(current_prompt, mode))
            else:
                # Real API
                def stream_gen():
                    response_stream = get_gemini_response(
                        client, st.session_state.chat_history, instructions, temp_value
                    )
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text

                full_response = st.write_stream(stream_gen())

            # Save history (role="model" for Gemini)
            st.session_state.chat_history.append(
                {"role": "model", "parts": [{"text": full_response}]}
            )

        except Exception as e:
            st.error(f"Error: {e}")
            full_response = "Error occurred."

        finally:
            st.session_state.is_generating = False
            st.session_state.last_prompt = ""
            st.rerun()

        timer_placeholder.caption(f"Completed in {time.time() - start_time:.2f}s")
