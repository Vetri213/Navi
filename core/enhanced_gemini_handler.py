import google.generativeai as genai
import io
import os
import json
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

def configure_gemini():
    """Configure Gemini API with API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in .env")
    genai.configure(api_key=api_key)

def query_gemini_with_annotations(user_instruction: str, screenshot_image) -> Dict[str, Any]:
    """Query Gemini and get both instructions and annotation coordinates."""
    
    prompt = f"""You are Navi, a digital assistant that helps users navigate their computers with visual guidance.

User request: "{user_instruction}"

Analyze the screenshot and provide:
1. Step-by-step instructions
2. For each step, identify the approximate screen area where the user should look or click
3. Provide coordinates for screen annotation

Return your response as a JSON object with this structure:
{{
    "steps": [
        {{
            "instruction": "Step description",
            "annotation": {{
                "type": "rectangle|circle|arrow",
                "coordinates": {{
                    "x": 100,
                    "y": 50,
                    "width": 200,
                    "height": 100
                }},
                "color": "#ff0000",
                "text": "Look here"
            }}
        }}
    ]
}}

For annotation types:
- "rectangle": Use for buttons, menus, text areas (x, y, width, height)
- "circle": Use for icons, small elements (center_x, center_y, radius)
- "arrow": Use for pointing (from_x, from_y, to_x, to_y)

For coordinates, use approximate screen positions. The screenshot dimensions are {screenshot_image.size[0]}x{screenshot_image.size[1]}.

Focus on the most important UI elements the user needs to interact with."""

    # Convert screenshot to bytes
    img_bytes = io.BytesIO()
    screenshot_image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
    response = model.generate_content([
        prompt,
        {"mime_type": "image/png", "data": img_bytes}
    ])
    
    try:
        # Try to parse JSON response
        response_text = response.text.strip()
        
        # Look for JSON in the response (sometimes Gemini adds extra text)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            # Fallback: create basic structure
            return {
                "steps": [
                    {
                        "instruction": response_text,
                        "annotation": {
                            "type": "rectangle",
                            "coordinates": {
                                "x": screenshot_image.size[0] // 4,
                                "y": screenshot_image.size[1] // 4,
                                "width": screenshot_image.size[0] // 2,
                                "height": screenshot_image.size[1] // 2
                            },
                            "color": "#ff0000",
                            "text": "Look here"
                        }
                    }
                ]
            }
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing Gemini response: {e}")
        # Fallback: create basic structure
        return {
            "steps": [
                {
                    "instruction": response.text.strip(),
                    "annotation": {
                        "type": "rectangle",
                        "coordinates": {
                            "x": screenshot_image.size[0] // 4,
                            "y": screenshot_image.size[1] // 4,
                            "width": screenshot_image.size[0] // 2,
                            "height": screenshot_image.size[1] // 2
                        },
                        "color": "#ff0000",
                        "text": "Look here"
                    }
                }
            ]
        }

def parse_annotation_instructions(response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse the response data into a list of instruction dictionaries."""
    steps = []
    
    for step_data in response_data.get("steps", []):
        instruction = step_data.get("instruction", "")
        annotation = step_data.get("annotation", {})
        
        steps.append({
            "instruction": instruction,
            "annotation": annotation
        })
    
    return steps

def get_region_hint_from_instruction(instruction: str) -> str:
    """Extract a region hint from the instruction text."""
    instruction_lower = instruction.lower()
    
    # Common UI element patterns
    if any(word in instruction_lower for word in ["taskbar", "bottom", "dock"]):
        return "bottom"
    elif any(word in instruction_lower for word in ["menu", "top", "bar", "title"]):
        return "top"
    elif any(word in instruction_lower for word in ["left", "sidebar", "panel"]):
        return "left"
    elif any(word in instruction_lower for word in ["right", "panel"]):
        return "right"
    elif any(word in instruction_lower for word in ["center", "middle", "main"]):
        return "center"
    elif any(word in instruction_lower for word in ["button", "click", "icon"]):
        return "center"
    else:
        return "center"  # Default to center

# Legacy functions for backward compatibility
def query_gemini(user_instruction: str, screenshot_image):
    """Legacy function - returns just the instruction text."""
    response_data = query_gemini_with_annotations(user_instruction, screenshot_image)
    steps = [step["instruction"] for step in response_data.get("steps", [])]
    return "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))

def parse_steps(response_text: str) -> List[str]:
    """Legacy function - parses steps from text response."""
    steps = []
    for line in response_text.splitlines():
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("Step")):
            # Remove step numbers
            step = re.sub(r'^\d+\.\s*', '', line)
            step = re.sub(r'^Step\s+\d+:\s*', '', step, flags=re.IGNORECASE)
            if step:
                steps.append(step)
    return steps if steps else [response_text]
