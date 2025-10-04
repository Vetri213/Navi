import os
import pyautogui
import google.generativeai as genai
import customtkinter as ctk
from PIL import Image
import time

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def take_screenshot(filename="screenshot.png", root=None):
    if root:
        root.withdraw()
        root.update()
        time.sleep(0.2)
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    if root:
        root.deiconify()
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


class GeminiGUI:
    def __init__(self, root):
        self.root = root
        self.steps = []
        self.current_step = 0
        self.expanded = False  # collapsed by default

        # Root config
        self.root.title("✨ Gemini Assistant")
        self.set_collapsed_geometry()

        # Load logo image
        self.logo_img = ctk.CTkImage(Image.open("logo.png"), size=(40, 40))  # add your logo.png here

        # Floating button (always visible)
        self.fab_button = ctk.CTkButton(root, image=self.logo_img, text="", width=60, height=60,
                                        corner_radius=30, fg_color="royalblue",
                                        hover_color="navy", command=self.toggle_expand)
        self.fab_button.pack(padx=10, pady=10, anchor="se")  # bottom-right corner

        # Expanded frame (hidden at first)
        self.main_frame = ctk.CTkFrame(root, width=600, height=500)
        # Add widgets inside this frame
        self.input_box = ctk.CTkEntry(self.main_frame, width=400, height=35,
                                      placeholder_text="Type your command here...")
        self.input_box.pack(pady=5)

        self.submit_button = ctk.CTkButton(self.main_frame, text="Submit 🚀", command=self.process_command)
        self.submit_button.pack(pady=5)

        self.output_area = ctk.CTkTextbox(self.main_frame, width=550, height=250, wrap="word")
        self.output_area.pack(padx=10, pady=10, fill="both", expand=True)

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=5)
        self.yes_button = ctk.CTkButton(button_frame, text="Yes ✅", fg_color="green",
                                        hover_color="#228B22", command=self.next_step, state="disabled", width=100)
        self.no_button = ctk.CTkButton(button_frame, text="No ❌", fg_color="red",
                                       hover_color="#8B0000", command=self.stop_steps, state="disabled", width=100)
        self.yes_button.pack(side="left", padx=15)
        self.no_button.pack(side="left", padx=15)

    def set_collapsed_geometry(self):
        # Small floating bubble in bottom right
        self.root.geometry("80x80+{}+{}".format(
            self.root.winfo_screenwidth() - 100,
            self.root.winfo_screenheight() - 120
        ))

    def set_expanded_geometry(self):
        # Expand into main window
        self.root.geometry("650x550+{}+{}".format(
            self.root.winfo_screenwidth() - 700,
            self.root.winfo_screenheight() - 600
        ))

    def toggle_expand(self):
        if self.expanded:
            # Collapse
            self.main_frame.pack_forget()
            self.set_collapsed_geometry()
            self.expanded = False
        else:
            # Expand
            self.set_expanded_geometry()
            self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
            self.expanded = True

    def process_command(self):
        user_text = self.input_box.get()
        screenshot_path = take_screenshot(root=self.root)
        self.output_area.delete("1.0", "end")
        self.output_area.insert("end", "Thinking...\n")
        self.root.update()

        response = query_gemini(user_text, screenshot_path)
        self.steps = [line for line in response.splitlines() if line.strip().startswith(tuple("123456789"))]
        self.current_step = 0

        if self.steps:
            self.output_area.delete("1.0", "end")
            self.output_area.insert("end", self.steps[self.current_step] + "\n\nDid that work?")
            self.yes_button.configure(state="normal")
            self.no_button.configure(state="normal")
        else:
            self.output_area.insert("end", response)

    def next_step(self):
        self.current_step += 1
        if self.current_step < len(self.steps):
            self.output_area.delete("1.0", "end")
            self.output_area.insert("end", self.steps[self.current_step] + "\n\nDid that work?")
        else:
            self.output_area.delete("1.0", "end")
            self.output_area.insert("end", "All steps completed ✅")
            self.yes_button.configure(state="disabled")
            self.no_button.configure(state="disabled")

    def stop_steps(self):
        screenshot_path = take_screenshot(root=self.root)
        if self.current_step < len(self.steps):
            step_text = self.steps[self.current_step]
            clarification_prompt = f"""
You gave the following step to the user:
{step_text}

The user clicked "No", which means they could not complete it or are confused.

Task:
- Re-explain this step in a much clearer way, step by step if needed.
- Use extremely simple language.
- Mention exactly what to look for on the screen.
- Avoid vague words like 'thing' or 'menu'.

Screenshot of their current screen is attached for context.
"""
            clarification = query_gemini(clarification_prompt, screenshot_path)
            self.output_area.delete("1.0", "end")
            self.output_area.insert("end", f"Clarification for step:\n\n{clarification}\n\nTry again — did that help?")
        else:
            self.output_area.insert("end", "\n\nNo more steps to clarify.")
        self.yes_button.configure(state="normal")
        self.no_button.configure(state="normal")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    gui = GeminiGUI(root)
    root.attributes("-topmost", True)
    root.mainloop()
