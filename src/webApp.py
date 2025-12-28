import streamlit as st
import os
from dotenv import load_dotenv
from google import genai

# Reading .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# --1.1 Screen layout Title
st.set_page_config(page_title="My AI App Main Page", page_icon="TK")
st.title("Gemini based Chat")
st.write("Welcome to my app page")

# --1.2 Screen side bar
with st.sidebar:
    st.title("settings")
    st.write("Manage your chat session here")

    # Delete chat button
    if st.button("Clear Chat History"):
        # Clear the session
        st.session_state.chat_history = []
        st.rerun()


# --1.2.1 side bar for AI mode
with st.sidebar:
    mode = st.selectbox(
        "AI MODE",
        (
            "Casual Assistant",
            "Professional Interviewer",
            "English Teacher",
            "Code Reviewer",
        ),
    )
    if mode == "Professional Interviewer":
        instructions = "You are senior tech interviewer in Australia. Speak formally and ask challenging quesiotns"
    elif mode == "English Teacher":
        instructions = "You are a English teacher based on TESOL."
    elif mode == "Code Reviewer":
        instructions = "You are a excellent code reviewer."
    else:
        instructions = "You are a helpful assistant."

# --1.2.2 Silder bar for temperature
with st.sidebar:
    st.title("Settings")
    temp_value = st.sidebar.slider(
        label="Temperature(Creativity)",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.1,
    )


# --1. Screen sidebar bottom
with st.sidebar:
    st.divider()
    st.info("Built by TK | Hello World Support ")

# --2 Session control
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --2.1 setting for the default mode
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Casual Assistant"

# --2.2 mode change check
if mode != st.session_state.current_mode:
    st.session_state.chat_history = []
    st.session_state.current_mode = mode
    st.rerun()

# --3 showing chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0]["text"])

# --4 User input textbox
if prompt := st.chat_input("Do you have any questions?"):
    # showing User input
    st.session_state.chat_history.append({"role": "user", "parts": [{"text": prompt}]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI answer generating
    with st.chat_message("assistant"):
        try:
            # models/gemini-flash-latest  24-12-2025
            # response_stream = client.models.generate_content(
            response_stream = client.models.generate_content_stream(
                model="models/gemini-flash-latest",
                # Prompt answer
                # contents=prompt,
                # Answer based on Chat Histry
                contents=st.session_state.chat_history,
                config={"system_instruction": instructions, "temperature": temp_value},
            )

            # Streamlit write_stream
            # Paramater : generater
            # Chunk is appending to text
            def stream_generator():
                for chunk in response_stream:
                    # To SDK structure
                    if chunk.text:
                        yield chunk.text

            # Each character is showing up
            full_response = st.write_stream(stream_generator())

            # Stream response
            # st.write_stream(response)

            # Previous response -- improving 1 -- For instant answer
            # answer = response.text
            # st.markdown(answer)

            # add history
            st.session_state.chat_history.append(
                # {"role": "assistant", "content": answer} -- improving 1 --
                {"role": "assistant", "parts": [{"text": full_response}]}
            )
        except Exception as e:
            st.error(f"Error:{e}")
