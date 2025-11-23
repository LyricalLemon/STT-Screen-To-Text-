import tkinter as tk
from tkinter import scrolledtext
import pytesseract
from PIL import ImageGrab
import time

# --- CONFIGURATION ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # point to your tesseract executable

def capture_screen():
    """
    Hides the window, takes a screenshot, shows the window, 
    and processes the text.
    """
    # 1. Hide the GUI window so it's not in the screenshot
    root.withdraw()
    
    # 2. Short pause to ensure window is fully gone
    time.sleep(0.5) 
    
    try:
        # 3. Capture the whole screen
        img = ImageGrab.grab()
        
        # 4. Show the GUI window again
        root.deiconify()
        
        # 5. Update status label
        status_label.config(text="Processing image...")
        root.update() # Force UI update
        
        # 6. Extract Text
        text = pytesseract.image_to_string(img)
        
        # 7. Display Text in the GUI
        # Clear previous text first
        result_text.delete(1.0, tk.END) 
        if text.strip():
            result_text.insert(tk.END, text)
            status_label.config(text="Capture Complete!")
        else:
            result_text.insert(tk.END, "No text detected.")
            status_label.config(text="Finished (No Text Found).")
            
    except Exception as e:
        root.deiconify() # Make sure window comes back even if error
        status_label.config(text="Error occurred.")
        result_text.insert(tk.END, f"Error: {e}")

# --- GUI SETUP ---

# Initialize the main window
root = tk.Tk()
root.title("Python OCR Tool")
root.geometry("500x300")

# Create a frame to hold the top controls
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

# The Capture Button
btn_capture = tk.Button(top_frame, text="Capture Whole Screen", command=capture_screen, font=("Arial", 12))
btn_capture.pack(side=tk.LEFT, padx=5)

# A Status Label to tell user what's happening
status_label = tk.Label(root, text="Ready", fg="gray")
status_label.pack()

# A Scrollable Text Area to show results
# width is in characters, height is in lines
result_text = scrolledtext.ScrolledText(root, width=50, height=10, font=("Courier New", 10))
result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Start the GUI loop
root.mainloop()