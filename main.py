import tkinter as tk
from tkinter import scrolledtext
import pytesseract
from PIL import ImageGrab
import time

# --- CONFIGURATION ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # point to your tesseract executable

class SnippingTool:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.start_x = None
        self.start_y = None
        self.rect = None

        # Hide the main window
        self.parent.withdraw()

        # Create the overlay window (The "Dimmed" Screen)
        self.overlay = tk.Toplevel(parent)
        self.overlay.attributes('-fullscreen', True) # Full screen
        self.overlay.attributes('-alpha', 0.5)       # Transparency (0.0 to 1.0)
        self.overlay.configure(bg="grey")            # Grey background
        self.overlay.cursor = "cross"                # Crosshair cursor

        # Create a canvas for drawing the selection box
        self.canvas = tk.Canvas(self.overlay, bg="grey", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # Escape key to cancel
        self.overlay.bind("<Escape>", self.cancel)

    def on_button_press(self, event):
        # Save starting coordinates
        self.start_x = event.x
        self.start_y = event.y
        # Create the black dotted rectangle
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline='white', width=2
        )

    def on_move_press(self, event):
        # Update the rectangle as the mouse drags
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        # Calculate coordinates (handling dragging backwards/upwards)
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        # Close the overlay
        self.overlay.destroy()
        
        # Wait a tiny bit for overlay to vanish completely
        time.sleep(0.2)
        
        # Pass coordinates back to the main logic
        self.callback(x1, y1, x2, y2)

    def cancel(self, event):
        self.overlay.destroy()
        self.parent.deiconify()


# --- MAIN APPLICATION LOGIC ---

def start_snipping():
    # Initialize the snipping tool class
    SnippingTool(root, perform_ocr)

def perform_ocr(x1, y1, x2, y2):
    """
    Takes the coordinates from the Snipper, grabs that area, and runs OCR.
    """
    try:
        # Make sure we captured a valid area (width and height > 0)
        if x2 - x1 < 5 or y2 - y1 < 5:
            root.deiconify()
            status_label.config(text="Selection too small!")
            return

        # 1. Grab specific area (bbox = left, top, right, bottom)
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        
        # 2. Show Main Window
        root.deiconify()
        status_label.config(text="Processing...")
        root.update()

        # 3. Run Tesseract
        text = pytesseract.image_to_string(img)

        # 4. Display Result
        result_text.delete(1.0, tk.END)
        if text.strip():
            result_text.insert(tk.END, text)
            status_label.config(text="Success!")
        else:
            result_text.insert(tk.END, "No text detected in selection.")
            status_label.config(text="Finished (No Text).")

    except Exception as e:
        root.deiconify()
        status_label.config(text="Error")
        result_text.insert(tk.END, f"Error: {e}")

# --- GUI SETUP ---

root = tk.Tk()
root.title("SST - Screen To Text")
root.geometry("500x300")

# Top Control Frame (for layout separation)
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

# Capture Button (Left Side)
btn_capture = tk.Button(top_frame, text="Capture", command=start_snipping, font=("Arial", 10, "bold"))
btn_capture.pack(side=tk.LEFT)

# Status Label (Right Side)
status_label = tk.Label(top_frame, text="Ready", fg="gray")
status_label.pack(side=tk.RIGHT)

# Text Area
result_text = scrolledtext.ScrolledText(root, width=50, height=10, font=("Courier New", 10))
result_text.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

root.mainloop()