import sys
import time
import threading
from typing import Optional, Tuple, List
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtCore import QTimer, QRect, QPoint, Qt, QPropertyAnimation, QEasingCurve, QThread, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QBrush, QLinearGradient
import platform


class ScreenAnnotator(QWidget):
    """Cross-platform screen annotator using PyQt that highlights areas on screen."""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool |
            Qt.WindowTransparentForInput |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        # Get screen dimensions
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # Annotation properties
        self.annotations = []  # List of (rect, color, text, duration)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update)
        
        # Hide initially
        self.hide()
    
    def add_rectangle_highlight(self, x: int, y: int, width: int, height: int, 
                              color: str = "#ff0000", text: str = "", 
                              duration: float = 3.0):
        """Add a rectangle highlight to the screen."""
        rect = QRect(x, y, width, height)
        self.annotations.append({
            'type': 'rectangle',
            'rect': rect,
            'color': QColor(color),
            'text': text,
            'duration': duration,
            'start_time': time.time()
        })
        
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Auto-hide after duration
        QTimer.singleShot(int(duration * 1000), self.clear_annotations)
    
    def add_circle_highlight(self, center_x: int, center_y: int, radius: int,
                           color: str = "#00ff00", text: str = "",
                           duration: float = 3.0):
        """Add a circular highlight to the screen."""
        self.annotations.append({
            'type': 'circle',
            'center': QPoint(center_x, center_y),
            'radius': radius,
            'color': QColor(color),
            'text': text,
            'duration': duration,
            'start_time': time.time()
        })
        
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Auto-hide after duration
        QTimer.singleShot(int(duration * 1000), self.clear_annotations)
    
    def add_arrow_pointing(self, from_x: int, from_y: int, to_x: int, to_y: int,
                          color: str = "#ffff00", text: str = "",
                          duration: float = 3.0):
        """Add an arrow pointing from one location to another."""
        self.annotations.append({
            'type': 'arrow',
            'from_point': QPoint(from_x, from_y),
            'to_point': QPoint(to_x, to_y),
            'color': QColor(color),
            'text': text,
            'duration': duration,
            'start_time': time.time()
        })
        
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Auto-hide after duration
        QTimer.singleShot(int(duration * 1000), self.clear_annotations)
    
    def highlight_region_by_name(self, region_name: str, duration: float = 3.0):
        """Highlight a named region of the screen."""
        screen = QApplication.primaryScreen().geometry()
        width = screen.width()
        height = screen.height()
        
        regions = {
            "top": (0, 0, width, int(height * 0.2)),
            "bottom": (0, int(height * 0.8), width, height),
            "left": (0, 0, int(width * 0.2), height),
            "right": (int(width * 0.8), 0, width, height),
            "center": (int(width * 0.3), int(height * 0.3),
                      int(width * 0.7), int(height * 0.7)),
            "taskbar": (0, int(height * 0.9), width, height),
            "top_left": (0, 0, int(width * 0.3), int(height * 0.3)),
            "top_right": (int(width * 0.7), 0, width, int(height * 0.3)),
            "bottom_left": (0, int(height * 0.7), int(width * 0.3), height),
            "bottom_right": (int(width * 0.7), int(height * 0.7), width, height),
        }
        
        if region_name in regions:
            x, y, w, h = regions[region_name]
            self.add_rectangle_highlight(x, y, w, h, "#ff0000", f"Look at {region_name}", duration)
        else:
            # Default to center if region not found
            self.highlight_region_by_name("center", duration)
    
    def clear_annotations(self):
        """Clear all annotations and hide the overlay."""
        self.annotations.clear()
        self.hide()
    
    def paintEvent(self, event):
        """Paint all active annotations."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        current_time = time.time()
        
        for annotation in self.annotations[:]:  # Copy to avoid modification during iteration
            # Check if annotation has expired
            if current_time - annotation['start_time'] > annotation['duration']:
                self.annotations.remove(annotation)
                continue
            
            # Calculate alpha based on remaining time (fade out effect)
            remaining_time = annotation['duration'] - (current_time - annotation['start_time'])
            alpha = min(255, int(255 * (remaining_time / annotation['duration'])))
            
            color = annotation['color']
            color.setAlpha(alpha)
            
            painter.setPen(QPen(color, 3))
            painter.setBrush(QBrush(color, Qt.NoBrush))
            
            if annotation['type'] == 'rectangle':
                rect = annotation['rect']
                painter.drawRect(rect)
                
                # Draw text if provided
                if annotation['text']:
                    painter.setPen(QPen(QColor(255, 255, 255, alpha), 2))
                    painter.setFont(QFont("Arial", 12, QFont.Bold))
                    painter.drawText(rect, Qt.AlignCenter, annotation['text'])
            
            elif annotation['type'] == 'circle':
                center = annotation['center']
                radius = annotation['radius']
                painter.drawEllipse(center, radius, radius)
                
                # Draw text if provided
                if annotation['text']:
                    painter.setPen(QPen(QColor(255, 255, 255, alpha), 2))
                    painter.setFont(QFont("Arial", 12, QFont.Bold))
                    text_rect = QRect(center.x() - radius, center.y() - radius, 
                                    radius * 2, radius * 2)
                    painter.drawText(text_rect, Qt.AlignCenter, annotation['text'])
            
            elif annotation['type'] == 'arrow':
                from_point = annotation['from_point']
                to_point = annotation['to_point']
                
                # Draw arrow line
                painter.drawLine(from_point, to_point)
                
                # Draw arrow head
                self._draw_arrow_head(painter, from_point, to_point, color)
                
                # Draw text if provided
                if annotation['text']:
                    painter.setPen(QPen(QColor(255, 255, 255, alpha), 2))
                    painter.setFont(QFont("Arial", 12, QFont.Bold))
                    mid_point = QPoint((from_point.x() + to_point.x()) // 2,
                                     (from_point.y() + to_point.y()) // 2)
                    painter.drawText(mid_point, annotation['text'])
    
    def _draw_arrow_head(self, painter: QPainter, from_point: QPoint, to_point: QPoint, color: QColor):
        """Draw an arrow head at the end of the line."""
        import math
        
        # Calculate arrow head points
        dx = to_point.x() - from_point.x()
        dy = to_point.y() - from_point.y()
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
        
        # Normalize direction vector
        dx /= length
        dy /= length
        
        # Arrow head size
        arrow_length = 20
        arrow_angle = math.pi / 6  # 30 degrees
        
        # Calculate arrow head points
        cos_angle = math.cos(arrow_angle)
        sin_angle = math.sin(arrow_angle)
        
        # Left arrow head point
        left_x = to_point.x() - arrow_length * (dx * cos_angle + dy * sin_angle)
        left_y = to_point.y() - arrow_length * (dy * cos_angle - dx * sin_angle)
        
        # Right arrow head point
        right_x = to_point.x() - arrow_length * (dx * cos_angle - dy * sin_angle)
        right_y = to_point.y() - arrow_length * (dy * cos_angle + dx * sin_angle)
        
        # Draw arrow head
        painter.drawLine(to_point, QPoint(int(left_x), int(left_y)))
        painter.drawLine(to_point, QPoint(int(right_x), int(right_y)))


class ScreenAnnotatorManager:
    """Manager class to handle screen annotations."""
    
    def __init__(self):
        self.annotator = None
        self._initialized = False
    
    def start(self):
        """Start the screen annotator (no separate thread needed)."""
        if self._initialized:
            return
        
        # Get or create QApplication
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication([])
        
        # Create annotator in main thread
        self.annotator = ScreenAnnotator()
        self._initialized = True
    
    def stop(self):
        """Stop the screen annotator."""
        if self.annotator:
            self.annotator.clear_annotations()
        self._initialized = False
    
    def highlight_region(self, region_name: str, duration: float = 3.0):
        """Highlight a region by name."""
        if self.annotator:
            self.annotator.highlight_region_by_name(region_name, duration)
    
    def highlight_rectangle(self, x: int, y: int, width: int, height: int, 
                          color: str = "#ff0000", text: str = "", duration: float = 3.0):
        """Highlight a rectangular area."""
        if self.annotator:
            self.annotator.add_rectangle_highlight(x, y, width, height, color, text, duration)
    
    def highlight_circle(self, center_x: int, center_y: int, radius: int,
                        color: str = "#00ff00", text: str = "", duration: float = 3.0):
        """Highlight a circular area."""
        if self.annotator:
            self.annotator.add_circle_highlight(center_x, center_y, radius, color, text, duration)
    
    def point_arrow(self, from_x: int, from_y: int, to_x: int, to_y: int,
                   color: str = "#ffff00", text: str = "", duration: float = 3.0):
        """Point an arrow from one location to another."""
        if self.annotator:
            self.annotator.add_arrow_pointing(from_x, from_y, to_x, to_y, color, text, duration)
    
    def clear_all(self):
        """Clear all annotations."""
        if self.annotator:
            self.annotator.clear_annotations()


# Global instance for easy access
_annotator_manager = None

def get_annotator():
    """Get the global screen annotator manager."""
    global _annotator_manager
    if _annotator_manager is None:
        _annotator_manager = ScreenAnnotatorManager()
        _annotator_manager.start()
    return _annotator_manager

def highlight_region(region_name: str, duration: float = 3.0):
    """Convenience function to highlight a region."""
    get_annotator().highlight_region(region_name, duration)

def highlight_rectangle(x: int, y: int, width: int, height: int, 
                      color: str = "#ff0000", text: str = "", duration: float = 3.0):
    """Convenience function to highlight a rectangle."""
    get_annotator().highlight_rectangle(x, y, width, height, color, text, duration)

def highlight_circle(center_x: int, center_y: int, radius: int,
                    color: str = "#00ff00", text: str = "", duration: float = 3.0):
    """Convenience function to highlight a circle."""
    get_annotator().highlight_circle(center_x, center_y, radius, color, text, duration)

def point_arrow(from_x: int, from_y: int, to_x: int, to_y: int,
               color: str = "#ffff00", text: str = "", duration: float = 3.0):
    """Convenience function to point an arrow."""
    get_annotator().point_arrow(from_x, from_y, to_x, to_y, color, text, duration)

def clear_annotations():
    """Convenience function to clear all annotations."""
    get_annotator().clear_all()
