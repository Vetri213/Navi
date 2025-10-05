from PIL import ImageTk, Image

from core.gemini_handler import query_gemini, parse_steps
from core.voice_handler import record_audio, transcribe_audio_with_eleven, speak_with_eleven, stop_speech
from core.screenshot_handler import take_screenshot
#annotate_screenshot
from core.wake_word_handler import WakeWordDetector
import customtkinter as ctk
import os
import platform
import threading
from core.pyqt_screen_annotator import get_annotator
from core.enhanced_gemini_handler import query_gemini_with_annotations, parse_annotation_instructions




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
        
        # Initialize screen annotation system
        self.annotator = get_annotator()
        self.annotator.start()
        self.annotated_steps = []  # Store steps with annotation data

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
        self.collapsed_frame.pack(fill="both", expand=True)

        # Centered text label directly inside the frame
        text_label = ctk.CTkLabel(
            self.collapsed_frame,
            text="ASK NAVI",
            font=("Arial", 15, "bold"),
            text_color="white",
            anchor="center"
        )
        text_label.place(relx=0.5, rely=0.5, anchor="center")  # <— perfect centering

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
        for widget in (self.collapsed_frame, text_label):
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
        stop_speech()
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

        # Input box with better background color
        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="What do you need help with?",
            height=44,
            corner_radius=12,
            border_width=0,
            fg_color="#e5e7eb",
            text_color="black",  # Black text color
            placeholder_text_color="#9ca3af",  # Light grey placeholder text
            font=("Arial", 14)
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.input_entry.bind("<Return>", lambda e: self.process_command())

        # Microphone button (on right end of entry)
        # --- Fancy Mic Button ---
        mic_image = Image.open("assets/Image.png").resize((33, 33))
        mic_photo = ImageTk.PhotoImage(mic_image)

        self.mic_btn = ctk.CTkButton(
            input_frame,
            text="",
            image=mic_photo,
            width=44,
            height=44,
            corner_radius=12,
            fg_color="#10b981",
            hover_color="#059669",
            font=("Arial", 20, "bold"),
            command=self.voice_input
        )
        self.mic_btn.image = mic_photo  # prevent garbage collection
        self.mic_btn.pack(side="right")


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
            fg_color="#9ca3af",  # Grey when disabled
            hover_color="#9ca3af",  # Grey when disabled
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
            fg_color="#9ca3af",  # Grey when disabled
            hover_color="#9ca3af",  # Grey when disabled
            font=("Arial", 14, "bold"),
            command=self.handle_no,
            state="disabled"
        )
        self.no_btn.pack(side="right", fill="x", expand=True, padx=(6, 0))

    def enable_buttons(self):
        """Enable buttons with proper colors."""
        self.yes_btn.configure(
            state="normal",
            fg_color="#10b981",  # Green
            hover_color="#059669"
        )
        self.no_btn.configure(
            state="normal",
            fg_color="#ef4444",  # Red
            hover_color="#dc2626"
        )

    def disable_buttons(self):
        """Disable buttons with grey colors."""
        self.yes_btn.configure(
            state="disabled",
            fg_color="#9ca3af",  # Grey
            hover_color="#9ca3af"
        )
        self.no_btn.configure(
            state="disabled",
            fg_color="#9ca3af",  # Grey
            hover_color="#9ca3af"
        )

    def process_command(self):
        """Process user command."""
        stop_speech()
        user_text = self.input_entry.get().strip()
        if not user_text:
            self.update_output("Please enter a command or question.", "#ef4444")
            return

        self.submit_btn.configure(state="disabled", text="Processing...")
        self.disable_buttons()
        self.update_output("📸 Taking screenshot and analyzing...", "#667eea")
        self.update()

        screenshot = take_screenshot(self)
        if not screenshot:
            self.update_output("❌ Could not take screenshot", "#ef4444")
            self.submit_btn.configure(state="normal", text="Get Help")
            return

        self.last_screenshot = screenshot

        # Use enhanced Gemini handler with annotations
        try:
            response_data = query_gemini_with_annotations(user_text, screenshot)
            self.annotated_steps = parse_annotation_instructions(response_data)
            
            # Extract just the instruction text for backward compatibility
            self.steps = [step["instruction"] for step in self.annotated_steps]
            self.current_step = 0

            self.display_step_with_annotations()

        except Exception as e:
            print(f"Error with enhanced Gemini: {e}")
            # Fallback to original method
            data = query_gemini(user_text, screenshot)
            steps = data["steps"] if isinstance(data, dict) else data
            self.steps = parse_steps(steps)
            self.current_step = 0
            self.display_step()

        self.submit_btn.configure(state="normal", text="Get Help")

    def display_step_with_annotations(self):
        """Display current step with visual annotations on screen."""
        if self.current_step < len(self.annotated_steps):
            step_data = self.annotated_steps[self.current_step]
            current = step_data["instruction"]
            
            # Context-aware follow-up selection
            text_lower = current.lower()
            if any(kw in text_lower for kw in ["see", "look", "find", "locate", "visible", "icon", "button"]):
                follow_up = "Do you see it?"
            elif any(kw in text_lower for kw in ["click", "open", "press", "select", "choose"]):
                follow_up = "Did that work?"
            elif any(kw in text_lower for kw in ["type", "enter", "fill", "write"]):
                follow_up = "Did you finish typing that?"
            else:
                follow_up = "Did that work?"

            # Build display text
            step_text = f"Step {self.current_step + 1} of {len(self.annotated_steps)}\n\n"
            step_text += current
            step_text += f"\n\n{follow_up}"

            self.update_output(step_text, "#374151")

            # Show visual annotation on screen
            self.show_step_annotation(step_data)

            self.enable_buttons()
            
            # Speak asynchronously
            threading.Thread(
                target=speak_with_eleven,
                args=(current + " " + follow_up,),
                kwargs={"on_finished": self.after_speech_response},
                daemon=True
            ).start()
        else:
            self.update_output(
                "🎉 All steps completed!\n\nGreat job! You can now close this window or ask for more help.",
                "#10b981"
            )
            threading.Thread(
                target=speak_with_eleven,
                args=("All steps are completed! Great job! You can now close this window or ask for more help.",),
                kwargs={"on_finished": self.voice_input},
                daemon=True
            ).start()
            self.disable_buttons()

    def show_step_annotation(self, step_data):
        """Show visual annotation for the current step."""
        try:
            annotation = step_data.get("annotation", {})
            if not annotation:
                return
            
            annotation_type = annotation.get("type", "rectangle")
            coordinates = annotation.get("coordinates", {})
            color = annotation.get("color", "#ff0000")
            text = annotation.get("text", "")
            
            if annotation_type == "rectangle":
                x = coordinates.get("x", 0)
                y = coordinates.get("y", 0)
                width = coordinates.get("width", 100)
                height = coordinates.get("height", 100)
                self.annotator.highlight_rectangle(x, y, width, height, color, text, 5.0)
                
            elif annotation_type == "circle":
                center_x = coordinates.get("center_x", 0)
                center_y = coordinates.get("center_y", 0)
                radius = coordinates.get("radius", 50)
                self.annotator.highlight_circle(center_x, center_y, radius, color, text, 5.0)
                
            elif annotation_type == "arrow":
                from_x = coordinates.get("from_x", 0)
                from_y = coordinates.get("from_y", 0)
                to_x = coordinates.get("to_x", 100)
                to_y = coordinates.get("to_y", 100)
                self.annotator.point_arrow(from_x, from_y, to_x, to_y, color, text, 5.0)
                
        except Exception as e:
            print(f"Error showing annotation: {e}")

    def display_step(self):
        """Display current step with context-aware follow-up question."""

        if self.current_step < len(self.steps):
            current = self.steps[self.current_step]
            instruction = current["instruction"]
            area_hint = current["area_hint"]
            print(area_hint)
            # Create a global annotator instance
            self.annotator = getattr(self, "annotator", ScreenAnnotator())

            # Instead of annotate_screenshot(...)
            self.annotator.highlight_region(area_hint, duration=2.5)


            # --- Context-aware follow-up selection ---
            text_lower = instruction.lower()
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
            step_text += instruction
            step_text += f"\n\n{follow_up}"

            self.update_output(step_text, "#374151")

            self.enable_buttons()
            # Speak asynchronously (no UI delay)
            threading.Thread(
                target=speak_with_eleven,
                args=(instruction + " " + follow_up,),
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
                kwargs={"on_finished": self.voice_input},
                daemon=True
            ).start()
            self.disable_buttons()

    def handle_yes(self):
        """Handle Yes button click."""
        stop_speech()
        # Clear current annotation
        self.annotator.clear_all()
        self.current_step += 1
        
        # Use annotation display if we have annotated steps
        if hasattr(self, 'annotated_steps') and self.annotated_steps:
            self.display_step_with_annotations()
        else:
            self.display_step()

    def handle_no(self):
        """Handle No button click."""
        stop_speech()
        if self.current_step >= len(self.steps):
            return

        # Clear current annotation
        self.annotator.clear_all()
        self.disable_buttons()
        self.update_output("🔍 Let me explain that better...", "#667eea")
        self.update()

        screenshot = take_screenshot(self)
        if not screenshot:
            self.update_output("❌ Could not take screenshot", "#ef4444")
            return

        clarification_prompt = f"""You gave this step to the user:
    {self.steps[self.current_step]['instruction']}

    The user clicked "No" — they couldn't complete it or are confused.

    Task:
    - Re-explain this step much more clearly
    - Use extremely simple language
    - Mention exactly what to look for (colors, text, icons, position)
    - Break into smaller sub-steps if needed
    Return structured JSON with 'steps' and 'area_hint' for each.
    """

        data = query_gemini(clarification_prompt, screenshot)

        # Make sure Gemini returned valid structured data
        clarification_steps = data.get("steps", [])
        if not clarification_steps:
            self.update_output("❌ Gemini did not return clarification steps.", "#ef4444")
            return

        # Use the first clarification instruction (you could show multiple)
        step = clarification_steps[0]
        instruction = step.get("instruction", "")
        area_hint = step.get("area_hint", "center")

        # Annotate screenshot for visual help
        # annotated_img = annotate_screenshot(self.last_screenshot, area_hint)

        # Update UI with the clarification
        clarification_text = f"Clarification for Step {self.current_step + 1}\n\n"
        clarification_text += instruction
        clarification_text += "\n\nDid that help?"

        self.update_output(clarification_text, "#374151")

        # Display annotated screenshot below
        # from customtkinter import CTkImage
        # from PIL import Image
        # img = Image.open(annotated_img)
        # self.annotated_photo = CTkImage(img, size=(300, 170))
        # self.image_label.configure(image=self.annotated_photo)

        # Speak asynchronously
        threading.Thread(
            target=speak_with_eleven,
            args=(instruction + " Did that help?",),
            daemon=True
        ).start()

        # Reactivate buttons
        self.enable_buttons()

    def update_output(self, text, color="#374151"):
        """Thread-safe update for output text area."""

        def _update():
            if not hasattr(self, "output_text") or not self.winfo_exists():
                return  # widget destroyed or window closed
            try:
                self.output_text.configure(state="normal", text_color=color)
                self.output_text.delete("1.0", "end")
                self.output_text.insert("1.0", text.replace("**", ""))
                self.output_text.configure(state="disabled")
            except Exception as e:
                print(f"⚠️ GUI update failed: {e}")

        self.after(0, _update)

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
        if not self.winfo_exists():
            return  # Window closed before callback executed

        stop_speech()
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
    
    def cleanup(self):
        """Clean up resources when closing."""
        if hasattr(self, 'annotator'):
            self.annotator.clear_all()
    
    def destroy(self):
        """Override destroy to clean up annotations."""
        self.cleanup()
        super().destroy()
