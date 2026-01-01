import streamlit as st
import os
import time
import json
from dotenv import load_dotenv
from google import genai
from ai_engine import get_gemini_response, get_mock_response

# -- Load Environment Variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# -- Data Persistence Settings
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
history_file = os.path.join(DATA_DIR, "chat_history.json")


# -- Helper Function: Save all states to JSON
def save_all(history, mode, temp_value):
    #
    # Saves all settings and chat history to JSON file.
    # Make it possible to remains data after a page refleshing.
    #
    data_to_save = {
        "settings": {"mode": mode, "temp": temp_value},
        "chat_history": history,
    }
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)


# -- UI Setup
st.set_page_config(page_title="My AI App", page_icon="TK")
st.title("Gemini based Chat")

# -- Initialize Session State
# -- disabled
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
# -- chat history
if "chat_history" not in st.session_state:
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                st.session_state.chat_history = saved_data.get("chat_history", [])
                saved_settings = saved_data.get("settings", {})
                st.session_state.initial_mode = saved_settings.get(
                    "mode", "Casual Assistant"
                )
                st.session_state.initial_temp = saved_settings.get("temp", 1.0)
        except Exception as e:
            st.error(f"Failed to load history:: {e}")
            st.session_state.chat_history = []
    else:
        st.session_state.chat_history = []

# -- For refleshing -------------
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# -- Sidebar Configuration
with st.sidebar:
    st.title("Settings")

    # Option for AI Character
    options = (
        "Casual Assistant",
        "Professional Interviewer",
        "English Teacher",
        "Code Reviewer",
    )
    # Match initial index for AI mode from saved data
    try:
        default_idx = options.index(
            st.session_state.get("initial_mode", "Casual Assistant")
        )
    except:
        default_idx = 0

    # -- Sidebar functions(Mode, Temp, Mock switch)
    mode = st.selectbox(
        "AI MODE",
        options,
        index=default_idx,
        disabled=st.session_state.is_generating,
    )

    temp_value = st.sidebar.slider(
        "Creativity (Temperature)",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.get("initial_temp", 1.0),
        step=0.1,
        disabled=st.session_state.is_generating,
    )
    use_mock = st.checkbox(
        "Enable Mock Mode", value=False, disabled=st.session_state.is_generating
    )

    if st.button("Clear History", disabled=st.session_state.is_generating):
        st.session_state.chat_history = []
        save_all([], mode, temp_value)
        st.rerun()

    st.divider()
    st.subheader("Data Preview(JSON)")
    st.json(st.session_state.chat_history)


# -- System Instruction Logic
instructions_map = {
    "Professional Interviewer": "You are senior tech interviewer...",
    "English Teacher": "You are an English teacher...",
    "Code Reviewer": "You are an excellent code reviewer.",
}
# Default value
instructions = instructions_map.get(mode, "You are a helpful assistant.")

# Mode Switch Logic
if "current_mode" not in st.session_state:
    st.session_state.current_mode = mode

if mode != st.session_state.current_mode:
    st.session_state.chat_history = []
    st.session_state.current_mode = mode
    save_all([], mode, temp_value)
    st.rerun()

# -- Display Chat History
for msg in st.session_state.chat_history:
    # For display as assistant icon
    display_role = "assistant" if msg["role"] == "model" else msg["role"]
    with st.chat_message(display_role):
        st.markdown(msg["parts"][0]["text"])


# -- User Input & AI Response
if prompt := st.chat_input(
    "Ask me anything...",
    disabled=st.session_state.is_generating,
):
    st.session_state.is_generating = True
    st.session_state.last_prompt = prompt
    st.rerun()


# -- Processing Generation
if st.session_state.is_generating:
    current_prompt = st.session_state.last_prompt

    # Append User Message
    st.session_state.chat_history.append(
        {"role": "user", "parts": [{"text": current_prompt}]}
    )
    save_all(st.session_state.chat_history, mode, temp_value)

    with st.chat_message("user"):
        st.markdown(current_prompt)

    with st.chat_message("assistant"):
        timer_placeholder = st.empty()
        start_time = time.time()
        st.caption(f"Settings: Temperature = {temp_value}")

        try:
            if use_mock:
                # Mock Mode
                full_response = st.write_stream(get_mock_response(current_prompt, mode))
            else:
                # Gemeni API
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
            save_all(st.session_state.chat_history, mode, temp_value)
        except Exception as e:
            st.error(f"Error: {e}")

        finally:
            st.session_state.is_generating = False
            st.session_state.last_prompt = ""
            st.rerun()

        timer_placeholder.caption(f"Completed in {time.time() - start_time:.2f}s")
