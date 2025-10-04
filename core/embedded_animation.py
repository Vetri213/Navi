"""
Embedded Tkinter-based wave animation with gradient colors.
Works natively with CustomTkinter - no multiprocessing needed!
Optimized for performance with background threading.
"""

import tkinter as tk
import math
import random
import threading
from queue import Queue


class GradientWaveAnimation(tk.Canvas):
    """
    A canvas widget that displays animated gradient waves.
    Can be embedded directly in a CustomTkinter application.
    """
    
    def __init__(self, parent, width=400, height=100, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg='#1a1a2e', highlightthickness=0, **kwargs)
        
        # Animation state
        self._animation_state = "idle"  # "idle" or "listening"
        self._is_running = False
        self._stop_thread = threading.Event()
        
        # Wave parameters
        self._phase = 0.0
        self._target_amplitude = 0.0
        self._current_amplitude = 0.0
        self._amplitude_velocity = 0.0
        
        # Idle state parameters (optimized for performance)
        self.idle_amplitude = 12.0
        self.idle_frequency = 0.6
        self.idle_speed = 0.04
        self.idle_wave_count = 3
        
        # Listening state parameters (optimized for performance)
        self.listening_amplitude = 30.0
        self.listening_frequency = 1.2
        self.listening_speed = 0.1
        self.listening_wave_count = 4  # Reduced from 5 for performance
        
        # Current parameters
        self.amplitude = self.idle_amplitude
        self.frequency = self.idle_frequency
        self.speed = self.idle_speed
        self.wave_count = self.idle_wave_count
        
        # Audio simulation (for listening state reactivity)
        self._simulated_volume = 0.5
        self._volume_target = 0.5
        
        # Gradient color scheme - beautiful blend
        self.gradient_colors = [
            "#7C3AED",  # Purple
            "#EC4899",  # Pink
            "#8B5CF6",  # Light purple
            "#F97316",  # Orange
            "#06B6D4",  # Cyan
        ]
        
        # Threading for calculations
        self.calculation_thread = None
        self.wave_data_queue = Queue(maxsize=2)  # Buffer only 2 frames
        
        # Animation timer
        self.animation_id = None
        
        # Performance optimization: reduce point count
        self.num_points = 100  # Reduced from 150 for better performance
        
        print("✨ Embedded gradient wave animation initialized (optimized)")
    
    def start_animation(self):
        """Start the wave animation with background thread for calculations."""
        if self._is_running:
            return
        
        self._is_running = True
        self._stop_thread.clear()
        
        # Start calculation thread
        self.calculation_thread = threading.Thread(
            target=self._calculation_loop,
            daemon=True
        )
        self.calculation_thread.start()
        
        # Start rendering loop on main thread
        self._render_loop()
        print("🌊 Gradient wave animation started (threaded)")
    
    def stop_animation(self):
        """Stop the wave animation and cleanup threads."""
        if not self._is_running:
            return
        
        self._is_running = False
        self._stop_thread.set()
        
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        
        # Wait for thread to finish
        if self.calculation_thread and self.calculation_thread.is_alive():
            self.calculation_thread.join(timeout=0.5)
        
        print("🛑 Gradient wave animation stopped")
    
    def set_state(self, state):
        """
        Set the animation state.
        
        Args:
            state: Either "idle" or "listening"
        """
        if state not in ["idle", "listening"]:
            return
        
        self._animation_state = state
        
        # Smoothly transition to new parameters
        if state == "idle":
            self._target_amplitude = self.idle_amplitude
            self.frequency = self.idle_frequency
            self.speed = self.idle_speed
            self.wave_count = self.idle_wave_count
        else:  # listening
            self._target_amplitude = self.listening_amplitude
            self.frequency = self.listening_frequency
            self.speed = self.listening_speed
            self.wave_count = self.listening_wave_count
    
    def set_listening_intensity(self, intensity):
        """
        Adjust the listening animation based on audio volume.
        
        Args:
            intensity: Float between 0.0 and 1.0 representing audio volume
        """
        if self._animation_state == "listening":
            self._volume_target = max(0.2, min(1.0, intensity))
    
    def _calculation_loop(self):
        """Background thread for calculating wave points (CPU-intensive)."""
        import time
        
        while not self._stop_thread.is_set() and self._is_running:
            start_time = time.time()
            
            # Update phase (moves the wave horizontally)
            self._phase += self.speed
            if self._phase > 2 * math.pi:
                self._phase -= 2 * math.pi
            
            # Smooth amplitude transition with spring-like physics
            amplitude_diff = self._target_amplitude - self._current_amplitude
            self._amplitude_velocity += amplitude_diff * 0.1
            self._amplitude_velocity *= 0.85  # Damping
            self._current_amplitude += self._amplitude_velocity
            
            # For listening state, simulate volume changes
            if self._animation_state == "listening":
                if random.random() < 0.05:
                    self._volume_target = random.uniform(0.4, 1.0)
                
                volume_diff = self._volume_target - self._simulated_volume
                self._simulated_volume += volume_diff * 0.15
                self.amplitude = self._current_amplitude * (0.5 + 0.5 * self._simulated_volume)
            else:
                self.amplitude = self._current_amplitude
            
            # Calculate wave data
            wave_data = self._calculate_wave_points()
            
            # Put in queue (non-blocking, drop old frames if queue full)
            try:
                if not self.wave_data_queue.full():
                    self.wave_data_queue.put_nowait(wave_data)
            except:
                pass
            
            # Target ~60 FPS (16ms per frame)
            elapsed = time.time() - start_time
            sleep_time = max(0, 0.016 - elapsed)
            time.sleep(sleep_time)
    
    def _render_loop(self):
        """Main thread rendering loop (just draws, no calculations)."""
        if not self._is_running:
            return
        
        # Get calculated wave data from queue
        try:
            wave_data = self.wave_data_queue.get_nowait()
            self._draw_waves_from_data(wave_data)
        except:
            pass  # No new data, skip this frame
        
        # Schedule next render (~60 FPS)
        self.animation_id = self.after(16, self._render_loop)
    
    def _calculate_wave_points(self):
        """Calculate wave points in background thread (CPU-intensive)."""
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return None
        
        center_y = height / 2
        waves = []
        
        # Calculate points for each wave layer
        for i in range(self.wave_count):
            phase_offset = (i * math.pi * 2) / self.wave_count
            amplitude_factor = 1.0 - (i * 0.12)
            color = self.gradient_colors[i % len(self.gradient_colors)]
            
            points = []
            for x_idx in range(self.num_points + 1):
                x = (x_idx / self.num_points) * width
                wave_x = (x_idx / self.num_points) * 4 * math.pi
                
                # Primary wave
                y = math.sin(wave_x * self.frequency + self._phase + phase_offset)
                # Secondary harmonic
                y += 0.3 * math.sin(wave_x * self.frequency * 2 - self._phase * 1.5 + phase_offset)
                # Tertiary harmonic
                y += 0.15 * math.sin(wave_x * self.frequency * 3 + self._phase * 2.5 + phase_offset)
                
                screen_y = center_y + (y * self.amplitude * amplitude_factor)
                points.append((x, screen_y))
            
            waves.append({'points': points, 'color': color})
        
        return waves
    
    def _draw_waves_from_data(self, wave_data):
        """Draw waves from pre-calculated data (fast, on main thread)."""
        if not wave_data:
            return
        
        # Clear canvas efficiently
        self.delete("wave")
        
        # Draw all waves
        for wave in wave_data:
            points = wave['points']
            color = wave['color']
            
            if len(points) > 1:
                # Convert to flat list
                flat_points = [coord for point in points for coord in point]
                
                # Draw with optimized settings for smoothness
                self.create_line(
                    flat_points,
                    fill=color,
                    width=4,  # Slightly thicker for smoother appearance
                    smooth=True,
                    splinesteps=20,  # More spline steps for smoother curves
                    capstyle=tk.ROUND,  # Rounded caps for smoother edges
                    joinstyle=tk.ROUND,  # Rounded joins
                    tags="wave"
                )
    
    def get_state(self):
        """Get current animation state."""
        return self._animation_state


