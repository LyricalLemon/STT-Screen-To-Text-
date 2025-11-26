import tkinter as tk
from tkinter import scrolledtext
import pytesseract
from PIL import Image, ImageGrab, ImageTk, ImageEnhance
import time

# --- CONFIGURATION ---
# Windows users: Uncomment and point to your tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Noah.Dias\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

class SnippingTool:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selection_image_id = None 

        # Hide main window
        self.parent.withdraw()
        time.sleep(0.2) 

        # Take screenshot and prepare "Dark" and "Bright" versions
        self.original_image = ImageGrab.grab()
        enhancer = ImageEnhance.Brightness(self.original_image)
        self.dark_image = enhancer.enhance(0.4) 
        self.tk_dark_image = ImageTk.PhotoImage(self.dark_image)

        # Overlay Window
        self.overlay = tk.Toplevel(parent)
        self.overlay.attributes('-fullscreen', True)
        self.overlay.cursor = "cross"

        self.canvas = tk.Canvas(self.overlay, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.tk_dark_image, anchor="nw")

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.overlay.bind("<Escape>", self.cancel)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline='white', width=2
        )

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

        x1 = min(self.start_x, cur_x)
        y1 = min(self.start_y, cur_y)
        x2 = max(self.start_x, cur_x)
        y2 = max(self.start_y, cur_y)
        
        if x2 - x1 > 0 and y2 - y1 > 0:
            cropped_clean = self.original_image.crop((x1, y1, x2, y2))
            self.tk_clean_selection = ImageTk.PhotoImage(cropped_clean)

            if self.selection_image_id:
                self.canvas.delete(self.selection_image_id)

            self.selection_image_id = self.canvas.create_image(
                x1, y1, image=self.tk_clean_selection, anchor="nw"
            )
            self.canvas.tag_raise(self.rect)

    def on_button_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        self.overlay.destroy()
        self.callback(x1, y1, x2, y2)

    def cancel(self, event):
        self.overlay.destroy()
        self.parent.deiconify()

# --- HELPER FUNCTIONS ---

def show_fading_popup(message):
    """Creates a small borderless window centered inside the Main GUI."""
    popup = tk.Toplevel(root)
    popup.overrideredirect(True) # Remove borders
    
    # 1. Define Popup Size
    popup_w = 200
    popup_h = 50
    
    # 2. Get Main Window (Root) Position & Size
    # We use winfo_x/y/width/height to get the dynamic current state
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    
    # 3. Calculate Center Position relative to the Main Window
    x = root_x + (root_w // 2) - (popup_w // 2)
    y = root_y + (root_h // 2) - (popup_h // 2)
    
    popup.geometry(f"{popup_w}x{popup_h}+{x}+{y}")
    popup.configure(bg="#333333")
    
    lbl = tk.Label(popup, text=message, fg="white", bg="#333333", font=("Aptos", 12, "bold"))
    lbl.pack(expand=True)
    
    # Schedule destruction after 1.5 seconds
    popup.after(2200, popup.destroy)

def delete_prev_word(event):
    text_widget = event.widget
    # Current cursor position
    cursor_pos = text_widget.index("insert")

    # Find the start of the previous word
    # "insert wordstart" jumps to the beginning of the word you're currently in.
    # "insert -1c wordstart" jumps to the start of the previous word.
    prev_word_start = text_widget.index("insert -1c wordstart")

    # Delete from previous word start to current cursor
    text_widget.delete(prev_word_start, cursor_pos)

    # Prevent the default behavior
    return "break"

# --- MAIN LOGIC ---

def start_snipping():
    SnippingTool(root, perform_ocr)

def perform_ocr(x1, y1, x2, y2):
    try:
        if x2 - x1 < 5 or y2 - y1 < 5:
            root.deiconify()
            status_label.config(text="STATUS: Selection too small!")
            return

        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        
        root.deiconify()
        status_label.config(text="STATUS: Processing...", fg="orange")
        root.update()

        # --- SAFELY OPTIMIZED PROCESSING ---
        img = img.convert('L')
        width, height = img.size
        img = img.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
        # --- END OPTIMIZATIONS ---

        custom_config = r'--psm 6'
        text = pytesseract.image_to_string(img, config=custom_config)

        # String Repairs
        text = text.replace('|', 'I') 
        text = text.replace(' 1 ', ' I ') 
        text = text.replace(' l ', ' I ')

        result_text.delete(1.0, tk.END)
        if text.strip():
            result_text.insert(tk.END, text)
            status_label.config(text="STATUS: Finished (Text Detected)", fg="green")
            
            # --- CLIPBOARD & POPUP ---
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update() # Required to finalize clipboard update
            show_fading_popup("Copied to Clipboard")
            
        else:
            result_text.insert(tk.END, "No text detected.")
            status_label.config(text="STATUS: Finished (No Text Detected)", fg="red")

    except Exception as e:
        root.deiconify()
        result_text.insert(tk.END, f"Error: {e}")


# --- GUI SETUP ---

root = tk.Tk()
root.title("SST - Screen To Text")
root.geometry("1000x500")

# 1. Top Control Frame
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

btn_capture = tk.Button(top_frame, text="Capture", command=start_snipping, font=("Arial", 12, "bold"))
btn_capture.pack(side=tk.LEFT)

status_label = tk.Label(top_frame, text="STATUS: Ready...", fg="black", font=("Arial", 12, "bold"))
status_label.pack(side=tk.RIGHT)

# 2. Text Area Frame
text_frame = tk.Frame(root)
text_frame.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

# 3. Scrollbars
v_scroll = tk.Scrollbar(text_frame, orient=tk.VERTICAL)
h_scroll = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL)

# 4. Text Widget
result_text = tk.Text(text_frame, font=("Arial", 12), wrap="none",
                      undo=True, autoseparators=True, maxundo=-1,
                      yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

result_text.bind("<Control-BackSpace>", delete_prev_word) # Custom Ctrl+Backspace
result_text.bind("<Control-z>", lambda e: (result_text.edit_undo(), "break")) # Undo
result_text.bind("<Control-y>", lambda e: (result_text.edit_redo(), "break")) # Redo

# 5. Link Scrollbars
v_scroll.config(command=result_text.yview)
h_scroll.config(command=result_text.xview)

# 6. Pack
v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root.mainloop()
