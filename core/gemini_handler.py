import google.generativeai as genai
import io, os
from dotenv import load_dotenv

load_dotenv()

def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in .env")
    genai.configure(api_key=api_key)

import io
import json
import google.generativeai as genai

def query_gemini(user_instruction, screenshot_image):
    prompt = f"""
You are Navi, a desktop assistant that helps users navigate their computers step-by-step.

User request: "{user_instruction}"

Analyze the screenshot context and return your response as a JSON list of steps.
Each step must include:
1. "instruction": a short actionable description (e.g., "Click the Start menu")
2. "area_hint": one of ["top-left", "top", "top-right", "center", "bottom-left", "bottom", "bottom-right", "left", "right", "taskbar", "menu-bar"]

Example format:
{{
  "steps": [
    {{"instruction": "Click on the Start icon.", "area_hint": "bottom-left"}},
    {{"instruction": "Open Settings.", "area_hint": "center"}}
  ]
}}
"""

    # Convert screenshot to bytes
    img_bytes = io.BytesIO()
    screenshot_image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    response = model.generate_content([
        prompt,
        {"mime_type": "image/png", "data": img_bytes}
    ])

    # Try parsing structured JSON output
    try:
        text = response.text.strip()
        data = json.loads(text[text.find('{'):text.rfind('}') + 1])  # safely extract JSON block
        return data
    except Exception as e:
        print("⚠️ Could not parse JSON from Gemini response:", e)
        return {"steps": [{"instruction": response.text.strip(), "area_hint": "center"}]}


def parse_steps(steps_data):
    """Ensure steps are returned as list of dicts with instruction + area_hint."""
    parsed = []
    for step in steps_data:
        if isinstance(step, dict):
            parsed.append({
                "instruction": step.get("instruction", ""),
                "area_hint": step.get("area_hint", "center")
            })
    return parsed
