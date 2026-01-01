# Gemini-based AI Chat App

This application is a high-performance chat AI built with the latest Gemini API. My goal was to ensure a robust User Experience (UX) by applying architectural principles from my Java engineering background.

## Featured Highlights

### 1. Persistence and Hydration
- State Management: Streamlit naturally resets variables on every reload. This app uses JSON-based storage to persist chat history and user settings (Mode/Temperature).
- Hydration Logic: On startup, the app automatically "hydrates" the UI with previously saved data, providing a seamless experience across sessions.

### 2. Data-Driven Design
- Separation of Concerns: AI personas (System Instructions) are decoupled from the main logic using an `instructions_map`.
- Scalability: Following Java's design patterns, the architecture makes it easy to add new AI characters without modifying the core processing logic.

### 3. Latency Transparency
- Real-time Metrics: Using `st.empty()` and the `time` module, the app calculates and displays the AI's response time.
- Developer-Friendly UI: Visualizing API latency helps monitor performance and ensures a transparent user interface.

## 🛠 Technical Stack
- Language  : Python 3.x
- Frontend  : Streamlit
- AI Engine : Google Gemini API (`google-genai`)
- Management: `python-dotenv`, `json`


## How to Set Up

1. Clone the repository
   bash
   git clone [https://github.com/kento081461australia-lang/Python_AI_Chatbot_For_Portfolio.git]
 
 2. Install requirements
    bash 
    pip install -r requirements.txt

 3. Configure Environment Variables Create a .env file in the root directory and add your API key
    plaintext
    GOOGLE_API_KEY=YOUR_API_KEY_HERE

 4. Run the App
    bash
    streamlit run app.py