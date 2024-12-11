# main.py
import sys
sys.dont_write_bytecode = True



# Importing the necessary modules
import customtkinter as ctk
from pages import Debug, LiveTest  # Importing page classes
from PIL import Image
import os
import serial
from serial.tools import list_ports


# Initialize the main window
root = ctk.CTk()
root.title("EVR app")
root.geometry("1920x1080")
root.resizable(False, False)



# Set up the appearance and theme for the GUI
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme("blue")





# Function to detect available serial ports
def detect_serial_port():
    ports = list(list_ports.comports())
    for port in ports:
            return port.device
    return None

# Detect serial port or use default
input = detect_serial_port() or "/dev/ttyUSB0"
default_input = "/dev/ttyUSB0"

# Update the label to show the detected port
label1 = ctk.CTkLabel(
    root, 
    text=f"Detected Port: {input}\nSearch in /dev folder if incorrect", 
    font=("Arial", 15), 
    text_color="white", 
    bg_color="#363a3d"
)
label1.place(x=800, y=750)



# Set the path for the Filter file based on the runtime environment
if hasattr(sys, "_MEIPASS"):
    # Running as a bundled app
    assets_path = os.path.join(sys._MEIPASS)
else:
    # Running as a script
    assets_path = os.path.join(os.path.dirname(__file__))
path1 = os.path.join(assets_path, "Filter.txt")



# Buttons to open secondary pages
text_button_debug = ctk.CTkButton(root, text="Debug Page", command=lambda: Debug(input, default_input,filter_file=path1), border_width=3, border_color="black", width=200, height=70)
text_button_debug.place(x=400, y=550)

text_button_live_test = ctk.CTkButton(root, text="Live Test", command=lambda: LiveTest(input, default_input,filter_file=path1), border_width=3, border_color="black", width=200, height=70)
text_button_live_test.place(x=1235, y=550)



# Background Image for the GUI
# Set the path for the assets folder based on the runtime environment
if hasattr(sys, "_MEIPASS"):
    # Running as a bundled app
    assets_path = os.path.join(sys._MEIPASS, "assets")
else:
    # Running as a script
    assets_path = os.path.join(os.path.dirname(__file__), "assets")
image_path = os.path.join(assets_path, "logo.jpeg")
my_image = ctk.CTkImage(dark_image=Image.open(image_path), size=(1920, 1000))
image_label = ctk.CTkLabel(root, image=my_image, text="")
image_label.place(x=0, y=-40, relwidth=1, relheight=1)
image_label.lower()



# Run the Tkinter main loop
root.mainloop()