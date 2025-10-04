import os
import pyautogui
import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext
import time
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


# Configure Gemini
genai.configure(api_key="AIzaSyCOt6oDGt2zovnPQYl2LvHz82x-fga4uFU")


def take_screenshot(filename="screenshot.png", root=None):
    if root:
        root.withdraw()  # hide Tkinter window
        root.update()
        time.sleep(0.2)  # wait 200ms to let window fully hide
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    if root:
        root.deiconify()  # bring Tkinter back
        root.update()
    return filename


def query_gemini(user_instruction, image_path):
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
- End with: "Did that work?"
- Return steps clearly numbered (1., 2., 3., ...).
"""
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    with open(image_path, "rb") as f:
        response = model.generate_content([prompt, {"mime_type": "image/png", "data": f.read()}])

    return response.text.strip()


# ---------- GUI Part ----------


class GeminiGUI:
    def __init__(self, root):
        style = ttk.Style("cosmo")   # themes: cosmo, darkly, flatly, lumen, etc.
        self.root = root
        self.root.title("Gemini Assistant")
        self.steps = []
        self.current_step = 0

        # Input field
        self.input_label = ttk.Label(root, text="Enter your command:", font=("Segoe UI", 11))
        self.input_label.pack(pady=5)

        self.input_box = ttk.Entry(root, width=50, font=("Segoe UI", 11))
        self.input_box.pack(pady=5)

        self.submit_button = ttk.Button(root, text="Submit", bootstyle=PRIMARY, command=self.process_command)
        self.submit_button.pack(pady=5)

        # Output area
        self.output_area = ttk.ScrolledText(root, width=60, height=15, font=("Segoe UI", 11))
        self.output_area.pack(padx=10, pady=10, fill=BOTH, expand=True)

        # Yes/No buttons
        frame = ttk.Frame(root)
        frame.pack(pady=10)

        self.yes_button = ttk.Button(frame, text="Yes ✅", bootstyle=SUCCESS, command=self.next_step, state="disabled")
        self.no_button = ttk.Button(frame, text="No ❌", bootstyle=DANGER, command=self.stop_steps, state="disabled")
        self.yes_button.pack(side=LEFT, padx=10)
        self.no_button.pack(side=LEFT, padx=10)


    def process_command(self):
        user_text = self.input_box.get()
        screenshot_path = take_screenshot(root=self.root)
        self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, "Thinking...\n")
        self.root.update()

        response = query_gemini(user_text, screenshot_path)

        # Split into steps
        self.steps = [line for line in response.splitlines() if line.strip().startswith(tuple("123456789"))]
        self.current_step = 0

        if self.steps:
            self.output_area.delete(1.0, tk.END)
            self.output_area.insert(tk.END, self.steps[self.current_step] + "\n\nDid that work?")
            self.yes_button.config(state=tk.NORMAL)
            self.no_button.config(state=tk.NORMAL)
        else:
            self.output_area.insert(tk.END, response)

    def next_step(self):
        self.current_step += 1
        if self.current_step < len(self.steps):
            self.output_area.delete(1.0, tk.END)
            self.output_area.insert(tk.END, self.steps[self.current_step] + "\n\nDid that work?")
        else:
            self.output_area.delete(1.0, tk.END)
            self.output_area.insert(tk.END, "All steps completed ✅")
            self.yes_button.config(state=tk.DISABLED)
            self.no_button.config(state=tk.DISABLED)

    def stop_steps(self):
        # Take another screenshot for context
        screenshot_path = take_screenshot(root=self.root)

        # Re-ask Gemini for clarification on the current step
        if self.current_step < len(self.steps):
            step_text = self.steps[self.current_step]
            clarification_prompt = f"""
    You gave the following step to the user:
    {step_text}

    The user clicked "No", which means they could not complete it or are confused.

    Task:
    - Re-explain this step in a much clearer way, step by step if needed.
    - Use extremely simple language (like talking to a beginner).
    - Mention exactly what to look for on the screen (buttons, colors, icons, labels).
    - Avoid vague words like 'thing' or 'menu'. Be concrete.

    Screenshot of their current screen is attached for context.
    """
            clarification = query_gemini(clarification_prompt, screenshot_path)

            self.output_area.delete(1.0, tk.END)
            self.output_area.insert(tk.END, f"Clarification for step:\n\n{clarification}\n\nTry again — did that help?")
        else:
            self.output_area.insert(tk.END, "\n\nNo more steps to clarify.")

        # Keep Yes/No buttons enabled so user can retry or continue
        self.yes_button.config(state=tk.NORMAL)
        self.no_button.config(state=tk.NORMAL)

# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    gui = GeminiGUI(root)
    root.attributes("-topmost", True)  # always on top
    root.mainloop()
