import google.generativeai as genai
import io, os, json
from dotenv import load_dotenv

load_dotenv()

def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in .env")
    genai.configure(api_key=api_key)

def query_gemini(user_instruction, screenshot_image):
    prompt = f"""You are Navi, a digital assistant that helps users navigate their computers.
User request: "{user_instruction}"
Provide short, numbered steps with clear UI descriptions."""

    # Convert screenshot to bytes
    img_bytes = io.BytesIO()
    screenshot_image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    response = model.generate_content([
        prompt,
        {"mime_type": "image/png", "data": img_bytes}
    ])
    return response.text.strip()

def query_gemini_for_steps_with_boxes(user_instruction, screenshot_image):
    """
    Queries Gemini to get a list of steps, where each step is a JSON object
    containing the instruction text and optional bounding box coordinates.
    """
    prompt = f"""
You are Navi, an expert computer assistant for elderly users.
Your goal is to provide simple, step-by-step instructions based on the user's request and a screenshot.
User request: "{user_instruction}"

Analyze the screenshot and break down the task into numbered steps.
For each step, respond with a JSON object in a list. Each object must have:
1. A "text" key with the instruction (e.g., "First, click on the 'File' menu.").
2. A "box" key with the bounding box coordinates [x1, y1, x2, y2] for the UI element in that step.

If a step does not have a clear visual element (e.g., "Wait for the page to load"), the value for "box" should be null.

Example response for "how do I save this file":
[
    {{"text": "First, click on the 'File' menu at the top left.", "box": [10, 25, 55, 45]}},
    {{"text": "Next, in the dropdown menu, click on 'Save As...'.", "box": [12, 50, 150, 70]}},
    {{"text": "Finally, type your desired filename in the input box and press the 'Save' button.", "box": [450, 350, 520, 380]}}
]

Now, provide the JSON response for the user's request.
"""

    img_bytes = io.BytesIO()
    screenshot_image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    response = model.generate_content([
        prompt,
        {"mime_type": "image/png", "data": img_bytes}
    ])

    try:
        # Clean the response to extract only the JSON part
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        steps_data = json.loads(json_text)
        return steps_data
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"❌ Error parsing JSON from Gemini: {e}")
        # Fallback for non-JSON responses
        return [{"text": response.text.strip(), "box": None}]

def parse_steps(response_text):
    steps = []
    for line in response_text.splitlines():
        s = line.strip()
        if s and s[0].isdigit():
            steps.append(s)
    return steps or [response_text]
