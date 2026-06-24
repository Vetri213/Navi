import google.generativeai as genai
import io, os
from dotenv import load_dotenv

load_dotenv()

def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in .env")
    genai.configure(api_key=api_key)

def query_gemini(user_instruction, screenshot_image):
    #Respond in Tamil but written with English letters. Make sure EVERYTHING IS WRITTEN IN ENGLISH LETTERS.
    prompt = f"""Respond in Tamil. You are Navi, a digital assistant that helps users navigate their computers.
User request: "{user_instruction}"
Provide short, numbered steps with clear UI descriptions. Keep each step as concise as possible."""

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

def parse_steps(response_text):
    steps = []
    for line in response_text.splitlines():
        s = line.strip()
        if s and s[0].isdigit():
            steps.append(s)
    return steps or [response_text]
