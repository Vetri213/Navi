from core.gemini_handler import query_gemini, parse_steps
from core.voice_handler import record_audio, transcribe_audio_with_eleven, speak_with_eleven, stop_speech
from core.screenshot_handler import take_screenshot
from core.wake_word_handler import WakeWordDetector
from core.embedded_animation import EmbeddedAnimationController

from PySide6.QtCore import (
    QTimer, 
    QPointF, 
    QRectF, 
    Property, 
    Signal, 
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QPoint
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QFrame,
    QGraphicsOpacityEffect
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QFont,
    QLinearGradient,
    QPainterPath,
    QRegion
)
import os
import platform
import threading


class FloatingButton(QWidget):
    """Floating purple button with hover effects."""
    
    clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 56)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Hover state
        self.is_hovering = False
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel("ASK NAVI")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            color: white;
            font-size: 15px;
            font-weight: bold;
            background: transparent;
        """)
        layout.addWidget(self.label)
        
        # Enable mouse tracking for hover
        self.setMouseTracking(True)
    
    def paintEvent(self, event):
        """Paint the rounded button with gradient."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), 32, 32)
        
        # Set gradient color
        if self.is_hovering:
            color = QColor("#8B5CF6")
        else:
            color = QColor("#7C3AED")
        
        painter.fillPath(path, color)
    
    def enterEvent(self, event):
        """Mouse entered the button."""
        self.is_hovering = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Mouse left the button."""
        self.is_hovering = False
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ExpandedPanel(QWidget):
    """Expanded panel with all controls."""
    
    collapsed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("DEBUG: ExpandedPanel __init__ called")
        self.setFixedSize(420, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.steps = []
        self.current_step = 0
        self.last_screenshot = None
        self.current_user_text = ""
        
        # Animation controller
        self.animation = None
        
        print("DEBUG: About to call init_ui")
        self.init_ui()
        print("DEBUG: init_ui completed")
    
    def init_ui(self):
        """Initialize the UI."""
        # Main container with white background
        container = QWidget(self)
        container.setGeometry(0, 0, 420, 600)
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 20px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # --- Header ---
        header = QFrame()
        header.setFixedHeight(40)
        header.setStyleSheet("""
            QFrame {
                background-color: #f3f4f6;
                border-radius: 20px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 5, 5)
        
        title = QLabel("Navi Assistant")
        title.setStyleSheet("""
            color: #374151;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e5e7eb;
                color: black;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #d1d5db;
            }
        """)
        close_btn.clicked.connect(self.collapsed.emit)
        header_layout.addWidget(close_btn)
        
        layout.addWidget(header)
        
        # --- Animation ---
        try:
            self.animation = EmbeddedAnimationController(container, width=380, height=80)
            animation_widget = self.animation.get_widget()
            layout.addWidget(animation_widget)
            self.animation.start()
            self.animation.set_idle()
            print("✨ Siri-like animation enabled")
        except Exception as e:
            print(f"⚠️ Could not create animation: {e}")
            self.animation = None
        
        # --- Input Section ---
        input_frame = QWidget()
        input_frame.setStyleSheet("background: transparent;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 0, 10, 0)
        input_layout.setSpacing(8)
        
        self.input_entry = QLineEdit()
        self.input_entry.setPlaceholderText("What do you need help with?")
        self.input_entry.setFixedHeight(44)
        self.input_entry.setStyleSheet("""
            QLineEdit {
                background-color: #1f2937;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0 15px;
                font-size: 14px;
            }
        """)
        self.input_entry.returnPressed.connect(self.process_command)
        input_layout.addWidget(self.input_entry)
        
        self.voice_btn = QPushButton("🎤")
        self.voice_btn.setFixedSize(44, 44)
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.voice_btn.clicked.connect(self.voice_input)
        input_layout.addWidget(self.voice_btn)
        
        layout.addWidget(input_frame)
        
        # --- Submit Button ---
        self.submit_btn = QPushButton("Ask Navi")
        self.submit_btn.setFixedHeight(44)
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5568d3, stop:1 #6a3f8f);
            }
        """)
        print("DEBUG: Connecting submit button to process_command")
        self.submit_btn.clicked.connect(self.process_command)
        self.submit_btn.clicked.connect(lambda: print("DEBUG: Submit button CLICKED!"))
        print("DEBUG: Submit button connected successfully")
        layout.addWidget(self.submit_btn)
        
        # --- Output Area ---
        output_container = QFrame()
        output_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
            }
        """)
        output_layout = QVBoxLayout(output_container)
        output_layout.setContentsMargins(12, 12, 12, 12)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #374151;
                border: none;
                font-size: 13px;
            }
        """)
        self.output_text.setText("Enter a question above to get started...")
        output_layout.addWidget(self.output_text)
        
        layout.addWidget(output_container)
        
        # --- Yes/No Buttons ---
        button_frame = QWidget()
        button_frame.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(10, 0, 10, 0)
        button_layout.setSpacing(12)
        
        self.yes_btn = QPushButton("Yes, Next Step")
        self.yes_btn.setFixedHeight(44)
        self.yes_btn.setEnabled(False)
        self.yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #059669;
            }
            QPushButton:disabled {
                background-color: #d1d5db;
                color: #9ca3af;
            }
        """)
        self.yes_btn.clicked.connect(self.handle_yes)
        button_layout.addWidget(self.yes_btn)
        
        self.no_btn = QPushButton("No, Clarify")
        self.no_btn.setFixedHeight(44)
        self.no_btn.setEnabled(False)
        self.no_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #dc2626;
            }
            QPushButton:disabled {
                background-color: #d1d5db;
                color: #9ca3af;
            }
        """)
        self.no_btn.clicked.connect(self.handle_no)
        button_layout.addWidget(self.no_btn)
        
        layout.addWidget(button_frame)
    
    def process_command(self):
        """Process user command."""
        print("DEBUG: process_command called")
        user_text = self.input_entry.text().strip()
        if not user_text:
            self.update_output("Please enter a command or question.", "#ef4444")
            return
        
        # Store the user text BEFORE hiding
        self.current_user_text = user_text
        print(f"DEBUG: Stored user text: {self.current_user_text}")
        
        self.submit_btn.setEnabled(False)
        self.submit_btn.setText("Processing...")
        self.yes_btn.setEnabled(False)
        self.no_btn.setEnabled(False)
        self.update_output("📸 Taking screenshot and analyzing...", "#667eea")
        
        # Set animation to listening state
        if self.animation:
            self.animation.set_listening()
        
        print("DEBUG: About to hide panel")
        # Hide the panel
        self.hide()
        
        print("DEBUG: Panel hidden, setting timer")
        # Use QTimer to delay screenshot
        QTimer.singleShot(300, self.start_processing_thread)

    def start_processing_thread(self):
        """Start the processing in a background thread."""
        print("DEBUG: start_processing_thread called")
        
        # Use the stored text (don't read from hidden widget)
        user_text = self.current_user_text
        print(f"DEBUG: Using stored text: {user_text}")
        
        def process_thread():
            print("DEBUG: Background thread started")
            try:
                # Take screenshot
                print("DEBUG: Taking screenshot...")
                screenshot = take_screenshot()
                print(f"DEBUG: Screenshot result: {screenshot is not None}")
                
                if not screenshot:
                    print("DEBUG: Screenshot failed, calling finish_processing")
                    QTimer.singleShot(0, lambda: self.finish_processing(False, "❌ Could not take screenshot"))
                    return
                
                self.last_screenshot = screenshot
                
                # Query Gemini
                print("DEBUG: Querying Gemini...")
                response = query_gemini(user_text, screenshot)
                print(f"DEBUG: Gemini response length: {len(response) if response else 0}")
                
                self.steps = parse_steps(response)
                self.current_step = 0
                print(f"DEBUG: Parsed {len(self.steps)} steps")
                
                # Call finish on main thread
                print("DEBUG: Calling finish_processing with success")
                QTimer.singleShot(0, lambda: self.finish_processing(True))
                
            except Exception as e:
                print(f"DEBUG: Exception in background thread: {e}")
                import traceback
                traceback.print_exc()
                QTimer.singleShot(0, lambda: self.finish_processing(False, f"Error: {e}"))
        
        print("DEBUG: Starting background thread")
        threading.Thread(target=process_thread, daemon=True).start()
        print("DEBUG: Background thread started successfully")

    def finish_processing(self, success, message=None):
        """Finish processing and show panel again."""
        print(f"DEBUG: finish_processing called - success={success}, message={message}")
        
        # Re-show the panel
        self.show()
        self.raise_()
        self.activateWindow()
        print("DEBUG: Panel shown")
        
        # Reset animation
        if self.animation:
            self.animation.set_idle()
        
        self.submit_btn.setEnabled(True)
        self.submit_btn.setText("Ask Navi")
        
        if success:
            print("DEBUG: Displaying step")
            self.display_step()
        else:
            print(f"DEBUG: Showing error: {message}")
            self.update_output(message, "#ef4444")
            self.yes_btn.setEnabled(False)
            self.no_btn.setEnabled(False)
    
    def display_step(self):
        """Display current step with context-aware follow-up question."""
        if self.current_step < len(self.steps):
            current = self.steps[self.current_step]
            
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
            step_text = f"Step {self.current_step + 1} of {len(self.steps)}\n\n"
            step_text += current
            step_text += f"\n\n{follow_up}"
            
            self.update_output(step_text, "#374151")
            self.yes_btn.setEnabled(True)
            self.no_btn.setEnabled(True)
            
            # Speak asynchronously
            threading.Thread(target=speak_with_eleven, args=(current+" "+follow_up,), daemon=True).start()
        else:
            self.update_output(
                "🎉 All steps completed!\n\nGreat job! You can now close this window or ask for more help.",
                "#10b981"
            )
            self.yes_btn.setEnabled(False)
            self.no_btn.setEnabled(False)
    
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
        
        self.yes_btn.setEnabled(False)
        self.no_btn.setEnabled(False)
        self.update_output("🔍 Let me explain that better...", "#667eea")
        
        # Hide panel on main thread first
        self.hide()
        QTimer.singleShot(300, self.start_clarification_thread)

    def start_clarification_thread(self):
        """Start clarification processing in background thread."""
        def clarify_thread():
            try:
                screenshot = take_screenshot()
                if not screenshot:
                    QTimer.singleShot(0, lambda: self.finish_clarification(success=False, message="❌ Could not take screenshot"))
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
                
                QTimer.singleShot(0, lambda: self.finish_clarification(success=True, clarification=clarification))
                
            except Exception as e:
                print(f"Error in clarify_thread: {e}")
                QTimer.singleShot(0, lambda: self.finish_clarification(success=False, message=f"Error: {e}"))
        
        threading.Thread(target=clarify_thread, daemon=True).start()

    def finish_clarification(self, success, message=None, clarification=None):
        """Finish clarification processing on main thread."""
        # Re-show the panel and activate it
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Reset animation to idle
        if self.animation:
            self.animation.set_idle()
        
        self.yes_btn.setEnabled(True)
        self.no_btn.setEnabled(True)
        
        if success:
            clarification_text = f"Clarification for Step {self.current_step + 1}\n\n"
            clarification_text += clarification
            clarification_text += "\n\nDid that help?"
            self.update_output(clarification_text, "#374151")
            # Speak asynchronously
            threading.Thread(target=speak_with_eleven, args=(clarification+"\nDid that help?",), daemon=True).start()
        else:
            self.update_output(message, "#ef4444")
    
    def update_output(self, text, color="#374151"):
        """Update output text area."""
        self.output_text.setText(text.replace("**", ""))
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: transparent;
                color: {color};
                border: none;
                font-size: 13px;
            }}
        """)
    
    def voice_input(self):
        """Capture voice and process as text command."""
        try:
            # Set animation to listening state
            if self.animation:
                self.animation.set_listening()
            
            self.update_output("🎙️ Listening...", "#667eea")
            
            def record_thread():
                audio_data = record_audio(duration=5)
                text = transcribe_audio_with_eleven(audio_data)
                
                # Return to idle
                if self.animation:
                    QTimer.singleShot(0, lambda: self.animation.set_idle())
                
                if text:
                    QTimer.singleShot(0, lambda: self.update_output(f"You said: \"{text}\"", "#374151"))
                    QTimer.singleShot(0, lambda: self.input_entry.setText(text))
                    QTimer.singleShot(0, self.process_command)
                else:
                    QTimer.singleShot(0, lambda: self.update_output("❌ Couldn't recognize speech.", "#ef4444"))
            
            threading.Thread(target=record_thread, daemon=True).start()
            
        except Exception as e:
            if self.animation:
                self.animation.set_idle()
            self.update_output(f"Error recording: {e}", "#ef4444")
    
    def paintEvent(self, event):
        """Paint the rounded panel."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw shadow/background
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), 20, 20)
        painter.fillPath(path, QColor("#ffffff"))


class NaviAssistant(QWidget):
    """Main Navi Assistant window with wake word detection."""
    
    def __init__(self):
        super().__init__()
        
        self.is_expanded = False
        
        # Initialize wake word detection
        self.wake_word_detector = None
        self.start_wake_word_detection()
        
        # Create collapsed button
        self.collapsed_button = FloatingButton()
        self.collapsed_button.clicked.connect(self.expand)
        self.position_collapsed()
        
        # Create expanded panel (hidden initially)
        self.expanded_panel = ExpandedPanel()
        self.expanded_panel.collapsed.connect(self.collapse)
        self.expanded_panel.hide()
        
        # Hide main window (we only show child widgets)
        self.hide()
        
        # Start checking for wake word
        self.wake_word_timer = QTimer(self)
        self.wake_word_timer.timeout.connect(self.check_wake_word_queue)
        self.wake_word_timer.start(100)  # Check every 100ms
        
        # Floating animation
        self.float_animation = None
    
    def position_collapsed(self):
        """Position collapsed button in bottom-right corner."""
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        x = screen.width() - 180 - 100
        y = screen.height() - 56 - 130
        self.collapsed_button.move(x, y)
    
    def position_expanded(self):
        """Position expanded panel in bottom-right corner."""
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        x = screen.width() - 420 - 100
        y = screen.height() - 600 - 130
        self.expanded_panel.move(x, y)
    
    def start_wake_word_detection(self):
        """Start the wake word detection in a background thread."""
        try:
            access_key = os.environ.get("PICOVOICE_ACCESS_KEY")
            if not access_key:
                print("⚠️ PICOVOICE_ACCESS_KEY not found in environment.")
                print("Wake word detection disabled. Set the key in your .env file.")
                return
            
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
                self.trigger_floating_effect()
                if self.expanded_panel.animation:
                    self.expanded_panel.animation.set_listening()
                self.expand()
                # Trigger voice input after expansion
                QTimer.singleShot(500, self.expanded_panel.voice_input)
    
    def trigger_floating_effect(self):
        """Trigger a floating/bouncing effect on the button."""
        if self.is_expanded:
            return
        
        # Create bounce animation
        self.float_animation = QPropertyAnimation(self.collapsed_button, b"pos")
        self.float_animation.setDuration(600)
        self.float_animation.setEasingCurve(QEasingCurve.OutBounce)
        
        current_pos = self.collapsed_button.pos()
        up_pos = QPoint(current_pos.x(), current_pos.y() - 30)
        
        self.float_animation.setStartValue(current_pos)
        self.float_animation.setKeyValueAt(0.5, up_pos)
        self.float_animation.setEndValue(current_pos)
        self.float_animation.start()
    
    def expand(self):
        """Expand to full panel."""
        if self.is_expanded:
            return
        
        self.is_expanded = True
        self.collapsed_button.hide()
        self.position_expanded()
        self.expanded_panel.show()
        
        # Fade-in animation
        opacity_effect = QGraphicsOpacityEffect(self.expanded_panel)
        self.expanded_panel.setGraphicsEffect(opacity_effect)
        
        fade_in = QPropertyAnimation(opacity_effect, b"opacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.start()
    
    def collapse(self):
        """Collapse to floating button."""
        if not self.is_expanded:
            return
        
        self.is_expanded = False
        self.expanded_panel.hide()
        
        # Stop animation
        if self.expanded_panel.animation:
            self.expanded_panel.animation.stop()
        
        self.position_collapsed()
        self.collapsed_button.show()
    
    def show(self):
        """Override show to show the collapsed button instead."""
        self.collapsed_button.show()
    
    def closeEvent(self, event):
        """Cleanup when closing."""
        if self.expanded_panel.animation:
            self.expanded_panel.animation.stop()
        event.accept()
