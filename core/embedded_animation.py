"""
PySide6-based Siri-like audio animation with gradient waves.
Beautiful animated orb that responds to voice input.
"""

from PySide6.QtCore import (
    QTimer, 
    QPointF, 
    QRectF, 
    Property, 
    Signal, 
    Qt,
    QObject,
    QPropertyAnimation,
    QEasingCurve
)
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter, 
    QColor, 
    QPen, 
    QRadialGradient,
    QPainterPath,
    QLinearGradient
)
import math
import random


class SiriLikeAnimation(QWidget):
    """
    A Siri-like animated orb that responds to voice input.
    Features smooth gradient waves that pulse and flow.
    """
    
    def __init__(self, parent=None, width=400, height=100):
        super().__init__(parent)
        self.setFixedSize(width, height)
        
        # Animation state
        self._animation_state = "idle"  # "idle" or "listening"
        self._phase = 0.0
        self._amplitude = 0.0
        self._target_amplitude = 0.0
        
        # Wave parameters
        self.idle_amplitude = 15.0
        self.listening_amplitude = 35.0
        
        # Audio reactivity simulation
        self._volume = 0.5
        self._volume_target = 0.5
        
        # Gradient colors - beautiful purple/pink theme
        self.gradient_colors = [
            QColor("#7C3AED"),  # Purple
            QColor("#EC4899"),  # Pink
            QColor("#8B5CF6"),  # Light purple
            QColor("#F97316"),  # Orange
            QColor("#06B6D4"),  # Cyan
        ]
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        
        # Orb parameters for Siri-like effect
        self.orb_radius = 25.0
        self.orb_pulse_factor = 1.0
        self.orb_target_pulse = 1.0
        
        # Wave layers
        self.wave_count = 4
        self.wave_layers = []
        
        # Background
        self.setStyleSheet("background-color: #1a1a2e;")
        
        print("✨ Siri-like animation initialized")
    
    def start_animation(self):
        """Start the animation timer."""
        if not self.timer.isActive():
            self.timer.start(16)  # ~60 FPS
            print("🌊 Siri animation started")
    
    def stop_animation(self):
        """Stop the animation timer."""
        if self.timer.isActive():
            self.timer.stop()
            print("🛑 Siri animation stopped")
    
    def set_state(self, state):
        """
        Set the animation state.
        
        Args:
            state: Either "idle" or "listening"
        """
        if state not in ["idle", "listening"]:
            return
        
        self._animation_state = state
        
        if state == "idle":
            self._target_amplitude = self.idle_amplitude
            self.orb_target_pulse = 1.0
        else:  # listening
            self._target_amplitude = self.listening_amplitude
            self.orb_target_pulse = 1.3
    
    def set_listening_intensity(self, intensity):
        """
        Adjust the listening animation based on audio volume.
        
        Args:
            intensity: Float between 0.0 and 1.0 representing audio volume
        """
        if self._animation_state == "listening":
            self._volume_target = max(0.2, min(1.0, intensity))
    
    def update_animation(self):
        """Update animation parameters and trigger repaint."""
        # Update phase (moves the wave)
        speed = 0.1 if self._animation_state == "listening" else 0.04
        self._phase += speed
        if self._phase > 2 * math.pi:
            self._phase -= 2 * math.pi
        
        # Smooth amplitude transition
        amplitude_diff = self._target_amplitude - self._amplitude
        self._amplitude += amplitude_diff * 0.1
        
        # Smooth pulse transition
        pulse_diff = self.orb_target_pulse - self.orb_pulse_factor
        self.orb_pulse_factor += pulse_diff * 0.05
        
        # Simulate volume changes for listening state
        if self._animation_state == "listening":
            if random.random() < 0.05:
                self._volume_target = random.uniform(0.5, 1.0)
            
            volume_diff = self._volume_target - self._volume
            self._volume += volume_diff * 0.15
        
        # Trigger repaint
        self.update()
    
    def paintEvent(self, event):
        """Paint the Siri-like animation."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        # Draw background
        painter.fillRect(0, 0, width, height, QColor("#1a1a2e"))
        
        if self._animation_state == "idle":
            # Draw central glowing orb for idle state
            self._draw_idle_orb(painter, center_x, center_y)
        else:
            # Draw Siri-like reactive waves for listening state
            self._draw_listening_waves(painter, center_x, center_y, width, height)
    
    def _draw_idle_orb(self, painter, cx, cy):
        """Draw a pulsing orb for idle state."""
        radius = self.orb_radius * self.orb_pulse_factor
        
        # Create radial gradient
        gradient = QRadialGradient(cx, cy, radius)
        gradient.setColorAt(0, QColor(124, 58, 237, 200))  # Purple center
        gradient.setColorAt(0.5, QColor(139, 92, 246, 150))
        gradient.setColorAt(1, QColor(124, 58, 237, 0))  # Transparent edge
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), radius, radius)
        
        # Add outer glow
        outer_radius = radius * 1.5
        outer_gradient = QRadialGradient(cx, cy, outer_radius)
        outer_gradient.setColorAt(0, QColor(124, 58, 237, 50))
        outer_gradient.setColorAt(1, QColor(124, 58, 237, 0))
        
        painter.setBrush(outer_gradient)
        painter.drawEllipse(QPointF(cx, cy), outer_radius, outer_radius)
    
    def _draw_listening_waves(self, painter, cx, cy, width, height):
        """Draw Siri-like reactive waves for listening state."""
        # Calculate current amplitude with volume
        current_amp = self._amplitude * (0.5 + 0.5 * self._volume)
        
        # Draw multiple wave layers
        for i in range(self.wave_count):
            phase_offset = (i * math.pi * 2) / self.wave_count
            amplitude_factor = 1.0 - (i * 0.15)
            color_idx = i % len(self.gradient_colors)
            color = self.gradient_colors[color_idx]
            
            # Create path for wave
            path = QPainterPath()
            points = []
            
            num_points = 80
            for x_idx in range(num_points + 1):
                x = (x_idx / num_points) * width
                wave_x = (x_idx / num_points) * 4 * math.pi
                
                # Multi-harmonic wave calculation
                y = math.sin(wave_x + self._phase + phase_offset)
                y += 0.3 * math.sin(wave_x * 2 - self._phase * 1.5 + phase_offset)
                y += 0.15 * math.sin(wave_x * 3 + self._phase * 2 + phase_offset)
                
                screen_y = cy + (y * current_amp * amplitude_factor)
                points.append(QPointF(x, screen_y))
            
            # Draw smooth wave line
            if points:
                path.moveTo(points[0])
                for point in points[1:]:
                    path.lineTo(point)
                
                # Set up pen with gradient-like appearance
                alpha = int(200 - (i * 30))
                color.setAlpha(alpha)
                pen = QPen(color)
                pen.setWidth(4)
                pen.setCapStyle(Qt.RoundCap)
                pen.setJoinStyle(Qt.RoundJoin)
                
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(path)
        
        # Draw central orb
        orb_radius = 15 * self.orb_pulse_factor * (1 + 0.3 * self._volume)
        gradient = QRadialGradient(cx, cy, orb_radius)
        gradient.setColorAt(0, QColor(236, 72, 153, 220))  # Pink center
        gradient.setColorAt(0.6, QColor(139, 92, 246, 180))
        gradient.setColorAt(1, QColor(124, 58, 237, 0))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), orb_radius, orb_radius)
    
    def get_state(self):
        """Get current animation state."""
        return self._animation_state


class EmbeddedAnimationController(QObject):
    """
    Controller to manage Siri-like animation.
    """
    
    def __init__(self, parent, width=400, height=100):
        """
        Initialize the embedded animation.
        
        Args:
            parent: Parent PySide6 widget
            width: Animation width
            height: Animation height
        """
        super().__init__(parent)
        self.animation = SiriLikeAnimation(parent, width=width, height=height)
        self._started = False
    
    def get_widget(self):
        """Get the animation widget to add to layouts."""
        return self.animation
    
    def start(self):
        """Start the animation."""
        if not self._started:
            self.animation.start_animation()
            self._started = True
            return True
        return False
    
    def stop(self):
        """Stop the animation."""
        if self._started:
            self.animation.stop_animation()
            self._started = False
    
    def set_idle(self):
        """Set animation to idle state."""
        self.animation.set_state("idle")
    
    def set_listening(self):
        """Set animation to listening state."""
        self.animation.set_state("listening")
    
    def set_intensity(self, intensity):
        """Set listening intensity."""
        self.animation.set_listening_intensity(intensity)


# Test function
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
    
    print("\n" + "="*60)
    print("🌈 TESTING SIRI-LIKE ANIMATION")
    print("="*60 + "\n")
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Siri-Like Animation Test")
    window.setGeometry(100, 100, 600, 400)
    
    central = QWidget()
    window.setCentralWidget(central)
    layout = QVBoxLayout(central)
    
    # Title
    title = QLabel("Siri-Like Animation Test")
    title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)
    
    # Animation
    anim_controller = EmbeddedAnimationController(central, width=500, height=120)
    anim_widget = anim_controller.get_widget()
    layout.addWidget(anim_widget)
    
    # Start animation
    anim_controller.start()
    anim_controller.set_idle()
    
    # Control buttons
    button_widget = QWidget()
    button_layout = QVBoxLayout(button_widget)
    
    def toggle_state():
        current = anim_controller.animation.get_state()
        if current == "idle":
            anim_controller.set_listening()
            toggle_btn.setText("Switch to Idle")
        else:
            anim_controller.set_idle()
            toggle_btn.setText("Switch to Listening")
    
    toggle_btn = QPushButton("Switch to Listening")
    toggle_btn.clicked.connect(toggle_state)
    toggle_btn.setStyleSheet("padding: 10px; font-size: 14px;")
    button_layout.addWidget(toggle_btn)
    
    close_btn = QPushButton("Close")
    close_btn.clicked.connect(app.quit)
    close_btn.setStyleSheet("padding: 10px; font-size: 14px;")
    button_layout.addWidget(close_btn)
    
    layout.addWidget(button_widget)
    
    # Info label
    info = QLabel("🌈 Beautiful Siri-like animation!\nClick 'Switch' to toggle between idle and listening states")
    info.setStyleSheet("color: white; font-size: 12px;")
    info.setAlignment(Qt.AlignCenter)
    layout.addWidget(info)
    
    # Set dark background
    central.setStyleSheet("background-color: #1a1a2e;")
    
    print("✅ Test window opened!")
    print("   Click 'Switch' to toggle between idle and listening states")
    print("   Watch the beautiful Siri-like animation!\n")
    
    window.show()
    sys.exit(app.exec())
