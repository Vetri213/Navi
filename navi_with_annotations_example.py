#!/usr/bin/env python3
"""
Example of how to integrate screen annotations with the existing Navi Assistant.
This shows how to modify the process_command method to include visual annotations.
"""

import sys
import time
import threading
from PySide6.QtWidgets import QApplication
from core.gemini_handler import configure_gemini
from core.screenshot_handler import take_screenshot
from core.navi_annotation_integration import get_navi_annotation, clear_all_annotations
from UI.navi_assistant import NaviAssistant

class AnnotatedNaviAssistant(NaviAssistant):
    """Extended Navi Assistant with screen annotation capabilities."""
    
    def __init__(self):
        super().__init__()
        self.navi_annotation = get_navi_annotation()
        self.current_steps = []
        self.current_step_index = 0
    
    def process_command_with_annotations(self, user_text: str):
        """Process user command with visual annotations."""
        print(f"Processing command with annotations: {user_text}")
        
        # Clear any existing annotations
        clear_all_annotations()
        
        # Take screenshot
        screenshot = take_screenshot(self)
        if not screenshot:
            self.update_output("❌ Could not take screenshot", "#ef4444")
            return
        
        # Process with annotation support
        try:
            self.current_steps = self.navi_annotation.process_instruction_with_annotations(
                user_text, screenshot
            )
            self.current_step_index = 0
            
            if self.current_steps:
                self.display_annotated_step()
            else:
                self.update_output("No steps generated", "#ef4444")
                
        except Exception as e:
            print(f"Error processing with annotations: {e}")
            self.update_output(f"Error: {e}", "#ef4444")
    
    def display_annotated_step(self):
        """Display current step with visual annotation."""
        if self.current_step_index >= len(self.current_steps):
            self.update_output("🎉 All steps completed!", "#10b981")
            clear_all_annotations()
            return
        
        step_data = self.current_steps[self.current_step_index]
        instruction = step_data["instruction"]
        
        # Show the instruction
        step_text = f"Step {self.current_step_index + 1} of {len(self.current_steps)}\n\n{instruction}"
        self.update_output(step_text, "#374151")
        
        # Show visual annotation
        self.navi_annotation.show_annotation_for_step(step_data, duration=5.0)
        
        # Enable buttons
        self.enable_buttons()
    
    def handle_yes_with_annotation(self):
        """Handle Yes button click with annotation support."""
        stop_speech()
        clear_all_annotations()  # Clear current annotation
        self.current_step_index += 1
        self.display_annotated_step()
    
    def handle_no_with_annotation(self):
        """Handle No button click with annotation support."""
        stop_speech()
        clear_all_annotations()  # Clear current annotation
        
        if self.current_step_index >= len(self.current_steps):
            return
        
        self.disable_buttons()
        self.update_output("🔍 Let me explain that better...", "#667eea")
        
        # Show a different annotation for clarification
        step_data = self.current_steps[self.current_step_index]
        annotation = step_data.get("annotation", {})
        
        # Modify annotation for clarification (make it more prominent)
        if annotation:
            clarification_annotation = annotation.copy()
            clarification_annotation["color"] = "#ffff00"  # Yellow for attention
            clarification_annotation["text"] = "Look carefully here"
            
            clarification_step = {
                "instruction": f"Clarification: {step_data['instruction']}",
                "annotation": clarification_annotation
            }
            
            self.navi_annotation.show_annotation_for_step(clarification_step, duration=6.0)
        
        self.enable_buttons()
    
    def show_region_hint(self, region_name: str):
        """Show a region hint as fallback."""
        self.navi_annotation.show_region_hint(region_name, duration=3.0)

def main():
    """Main function to run the annotated Navi Assistant."""
    print("Starting Navi Assistant with Screen Annotations...")
    
    # Configure Gemini
    configure_gemini()
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create the annotated assistant
    window = AnnotatedNaviAssistant()
    
    # Override the button handlers to use annotation versions
    window.handle_yes = window.handle_yes_with_annotation
    window.handle_no = window.handle_no_with_annotation
    
    # Override process_command to use annotation version
    original_process_command = window.process_command
    
    def annotated_process_command():
        user_text = window.input_entry.get().strip()
        if not user_text:
            window.update_output("Please enter a command or question.", "#ef4444")
            return
        
        window.submit_btn.configure(state="disabled", text="Processing...")
        window.disable_buttons()
        window.update_output("📸 Taking screenshot and analyzing...", "#667eea")
        window.update()
        
        # Process with annotations in background thread
        def process_thread():
            window.process_command_with_annotations(user_text)
            window.submit_btn.configure(state="normal", text="Ask Navi")
        
        threading.Thread(target=process_thread, daemon=True).start()
    
    window.process_command = annotated_process_command
    
    # Show the window
    window.show()
    
    print("Navi Assistant with annotations is running!")
    print("Try asking: 'How do I open a new file?' or 'Show me the menu bar'")
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
