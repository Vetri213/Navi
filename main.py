import os
import sys
import time
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import pyautogui
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageTk
import io

from dotenv import load_dotenv

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

load_dotenv()

def configure_gemini():
    """Configure Gemini API with error handling."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        messagebox.showerror(
            "API Key Missing",
            "GEMINI_API_KEY environment variable not set!\n\n"
            "Please set it with:\nexport GEMINI_API_KEY='your-api-key'"
        )
        sys.exit(1)
    genai.configure(api_key=api_key)


def take_screenshot(window):
    """Take a screenshot after hiding the window."""
    try:
        window.withdraw()
        time.sleep(0.3)
        screenshot = pyautogui.screenshot()
        window.deiconify()
        return screenshot
    except Exception as e:
        window.deiconify()
        print(f"Screenshot error: {e}")
        return None


def query_gemini(user_instruction, screenshot_image):
    """Query Gemini with screenshot and instruction."""
    try:
        prompt = f"""You are an assistant helping elderly or non-technical users navigate their computer.

Context:
- The user provides a screenshot of their screen
- The user's request: "{user_instruction}"

Task:
- Break the solution into simple, numbered steps (1., 2., 3., etc.)
- Keep each step short and crystal clear
- Describe clickable items by color, text, or icon
- End with: "Did that work?"
"""
        model = genai.GenerativeModel("models/gemini-2.0-flash-exp")

        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        screenshot_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        response = model.generate_content([
            prompt,
            {"mime_type": "image/png", "data": img_byte_arr}
        ])

        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def parse_steps(response_text):
    """Extract numbered steps from response."""
    steps = []
    for line in response_text.splitlines():
        stripped = line.strip()
        if stripped and len(stripped) > 2:
            # Check if line starts with a number followed by period or parenthesis
            if stripped[0].isdigit() and stripped[1] in ['.', ')', ':']:
                steps.append(stripped)

    if not steps:
        steps = [response_text]

    return steps


class NaviAssistant(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Navi Assistant")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#1a1a2e")

        self.is_expanded = False
        self.steps = []
        self.current_step = 0
        self.last_screenshot = None

        self.collapsed_size = (180, 56)
        self.expanded_size = (420, 600)
        self.position_window(self.collapsed_size)

        self.create_collapsed_ui()

        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.on_drag)

    def position_window(self, size):
        """Position window in bottom-right corner using given size tuple (w, h)."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        w, h = size

        x = screen_width - w - 100  # padding from right
        y = screen_height - h - 130  # padding from bottom
        self.geometry(f"{w}x{h}+{x}+{y}")

    def start_drag(self, event):
        """Start dragging the window."""
        self.drag_x = event.x
        self.drag_y = event.y

    def on_drag(self, event):
        """Handle window dragging."""
        x = self.winfo_x() + event.x - self.drag_x
        y = self.winfo_y() + event.y - self.drag_y
        self.geometry(f"+{x}+{y}")

    def create_collapsed_ui(self):
        """Create the collapsed floating button."""
        self.collapsed_frame = ctk.CTkFrame(
            self,
            fg_color=("#667eea", "#764ba2"),
            corner_radius=28,
            border_width=0
        )
        self.collapsed_frame.pack(fill="both", expand=True, padx=0, pady=0)

        button_content = ctk.CTkFrame(
            self.collapsed_frame,
            fg_color="transparent",
            corner_radius=0
        )
        button_content.pack(fill="both", expand=True, padx=16, pady=12)

        icon_label = ctk.CTkLabel(
            button_content,
            text="✨",
            font=("Arial", 20),
            text_color="white"
        )
        icon_label.pack(side="left", padx=(0, 8))

        text_label = ctk.CTkLabel(
            button_content,
            text="NAVIGATE",
            font=("Arial", 14, "bold"),
            text_color="white",
            justify="center"
        )
        text_label.pack(side="left")
        self.attributes("-transparentcolor", self.cget("fg_color"))

        self.collapsed_frame.bind("<Button-1>", lambda e: self.expand())
        button_content.bind("<Button-1>", lambda e: self.expand())
        icon_label.bind("<Button-1>", lambda e: self.expand())
        text_label.bind("<Button-1>", lambda e: self.expand())

    def expand(self):
        """Expand to full panel."""
        if self.is_expanded:
            return

        self.is_expanded = True

        self.collapsed_frame.destroy()

        self.position_window(self.expanded_size)

        self.create_expanded_ui()

    def collapse(self):
        """Collapse to floating button."""
        if not self.is_expanded:
            return

        self.is_expanded = False

        self.expanded_frame.destroy()

        self.position_window(self.collapsed_size)

        self.create_collapsed_ui()

    def create_expanded_ui(self):
        """Create the expanded panel UI."""
        self.expanded_frame = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=20,
            border_width=0
        )
        self.expanded_frame.pack(fill="both", expand=True)

        header = ctk.CTkFrame(
            self.expanded_frame,
            fg_color=("#667eea", "#764ba2"),
            corner_radius=0,
            height=80
        )
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=16)

        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(side="left", fill="y")

        title = ctk.CTkLabel(
            title_frame,
            text="AI Assistant",
            font=("Arial", 20, "bold"),
            text_color="white"
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Get step-by-step help",
            font=("Arial", 12),
            text_color="white"
        )
        subtitle.pack(anchor="w")

        close_btn = ctk.CTkButton(
            header_content,
            text="×",
            width=36,
            height=36,
            corner_radius=18,
            fg_color="white",
            hover_color="black",
            font=("Arial", 24),
            command=self.collapse
        )
        close_btn.pack(side="right")

        content = ctk.CTkFrame(
            self.expanded_frame,
            fg_color="transparent"
        )
        content.pack(fill="both", expand=True, padx=20, pady=20)

        self.input_entry = ctk.CTkEntry(
            content,
            placeholder_text="What do you need help with?",
            height=44,
            corner_radius=12,
            border_width=2,
            border_color="#e5e7eb",
            font=("Arial", 14)
        )
        self.input_entry.pack(fill="x", pady=(0, 12))
        self.input_entry.bind("<Return>", lambda e: self.process_command())

        self.submit_btn = ctk.CTkButton(
            content,
            text="Get Help",
            height=44,
            corner_radius=12,
            fg_color=("#667eea", "#764ba2"),
            hover_color=("#5568d3", "#6a3f8f"),
            font=("Arial", 14, "bold"),
            command=self.process_command
        )
        self.submit_btn.pack(fill="x", pady=(0, 16))

        self.output_frame = ctk.CTkFrame(
            content,
            fg_color="white",
            corner_radius=12,
            border_width=2,
            border_color="#e5e7eb"
        )
        self.output_frame.pack(fill="both", expand=True, pady=(0, 16))

        self.output_text = ctk.CTkTextbox(
            self.output_frame,
            fg_color="transparent",
            font=("Arial", 13),
            wrap="word",
            activate_scrollbars=True
        )
        self.output_text.pack(fill="both", expand=True, padx=12, pady=12)
        self.output_text.insert("1.0", "Enter a question above to get started...")
        self.output_text.configure(state="disabled")

        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x")

        self.yes_btn = ctk.CTkButton(
            button_frame,
            text="✓ Yes, Next Step",
            height=44,
            corner_radius=12,
            fg_color="#10b981",
            hover_color="#059669",
            font=("Arial", 14, "bold"),
            command=self.handle_yes,
            state="disabled"
        )
        self.yes_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.no_btn = ctk.CTkButton(
            button_frame,
            text="✗ No, Clarify",
            height=44,
            corner_radius=12,
            fg_color="#ef4444",
            hover_color="#dc2626",
            font=("Arial", 14, "bold"),
            command=self.handle_no,
            state="disabled"
        )
        self.no_btn.pack(side="right", fill="x", expand=True, padx=(6, 0))

    def process_command(self):
        """Process user command."""
        user_text = self.input_entry.get().strip()
        if not user_text:
            self.update_output("Please enter a command or question.", "#ef4444")
            return

        self.submit_btn.configure(state="disabled", text="Processing...")
        self.yes_btn.configure(state="disabled")
        self.no_btn.configure(state="disabled")
        self.update_output("📸 Taking screenshot and analyzing...", "#667eea")
        self.update()

        screenshot = take_screenshot(self)
        if not screenshot:
            self.update_output("❌ Could not take screenshot", "#ef4444")
            self.submit_btn.configure(state="normal", text="Get Help")
            return

        self.last_screenshot = screenshot

        response = query_gemini(user_text, screenshot)

        self.steps = parse_steps(response)
        self.current_step = 0

        self.display_step()

        self.submit_btn.configure(state="normal", text="Get Help")

    def display_step(self):
        """Display current step with context-aware follow-up question."""
        if self.current_step < len(self.steps):
            current = self.steps[self.current_step]

            # --- Context-aware follow-up selection ---
            text_lower = current.lower()
            if any(kw in text_lower for kw in ["see", "look", "find", "locate", "visible", "icon", "button"]):
                follow_up = "Do you see it?"
            elif any(kw in text_lower for kw in ["click", "open", "press", "select", "choose"]):
                follow_up = "Did that work?"
            elif any(kw in text_lower for kw in ["type", "enter", "fill", "write"]):
                follow_up = "Did you finish typing that?"
            else:
                follow_up = "Did that work?"

            # --- Build display text ---
            step_text = f"Step {self.current_step + 1} of {len(self.steps)}\n\n"
            step_text += current
            step_text += f"\n\n{follow_up}"

            self.update_output(step_text, "#374151")
            self.yes_btn.configure(state="normal")
            self.no_btn.configure(state="normal")
        else:
            self.update_output(
                "🎉 All steps completed!\n\nGreat job! You can now close this window or ask for more help.",
                "#10b981"
            )
            self.yes_btn.configure(state="disabled")
            self.no_btn.configure(state="disabled")

    def handle_yes(self):
        """Handle Yes button click."""
        self.current_step += 1
        self.display_step()

    def handle_no(self):
        """Handle No button click."""
        if self.current_step >= len(self.steps):
            return

        self.yes_btn.configure(state="disabled")
        self.no_btn.configure(state="disabled")
        self.update_output("🔍 Let me explain that better...", "#667eea")
        self.update()

        screenshot = take_screenshot(self)
        if not screenshot:
            self.update_output("❌ Could not take screenshot", "#ef4444")
            return

        clarification_prompt = f"""You gave this step to the user:
{self.steps[self.current_step]}

The user clicked "No" - they couldn't complete it or are confused.

Task:
- Re-explain this step much more clearly
- Use extremely simple language
- Mention exactly what to look for (colors, text, icons, position)
- Break into smaller sub-steps if needed
"""

        clarification = query_gemini(clarification_prompt, screenshot)

        clarification_text = f"Clarification for Step {self.current_step + 1}\n\n"
        clarification_text += clarification
        clarification_text += "\n\nTry again — did that help?"

        self.update_output(clarification_text, "#374151")
        self.yes_btn.configure(state="normal")
        self.no_btn.configure(state="normal")

    def update_output(self, text, color="#374151"):
        """Update output text area."""
        self.output_text.configure(state="normal", text_color=color)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text.replace("**",""))
        self.output_text.configure(state="disabled")


if __name__ == "__main__":
    configure_gemini()
    app = NaviAssistant()
    app.mainloop()