# Convenience wrapper for easy integration
class EmbeddedAnimationController:
    """
    Controller to manage embedded animation - drop-in replacement for AnimationController.
    """
    
    def __init__(self, parent, width=400, height=100):
        """
        Initialize the embedded animation.
        
        Args:
            parent: Parent CustomTkinter widget
            width: Animation width
            height: Animation height
        """
        self.animation = GradientWaveAnimation(parent, width=width, height=height)
        self._started = False
    
    def get_widget(self):
        """Get the canvas widget to pack/grid into the UI."""
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
    import customtkinter as ctk
    
    print("\n" + "="*60)
    print("🌈 TESTING EMBEDDED GRADIENT WAVE ANIMATION")
    print("="*60 + "\n")
    
    app = ctk.CTk()
    app.title("Embedded Animation Test")
    app.geometry("600x400")
    
    # Title
    title = ctk.CTkLabel(
        app,
        text="Gradient Wave Animation Test",
        font=("Arial", 20, "bold")
    )
    title.pack(pady=20)
    
    # Create animation widget
    anim_controller = EmbeddedAnimationController(app, width=500, height=120)
    anim_widget = anim_controller.get_widget()
    anim_widget.pack(pady=20, padx=20)
    
    # Start animation
    anim_controller.start()
    anim_controller.set_idle()
    
    # Control buttons
    button_frame = ctk.CTkFrame(app)
    button_frame.pack(pady=20)
    
    def toggle_state():
        current = anim_controller.animation.get_state()
        if current == "idle":
            anim_controller.set_listening()
            toggle_btn.configure(text="Switch to Idle")
        else:
            anim_controller.set_idle()
            toggle_btn.configure(text="Switch to Listening")
    
    toggle_btn = ctk.CTkButton(
        button_frame,
        text="Switch to Listening",
        command=toggle_state,
        width=200
    )
    toggle_btn.pack(side="left", padx=10)
    
    close_btn = ctk.CTkButton(
        button_frame,
        text="Close",
        command=app.quit,
        width=100
    )
    close_btn.pack(side="left", padx=10)
    
    info = ctk.CTkLabel(
        app,
        text="🌈 Beautiful gradient colors blending together!\nClick 'Switch' to see idle vs listening states",
        font=("Arial", 12)
    )
    info.pack(pady=10)
    
    print("✅ Test window opened!")
    print("   Click 'Switch' to toggle between idle and listening states")
    print("   Watch the gradient colors blend beautifully!\n")
    
    app.mainloop()

