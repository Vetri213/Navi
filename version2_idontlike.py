import os
import pyautogui
import google.generativeai as genai
import customtkinter as ctk
from PIL import Image
import time

# ---- Gemini Config ----
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# ---- Screenshot Function ----
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


# ---- Query Gemini ----
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
- If a step depends on clicking something, describe it by its color, text, or icon.
- End with: "Did that work?"
"""
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    with open(image_path, "rb") as f:
        response = model.generate_content([prompt, {"mime_type": "image/png", "data": f.read()}])
    return response.text.strip()


# ====================== GUI ======================
class GeminiGUI:
    def __init__(self, root):
        self.root = root
        self.expanded = False
        self.steps = []
        self.current_step = 0

        # ---- Sizes ----
        self.circle_size = 80
        self.panel_width = 500
        self.panel_height = 480

        # ---- Logo ----
        self.logo_img = ctk.CTkImage(Image.open("logo.png"), size=(self.circle_size, self.circle_size))
        self.logo_label = ctk.CTkLabel(root, image=self.logo_img, text="", bg_color="black")
        self.logo_label.bind("<Button-1>", lambda e: self.toggle_expand())

        # ---- Main Frame ----
        self.main_frame = ctk.CTkFrame(root, width=self.panel_width, height=self.panel_height, corner_radius=15)

        self.input_box = ctk.CTkEntry(self.main_frame, width=350, height=35,
                                      placeholder_text="Type your command here...")
        self.input_box.pack(pady=(15, 5))

        self.submit_button = ctk.CTkButton(self.main_frame, text="Submit 🚀", command=self.process_command)
        self.submit_button.pack(pady=(5, 10))

        self.output_area = ctk.CTkTextbox(self.main_frame, width=450, height=230, wrap="word")
        self.output_area.pack(padx=10, pady=10, fill="both", expand=True)

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        self.yes_button = ctk.CTkButton(button_frame, text="Yes ✅", fg_color="green",
                                        hover_color="#228B22", command=self.next_step,
                                        state="disabled", width=100)
        self.no_button = ctk.CTkButton(button_frame, text="No ❌", fg_color="red",
                                       hover_color="#8B0000", command=self.stop_steps,
                                       state="disabled", width=100)
        self.yes_button.pack(side="left", padx=15)
        self.no_button.pack(side="left", padx=15)

        # ---- Start Collapsed ----
        self.show_collapsed()

    # -------- Geometry Helpers --------
    def bottom_right_geometry(self, w, h, pad_x=250, pad_y=60):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x = int(sw - w - pad_x)
        y = int(sh - h - pad_y)
        return f"{w}x{h}+{x}+{y}"

    # -------- Collapse/Expand --------
    def show_collapsed(self):
        """Display circular logo (floating bubble)."""
        self.expanded = False
        self.main_frame.pack_forget()
        self.root.overrideredirect(True)
        self.root.config(bg="black")
        self.root.attributes("-transparentcolor", "black")
        self.root.geometry(self.bottom_right_geometry(self.circle_size, self.circle_size))
        self.logo_label.pack(expand=True, fill="both")

    def show_expanded(self):
        """Display assistant panel (bottom-right aligned)."""
        self.expanded = True
        self.logo_label.pack_forget()
        self.root.overrideredirect(False)
        self.root.config(bg="")
        self.root.attributes("-transparentcolor", "")
        self.root.geometry(self.bottom_right_geometry(self.panel_width, self.panel_height, pad_x=25, pad_y=60))
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.root.lift()  # bring to front

    def toggle_expand(self):
        if self.expanded:
            self.show_collapsed()
        else:
            self.show_expanded()

    # -------- Assistant Logic --------
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
- Re-explain this step in a much clearer way.
- Use extremely simple language.
- Mention exactly what to look for on the screen.
"""
            clarification = query_gemini(clarification_prompt, screenshot_path)
            self.output_area.delete("1.0", "end")
            self.output_area.insert("end", f"Clarification:\n\n{clarification}\n\nTry again — did that help?")
        else:
            self.output_area.insert("end", "\n\nNo more steps to clarify.")
        self.yes_button.configure(state="normal")
        self.no_button.configure(state="normal")


# ====================== RUN ======================
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    gui = GeminiGUI(root)
    root.mainloop()
