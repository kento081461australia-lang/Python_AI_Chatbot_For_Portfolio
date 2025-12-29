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
    )
    temp_value = st.sidebar.slider("Creativity", 0.0, 2.0, 1.0, 0.1)
    use_mock = st.checkbox("Enable Mock Mode", value=False)
    if st.button("Clear History"):
        st.session_state.chat_history = []
        st.rerun()

# -- Logic for System Instructions
instructions = "You are a helpful assistant."
if mode == "Professional Interviewer":
    instructions = "You are senior tech interviewer in Australia."
elif mode == "English Teacher":
    instructions = "You are an English teacher based on TESOL."
elif mode == "Code Reviewer":
    instructions = "You are an excellent code reviewer."

# -- Session Control
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_mode" not in st.session_state:
    st.session_state.current_mode = mode

if mode != st.session_state.current_mode:
    st.session_state.chat_history = []
    st.session_state.current_mode = mode
    st.rerun()

# -- Display History
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["parts"][0]["text"])

# -- User Input & AI Response
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.chat_history.append({"role": "user", "parts": [{"text": prompt}]})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        timer_placeholder = st.empty()
        start_time = time.time()

        try:
            if use_mock:
                # Mock Mode
                full_response = st.write_stream(get_mock_response(prompt, mode))
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

        timer_placeholder.caption(f"Completed in {time.time() - start_time:.2f}s")
