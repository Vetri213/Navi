from core.gemini_handler import query_gemini, parse_steps
from core.voice_handler import record_audio, transcribe_audio_with_eleven, speak_with_eleven, stop_speech
from core.screenshot_handler import take_screenshot
from core.wake_word_handler import WakeWordDetector
import customtkinter as ctk
import os
import platform
import threading


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
        
        # Initialize wake word detection
        self.wake_word_detector = None
        self.start_wake_word_detection()
        
        # Start checking for wake word events
        self.check_wake_word_queue()

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
    
    def start_wake_word_detection(self):
        """Start the wake word detection in a background thread."""
        try:
            # Get Picovoice access key from environment
            access_key = os.environ.get("PICOVOICE_ACCESS_KEY")
            if not access_key:
                print("⚠️ PICOVOICE_ACCESS_KEY not found in environment.")
                print("Wake word detection disabled. Set the key in your .env file.")
                return
            
            # Create and start the wake word detector
            self.wake_word_detector = WakeWordDetector(access_key)
            success = self.wake_word_detector.start()
            
            if not success:
                self.wake_word_detector = None
                
        except Exception as e:
            print(f"❌ Failed to initialize wake word detection: {e}")
            self.wake_word_detector = None
    
    def check_wake_word_queue(self):
        """Periodically check if wake word was detected and trigger expand."""
        if self.wake_word_detector is not None:
            if self.wake_word_detector.check_for_wake_word():
                print("🎯 Activating assistant from wake word...")
                self.expand()
                self.voice_input()

        
        # Check again in 100ms (10 times per second)
        self.after(100, self.check_wake_word_queue)

    def create_collapsed_ui(self):
        """Create the collapsed floating button."""
        self.collapsed_frame = ctk.CTkFrame(
            self,
            fg_color=("#667eea", "#764ba2"),  # a clean purple
            corner_radius=32,
            border_width=0
        )
        self.collapsed_frame.pack(fill="both", expand=True, padx=0, pady=0)

        button_content = ctk.CTkFrame(
            self.collapsed_frame,
            fg_color="transparent"
        )
        button_content.pack(fill="both", expand=True, padx=20, pady=10)

        text_label = ctk.CTkLabel(
            button_content,
            text="ASK NAVI",
            font=("Arial", 15, "bold"),
            text_color="white"
        )
        text_label.pack()

        # Configure appearance with cross-platform compatibility
        self.collapsed_frame.configure(fg_color="#7C3AED")
        
        # Apply platform-specific transparency
        if platform.system() == "Windows":
            # Windows supports transparentcolor
            self.attributes("-transparentcolor", self.cget("fg_color"))
            self.configure(bg="#000000")
        
        # Alpha transparency works on both macOS and Windows
        self.attributes("-alpha", 0.96)

        # Hover effect: lighten color slightly
        def on_hover(e):
            self.collapsed_frame.configure(fg_color="#8B5CF6")

        def on_leave(e):
            self.collapsed_frame.configure(fg_color="#7C3AED")

        self.collapsed_frame.bind("<Enter>", on_hover)
        self.collapsed_frame.bind("<Leave>", on_leave)

        # Make entire frame clickable
        for widget in (self.collapsed_frame, button_content, text_label):
            widget.bind("<Button-1>", lambda e: self.expand())

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

        # --- Header Bar (for collapse button) ---
        header_frame = ctk.CTkFrame(
            self.expanded_frame,
            fg_color="#f3f4f6",
            corner_radius=20,
            height=40
        )
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)

        # Small "×" close button on the right
        close_btn = ctk.CTkButton(
            header_frame,
            text="×",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="#e5e7eb",
            hover_color="#d1d5db",
            text_color="black",
            font=("Arial", 18, "bold"),
            command=self.collapse
        )
        close_btn.pack(side="right", padx=(0, 5), pady=5)

        # Optional: Title text on the left for symmetry
        title_label = ctk.CTkLabel(
            header_frame,
            text="Navi Assistant",
            font=("Arial", 14, "bold"),
            text_color="#374151"
        )
        title_label.pack(side="left", padx=10)

        # --- Main content container ---
        content = ctk.CTkFrame(
            self.expanded_frame,
            fg_color="transparent"
        )
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Input Section (entry + mic button side-by-side) ---
        input_frame = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        input_frame.pack(fill="x", pady=(0, 12))

        # Black input box
        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="What do you need help with?",
            height=44,
            corner_radius=12,
            border_width=0,
            fg_color="#1f2937",
            text_color="white",
            font=("Arial", 14)
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.input_entry.bind("<Return>", lambda e: self.process_command())

        # Microphone button (on right end of entry)
        self.voice_btn = ctk.CTkButton(
            input_frame,
            text="🎤",
            width=44,
            height=44,
            corner_radius=12,
            fg_color="#10b981",
            hover_color="#059669",
            font=("Arial", 20, "bold"),
            command=self.voice_input
        )
        self.voice_btn.pack(side="right")

        # Long purple "Type Help" button
        self.submit_btn = ctk.CTkButton(
            content,
            text="Ask Navi",
            height=44,
            corner_radius=12,
            fg_color=("#667eea", "#764ba2"),
            hover_color=("#5568d3", "#6a3f8f"),
            font=("Arial", 14, "bold"),
            command=self.process_command
        )
        self.submit_btn.pack(fill="x", pady=(0, 16))

        # --- Output Area ---
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

        # --- Yes/No Buttons ---
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x")

        self.yes_btn = ctk.CTkButton(
            button_frame,
            text="Yes, Next Step",
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
            text="No, Clarify",
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
            # Speak asynchronously (no UI delay)
            threading.Thread(
                target=speak_with_eleven,
                args=(current + " " + follow_up,),
                kwargs={"on_finished": self.after_speech_response},
                daemon=True
            ).start()
        else:
            self.update_output(
                "🎉 All steps are completed!\n\nGreat job! You can now close this window or ask for more help.",
                "#10b981"
            )
            threading.Thread(
                target=speak_with_eleven,
                args=("All steps are completed! Great job! You can now close this window or ask for more help.",),
                kwargs={"on_finished": self.after_speech_response},
                daemon=True
            ).start()
            self.yes_btn.configure(state="disabled")
            self.no_btn.configure(state="disabled")

    def handle_yes(self):
        """Handle Yes button click."""
        stop_speech()
        self.current_step += 1
        self.display_step()

    def handle_no(self):
        """Handle No button click."""
        stop_speech()
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
        clarification_text += "\n\nDid that help?"

        self.update_output(clarification_text, "#374151")
        # Speak asynchronously (no UI delay)
        threading.Thread(target=speak_with_eleven, args=(clarification+"\nDid that help?",), daemon=True).start()
        self.yes_btn.configure(state="normal")
        self.no_btn.configure(state="normal")

    def update_output(self, text, color="#374151"):
        """Update output text area."""
        self.output_text.configure(state="normal", text_color=color)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", text.replace("**",""))
        self.output_text.configure(state="disabled")

    def after_speech_response(self):
        """Called after Navi finishes speaking — listens for yes/no."""
        from core.voice_handler import listen_for_yes_no

        response = listen_for_yes_no()
        if response == "yes":
            self.handle_yes()
        elif response == "no":
            self.handle_no()
        else:
            print("🕓 No clear response — waiting for manual input.")

    def voice_input(self):
        """Capture voice and process as text command."""
        try:
            self.update_output("🎙️ Listening...", "#667eea")
            self.update()

            audio_data = record_audio(duration=5)  # adjust time if needed
            text = transcribe_audio_with_eleven(audio_data)

            if text:
                self.update_output(f"You said: “{text}”", "#374151")
                self.input_entry.delete(0, "end")
                self.input_entry.insert(0, text)
                self.process_command()
            else:
                self.update_output("❌ Couldn't recognize speech.", "#ef4444")

        except Exception as e:
            self.update_output(f"Error recording: {e}", "#ef4444")
