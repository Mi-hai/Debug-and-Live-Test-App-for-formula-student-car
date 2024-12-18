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
root.minsize(900,700)
root.resizable(True,True)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)


# Set up the appearance and theme for the GUI
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme("blue")


# Background Image for the GUI
# Set the path for the assets folder based on the runtime environment
if hasattr(sys, "_MEIPASS"):
    # Running as a bundled app
    assets_path = os.path.join(sys._MEIPASS, "assets")
else:
    # Running as a script
    assets_path = os.path.join(os.path.dirname(__file__), "assets")
image_path = os.path.join(assets_path, "logo.jpeg")
my_image = ctk.CTkImage(dark_image=Image.open(image_path), size=(900, 700))
image_label = ctk.CTkLabel(root, image=my_image, text="")
image_label.grid(row=0,column=0,columnspan=3,rowspan=3)
image_label.lower()



# Function to detect available serial ports
def detect_serial_port(filter_keyword="ttyUSB"):
    ports = list(list_ports.comports())
    for port in ports:
        # Check if the filter_keyword matches the device name or description
        if filter_keyword is None or (filter_keyword in port.device or filter_keyword in port.description):
            return port.device
    return port.device
    return None

# Detect serial port or use default
input = detect_serial_port()
default_input = "/dev/ttyUSB0"

# Update the label to show the detected port
label1 = ctk.CTkLabel(
    root, 
    text=f"Detected Port: {input}", 
    font=("Arial", 15), 
    text_color="white", 
    bg_color="#363a3d"
)
label1.grid(row=3,column=1,pady=20)



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
text_button_debug.grid(row=3,column=0,pady=50)

text_button_live_test = ctk.CTkButton(root, text="Live Test", command=lambda: LiveTest(input, default_input,filter_file=path1), border_width=3, border_color="black", width=200, height=70)
text_button_live_test.grid(row=3,column=2,pady=50)






# Run the Tkinter main loop
root.mainloop()