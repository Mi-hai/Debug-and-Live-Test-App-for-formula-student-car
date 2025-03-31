# main.py
import sys
sys.dont_write_bytecode = True



# Importing the necessary modules
import customtkinter as ctk
from pages import Debug  # Importing page class
from PIL import Image, ImageTk
import os
import serial
from serial.tools import list_ports
import threading
import time
import platform



# Initialize the main window
root = ctk.CTk()
root.title("EVR app")
root.maxsize(1500,800)
root.resizable(True,True)
root.grid_rowconfigure(0, weight=1)
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
background_image = Image.open(image_path)
background_photo = ImageTk.PhotoImage(background_image)

# Create a canvas and set the background image
canvas = ctk.CTkCanvas(root, width=900, height=700)
canvas.grid(row=0, column=0, rowspan=4, columnspan=3, sticky="nsew")


# Function to resize the background image
def resize_image(event):
    new_width = event.width
    new_height = event.height
    resized_image = background_image.resize((new_width, new_height))
    background_photo = ImageTk.PhotoImage(resized_image)
    canvas.create_image(0, 0, anchor="nw", image=background_photo)
    canvas.image = background_photo  # Keep a reference to the image to prevent garbage collection

# Bind the resize event to the function
canvas.bind("<Configure>", resize_image)

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
try:
    input = detect_serial_port()
except:
    if platform.system() == "Windows":
        input = "COM1"
    elif platform.system() == "Linux":
        input = "/dev/ttyUSB0"
default_input = "/dev/ttyUSB0"

#Function to refresh the port
def refresh_port():
    global input
    input = detect_serial_port()
    label1.configure(text=f"Detected Port: {input}")

# Update the label to show the detected port
label1 = ctk.CTkLabel(
    root, 
    text=f"Detected Port: {input}", 
    font=("Arial", 13), 
    text_color="white", 
    bg_color="#363a3d"
)
label1.grid(row=3,column=1,pady=15)

def load_debug_page():
    """ Clears the window and loads the Debug page inside root. """
    for widget in root.winfo_children():
        widget.destroy()  # Remove all widgets from root

    # Call Debug class (make sure Debug is structured properly inside pages.py)
    Debug(root, input, default_input)  # Load Debug Page inside root



# Button to open secondary page
text_button_debug = ctk.CTkButton(root, text="Debug Page", command=lambda: load_debug_page(), border_width=3, border_color="black", width=200, height=40)
text_button_debug.grid(row=2,column=1,pady=0,sticky="s")


text_button_refresh = ctk.CTkButton(root, text="Port Refresh", command=refresh_port, border_width=3, border_color="black", width=120, height=35)
text_button_refresh.grid(row=3,column=1,pady=10,sticky="n")



# Run the Tkinter main loop
root.mainloop()