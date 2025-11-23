import tkinter as tk
from tkinter import scrolledtext
import pytesseract
from PIL import Image, ImageGrab, ImageTk, ImageEnhance
import time

# --- CONFIGURATION ---
# Windows users: Uncomment and point to your tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # point to your tesseract executable

class SnippingTool:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selection_image_id = None # To track the "Bright" selection

        # 1. Hide the main window so it's not in the screenshot
        self.parent.withdraw()
        time.sleep(0.2) # Ensure it's gone

        # 2. Take the screenshot (The "Clean" Image)
        self.original_image = ImageGrab.grab()
        
        # 3. Create a "Dimmed" version of the screenshot
        enhancer = ImageEnhance.Brightness(self.original_image)
        self.dark_image = enhancer.enhance(0.7) # Reduce brightness by 50%

        # 4. Prepare images for Tkinter
        self.tk_dark_image = ImageTk.PhotoImage(self.dark_image)
        # We don't convert original_image to Tk yet; we slice it dynamically

        # 5. Create the fullscreen overlay
        self.overlay = tk.Toplevel(parent)
        self.overlay.attributes('-fullscreen', True)
        self.overlay.cursor = "cross"

        # 6. Canvas with the Dark Image as background
        self.canvas = tk.Canvas(self.overlay, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.tk_dark_image, anchor="nw")

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.overlay.bind("<Escape>", self.cancel)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
        # Initialize the rectangle (dotted line)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline='white', width=2 # White dashed line stands out on dark
        )

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)

        # 1. Update the coordinates of the dotted box
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

        # 2. CALCULATE COORDINATES (Handle negative dragging)
        x1 = min(self.start_x, cur_x)
        y1 = min(self.start_y, cur_y)
        x2 = max(self.start_x, cur_x)
        y2 = max(self.start_y, cur_y)
        
        # Ensure we have a valid size (avoid crash on 0 width)
        if x2 - x1 > 0 and y2 - y1 > 0:
            # 3. THE TRICK: Crop the "Bright" image to the selection area
            cropped_clean = self.original_image.crop((x1, y1, x2, y2))
            self.tk_clean_selection = ImageTk.PhotoImage(cropped_clean)

            # 4. Remove previous selection image if it exists
            if self.selection_image_id:
                self.canvas.delete(self.selection_image_id)

            # 5. Draw the "Bright" image snippet ON TOP of the dark background
            # We place it exactly at x1, y1
            self.selection_image_id = self.canvas.create_image(
                x1, y1, image=self.tk_clean_selection, anchor="nw"
            )
            
            # Ensure the dotted line stays on top of the image
            self.canvas.tag_raise(self.rect)

    def on_button_release(self, event):
        # Calculate final coordinates
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        self.overlay.destroy()
        
        # Send coordinates back
        self.callback(x1, y1, x2, y2)

    def cancel(self, event):
        self.overlay.destroy()
        self.parent.deiconify()


# --- MAIN LOGIC ---

def start_snipping():
    SnippingTool(root, perform_ocr)

def perform_ocr(x1, y1, x2, y2):
    try:
        if x2 - x1 < 5 or y2 - y1 < 5:
            root.deiconify()
            status_label.config(text="Selection too small!")
            return

        # Grab the area
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        
        root.deiconify()
        status_label.config(text="Processing...")
        root.update()

        text = pytesseract.image_to_string(img)

        result_text.delete(1.0, tk.END)
        if text.strip():
            result_text.insert(tk.END, text)
            status_label.config(text="Success!")
        else:
            result_text.insert(tk.END, "No text detected.")
            status_label.config(text="Finished (No Text).")

    except Exception as e:
        root.deiconify()
        result_text.insert(tk.END, f"Error: {e}")

# --- GUI SETUP ---
root = tk.Tk()
root.title("SST - Screen To Text")
root.geometry("500x300")

top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

btn_capture = tk.Button(top_frame, text="Capture", command=start_snipping, font=("Arial", 10, "bold"))
btn_capture.pack(side=tk.LEFT)

status_label = tk.Label(top_frame, text="Ready", fg="gray")
status_label.pack(side=tk.RIGHT)

result_text = scrolledtext.ScrolledText(root, width=50, height=10, font=("Courier New", 10))
result_text.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

root.mainloop()