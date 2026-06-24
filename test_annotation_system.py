#!/usr/bin/env python3
"""
Test script for the Navi screen annotation system.
This demonstrates how to use the annotation system with PyQt.
"""

import sys
import time
from PySide6.QtWidgets import QApplication
from core.navi_annotation_integration import get_navi_annotation, show_region_hint
from core.pyqt_screen_annotator import get_annotator

def test_basic_annotations():
    """Test basic annotation functionality."""
    print("Testing basic screen annotations...")
    
    annotator = get_annotator()
    
    # Test rectangle highlight
    print("1. Testing rectangle highlight...")
    annotator.highlight_rectangle(100, 100, 200, 100, "#ff0000", "Test Rectangle", 3.0)
    time.sleep(4)
    
    # Test circle highlight
    print("2. Testing circle highlight...")
    annotator.highlight_circle(300, 300, 50, "#00ff00", "Test Circle", 3.0)
    time.sleep(4)
    
    # Test arrow pointing
    print("3. Testing arrow pointing...")
    annotator.point_arrow(50, 50, 250, 150, "#ffff00", "Look here!", 3.0)
    time.sleep(4)
    
    # Test region highlighting
    print("4. Testing region highlighting...")
    regions = ["top", "bottom", "left", "right", "center"]
    for region in regions:
        print(f"   Highlighting {region} region...")
        annotator.highlight_region(region, 2.0)
        time.sleep(2.5)
    
    print("Basic annotation tests completed!")

def test_navi_integration():
    """Test Navi integration with annotations."""
    print("\nTesting Navi integration...")
    
    # Simulate some step data
    test_steps = [
        {
            "instruction": "Look at the top of the screen for the menu bar",
            "annotation": {
                "type": "rectangle",
                "coordinates": {"x": 0, "y": 0, "width": 800, "height": 50},
                "color": "#ff0000",
                "text": "Menu Bar"
            }
        },
        {
            "instruction": "Click on the File menu",
            "annotation": {
                "type": "circle",
                "coordinates": {"center_x": 50, "center_y": 25, "radius": 30},
                "color": "#00ff00",
                "text": "File Menu"
            }
        },
        {
            "instruction": "Look at the center of the screen",
            "annotation": {
                "type": "rectangle",
                "coordinates": {"x": 200, "y": 200, "width": 400, "height": 300},
                "color": "#0000ff",
                "text": "Main Content Area"
            }
        }
    ]
    
    navi_annotation = get_navi_annotation()
    
    print("Showing step-by-step annotations...")
    for i, step in enumerate(test_steps):
        print(f"Step {i+1}: {step['instruction']}")
        navi_annotation.show_annotation_for_step(step, 3.0)
        time.sleep(4)
    
    print("Navi integration test completed!")

def main():
    """Main test function."""
    print("Navi Screen Annotation System Test")
    print("=" * 40)
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    try:
        # Initialize the annotator
        annotator_manager = get_annotator()
        annotator_manager.start()
        
        # Test basic annotations
        test_basic_annotations()
        
        # Test Navi integration
        test_navi_integration()
        
        print("\nAll tests completed successfully!")
        print("The annotation system is working properly.")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if 'annotator_manager' in locals():
            annotator_manager.clear_all()
        app.quit()

if __name__ == "__main__":
    main()
