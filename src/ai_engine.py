import time
from google import genai


def get_gemini_response(client, history, instructions, temp_value):
    # Using GenAI(gemini)
    return client.models.generate_content_stream(
        model="models/gemini-flash-latest",
        contents=history,
        config={
            "system_instruction": instructions,
            "temperature": temp_value,
        },
    )


def get_mock_response(prompt, mode):
    # Dummy Answer for development（Generator)
    responses = {
        "Professional Interviewer": f"That's an insightful answer about {prompt}. How would you scale this?",
        "English Teacher": f"Interesting! You used '{prompt}'. Let's check the grammar.",
        "Code Reviewer": f"I see the logic in '{prompt}'. Any thoughts on Big O notation?",
        "Casual Assistant": f"Sure, I can help with '{prompt}'. What else?",
    }
    response_text = responses.get(mode, f"Mocking response for: {prompt}")

    for char in response_text:
        yield char
