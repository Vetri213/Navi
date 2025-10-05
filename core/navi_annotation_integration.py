"""
Integration module that connects Navi Assistant with screen annotation capabilities.
This module handles the coordination between Navi's instructions and visual annotations.
"""

import time
import threading
from typing import List, Dict, Any, Optional
from .enhanced_gemini_handler import query_gemini_with_annotations, parse_annotation_instructions
from .pyqt_screen_annotator import get_annotator, clear_annotations

class NaviAnnotationIntegration:
    """Handles the integration between Navi instructions and screen annotations."""
    
    def __init__(self):
        self.annotator = get_annotator()
        self.current_annotations = []
        self.is_annotating = False
    
    def process_instruction_with_annotations(self, user_instruction: str, screenshot_image) -> List[Dict[str, Any]]:
        """Process user instruction and return steps with annotation data."""
        try:
            # Get response from Gemini with annotation data
            response_data = query_gemini_with_annotations(user_instruction, screenshot_image)
            
            # Parse the response into instruction steps
            steps = parse_annotation_instructions(response_data)
            
            return steps
            
        except Exception as e:
            print(f"Error processing instruction with annotations: {e}")
            # Fallback to basic instruction
            return [{
                "instruction": user_instruction,
                "annotation": {
                    "type": "rectangle",
                    "coordinates": {
                        "x": screenshot_image.size[0] // 4,
                        "y": screenshot_image.size[1] // 4,
                        "width": screenshot_image.size[0] // 2,
                        "height": screenshot_image.size[1] // 2
                    },
                    "color": "#ff0000",
                    "text": "Look here"
                }
            }]
    
    def show_annotation_for_step(self, step_data: Dict[str, Any], duration: float = 3.0):
        """Show annotation for a specific step."""
        annotation = step_data.get("annotation", {})
        if not annotation:
            return
        
        annotation_type = annotation.get("type", "rectangle")
        coordinates = annotation.get("coordinates", {})
        color = annotation.get("color", "#ff0000")
        text = annotation.get("text", "")
        
        try:
            if annotation_type == "rectangle":
                x = coordinates.get("x", 0)
                y = coordinates.get("y", 0)
                width = coordinates.get("width", 100)
                height = coordinates.get("height", 100)
                
                self.annotator.highlight_rectangle(x, y, width, height, color, text, duration)
                
            elif annotation_type == "circle":
                center_x = coordinates.get("center_x", 0)
                center_y = coordinates.get("center_y", 0)
                radius = coordinates.get("radius", 50)
                
                self.annotator.highlight_circle(center_x, center_y, radius, color, text, duration)
                
            elif annotation_type == "arrow":
                from_x = coordinates.get("from_x", 0)
                from_y = coordinates.get("from_y", 0)
                to_x = coordinates.get("to_x", 100)
                to_y = coordinates.get("to_y", 100)
                
                self.annotator.point_arrow(from_x, from_y, to_x, to_y, color, text, duration)
            
            # Store current annotation for cleanup
            self.current_annotations.append({
                "type": annotation_type,
                "coordinates": coordinates,
                "color": color,
                "text": text,
                "duration": duration,
                "start_time": time.time()
            })
            
        except Exception as e:
            print(f"Error showing annotation: {e}")
    
    def clear_current_annotations(self):
        """Clear all current annotations."""
        clear_annotations()
        self.current_annotations.clear()
    
    def show_region_hint(self, region_name: str, duration: float = 2.0):
        """Show a region hint (fallback when specific coordinates aren't available)."""
        try:
            self.annotator.highlight_region(region_name, duration)
        except Exception as e:
            print(f"Error showing region hint: {e}")
    
    def process_step_sequence(self, steps: List[Dict[str, Any]], 
                            step_delay: float = 1.0, 
                            annotation_duration: float = 3.0):
        """Process a sequence of steps with annotations."""
        def process_sequence():
            for i, step in enumerate(steps):
                print(f"Showing annotation for step {i+1}: {step['instruction']}")
                
                # Show annotation for this step
                self.show_annotation_for_step(step, annotation_duration)
                
                # Wait before showing next step
                if i < len(steps) - 1:
                    time.sleep(step_delay)
        
        # Run in background thread
        threading.Thread(target=process_sequence, daemon=True).start()
    
    def get_instruction_text(self, steps: List[Dict[str, Any]]) -> str:
        """Extract just the instruction text from steps."""
        return "\n".join(f"{i+1}. {step['instruction']}" for i, step in enumerate(steps))

# Global instance for easy access
_navi_annotation = None

def get_navi_annotation():
    """Get the global Navi annotation integration instance."""
    global _navi_annotation
    if _navi_annotation is None:
        _navi_annotation = NaviAnnotationIntegration()
    return _navi_annotation

def process_with_annotations(user_instruction: str, screenshot_image) -> List[Dict[str, Any]]:
    """Process user instruction with annotation support."""
    return get_navi_annotation().process_instruction_with_annotations(user_instruction, screenshot_image)

def show_step_annotation(step_data: Dict[str, Any], duration: float = 3.0):
    """Show annotation for a specific step."""
    get_navi_annotation().show_annotation_for_step(step_data, duration)

def clear_all_annotations():
    """Clear all annotations."""
    get_navi_annotation().clear_current_annotations()

def show_region_hint(region_name: str, duration: float = 2.0):
    """Show a region hint."""
    get_navi_annotation().show_region_hint(region_name, duration)
