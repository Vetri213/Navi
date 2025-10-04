import os
import base64
import pyautogui
import google.generativeai as genai

# Make sure to install dependencies:
# pip install pyautogui google-generativeai pillow

# Configure Gemini with your API key (set it in your environment first)
genai.configure(api_key="AIzaSyCOt6oDGt2zovnPQYl2LvHz82x-fga4uFU")

# for m in genai.list_models():
#     print(m.name, " — ", m.supported_generation_methods)

def take_screenshot(filename="screenshot.png"):
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return filename

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def query_gemini(user_instruction, image_path):
    # Wrap the instruction in a clean, consistent prompt
    prompt = f"""
You are an assistant that helps elderly or non-technical users navigate a computer.

Context:
- The user provides a screenshot of their screen.
- The user also provides a natural language request: "{user_instruction}"
- Use the screenshot to understand where they are.

Task:
- Break the solution down into **simple, numbered steps**.
- Keep each step short and crystal clear.
- If a step depends on clicking something, describe it by its color, text, or icon (not vague directions).

Output format:
1. Step one
2. Step two
3. Step three
...
"""

    model = genai.GenerativeModel("models/gemini-2.5-flash")

    if image_path:  # if we have a screenshot
        with open(image_path, "rb") as f:
            response = model.generate_content([
                prompt,
                {"mime_type": "image/png", "data": f.read()}
            ])
    else:  # fallback if no screenshot
        response = model.generate_content([prompt])

    return response.text


if __name__ == "__main__":
    user_text = input("Enter your instruction: ")
    screenshot_path = take_screenshot()
    print("Screenshot taken.")

    result = query_gemini(user_text, screenshot_path)
    print("\nGemini Response:\n", result)

