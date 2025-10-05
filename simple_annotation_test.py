#!/usr/bin/env python3
"""
Simple test for the screen annotation system without threading issues.
"""

import sys
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer

# Import our annotation system
from core.pyqt_screen_annotator import ScreenAnnotator

class TestWindow(QMainWindow):
    """Simple test window for screen annotations."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Annotation Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create buttons for testing
        self.rect_btn = QPushButton("Test Rectangle")
        self.rect_btn.clicked.connect(self.test_rectangle)
        layout.addWidget(self.rect_btn)
        
        self.circle_btn = QPushButton("Test Circle")
        self.circle_btn.clicked.connect(self.test_circle)
        layout.addWidget(self.circle_btn)
        
        self.arrow_btn = QPushButton("Test Arrow")
        self.arrow_btn.clicked.connect(self.test_arrow)
        layout.addWidget(self.arrow_btn)
        
        self.region_btn = QPushButton("Test Region")
        self.region_btn.clicked.connect(self.test_region)
        layout.addWidget(self.region_btn)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        layout.addWidget(self.clear_btn)
        
        # Create screen annotator
        self.annotator = ScreenAnnotator()
        
    def test_rectangle(self):
        """Test rectangle annotation."""
        print("Testing rectangle...")
        self.annotator.add_rectangle_highlight(100, 100, 200, 100, "#ff0000", "Test Rectangle", 3.0)
    
    def test_circle(self):
        """Test circle annotation."""
        print("Testing circle...")
        self.annotator.add_circle_highlight(300, 200, 50, "#00ff00", "Test Circle", 3.0)
    
    def test_arrow(self):
        """Test arrow annotation."""
        print("Testing arrow...")
        self.annotator.add_arrow_pointing(50, 50, 250, 150, "#ffff00", "Look here!", 3.0)
    
    def test_region(self):
        """Test region annotation."""
        print("Testing region...")
        self.annotator.highlight_region_by_name("center", 3.0)
    
    def clear_all(self):
        """Clear all annotations."""
        print("Clearing all annotations...")
        self.annotator.clear_annotations()

def main():
    """Main function."""
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    print("Screen Annotation Test Window")
    print("Click the buttons to test different annotation types")
    print("The annotations will appear as overlays on your screen")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
