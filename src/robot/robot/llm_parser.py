import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = """
You are a robot mission planner.

Convert the user's instruction into JSON.

Return ONLY JSON.

Schema:

{
    "mission":"patrol",
    "loops":1,
    "distance":5,
    "speed":0.2,
    "return_home":false
}

Rules:
- mission must be patrol
- loops must be integer
- distance is meters
- speed is m/s
- return_home true or false

Do not explain.
Do not write markdown.
Return only JSON.
"""


def parse_prompt(prompt):

    response = model.generate_content(
        SYSTEM_PROMPT + "\n\nUser: " + prompt
    )

    text = response.text.strip()

    # Remove markdown if Gemini adds it
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    print("\nGemini Output:")
    print(text)

    return json.loads(text)
