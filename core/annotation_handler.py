import customtkinter as ctk
import platform

class AnnotationOverlay(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        # Make the window transparent and cover the whole screen
        self.overrideredirect(True)
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        
        # Make it a topmost window so it appears over everything
        self.attributes("-topmost", True)
        
        # Platform-specific transparency handling
        if platform.system() == "Darwin":  # macOS
            # On macOS, use -transparent attribute and set alpha low
            try:
                self.attributes("-transparent", True)
                self.attributes("-alpha", 0.3)
            except:
                # Fallback if transparent doesn't work
                self.attributes("-alpha", 0.3)
            self.config(bg='systemTransparent')
        elif platform.system() == "Windows":
            # Windows uses -transparentcolor
            self.attributes("-alpha", 0.5)
            self.config(bg='white')
            self.attributes("-transparentcolor", 'white')
        else:
            # Linux/other
            self.attributes("-alpha", 0.3)
            self.config(bg='white')

        # Create a canvas to draw the highlight on
        if platform.system() == "Darwin":
            self.canvas = ctk.CTkCanvas(self, bg='systemTransparent', highlightthickness=0)
        else:
            self.canvas = ctk.CTkCanvas(self, bg='white', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.withdraw()  # Start hidden

    def show_highlight(self, x1, y1, x2, y2):
        """Draws a highlight box and shows the window."""
        self.canvas.delete("all")  # Clear previous highlights
        
        # Draw a bright, semi-transparent rectangle with thicker line for visibility
        self.canvas.create_rectangle(
            x1, y1, x2, y2, 
            outline="#00FF00",  # Bright lime green
            width=6,  # Thicker line
            fill=""  # Make the inside of the box transparent
        )
        
        # Add a second inner rectangle for better visibility
        self.canvas.create_rectangle(
            x1+3, y1+3, x2-3, y2-3, 
            outline="#32CD32",  # Slightly darker green
            width=2, 
            fill=""
        )
        
        self.deiconify()  # Show the window

    def hide(self):
        """Hides the overlay window."""
        self.withdraw()


