import pytesseract
from PIL import ImageGrab
import time

# --- CONFIGURATION ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # point to your tesseract.exe

def capture_and_read():
    print("--- SCREENSHOT OCR TOOL ---")
    print("Get ready! Taking a screenshot of the WHOLE screen in 5 seconds...")
    
    # Countdown to give you time to switch windows
    for i in range(5, 0, -1):
        print(f"{i}...", end=' ', flush=True)
        time.sleep(1)
    print("\n\n[!] SNAP! Processing image...")

    try:
        # 1. Take the Screenshot
        # input_img will be a PIL Image object
        input_img = ImageGrab.grab() 
        
        # 2. Convert Image to Text
        # We pass the image object directly to pytesseract
        detected_text = pytesseract.image_to_string(input_img)

        # 3. Output
        print("\n--- RESULT ---")
        if detected_text.strip():
            print(detected_text)
        else:
            print("[?] No text detected.")
        print("--------------")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Tip: Did you configure the Tesseract path correctly?")

if __name__ == "__main__":
    capture_and_read()