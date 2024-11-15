# main.py
import sys
sys.dont_write_bytecode = True



# Importing the necessary modules
import customtkinter as ctk
from pages import Debug, LiveTest  # Importing page classes
from PIL import Image
import os



# Initialize the main window
root = ctk.CTk()
root.title("EVR app")
root.geometry("1920x1080")
root.resizable(False, False)



# Set up the appearance and theme for the GUI
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme("blue")



# Initialize the input variables
input = ""
default_input = "/dev/ttyUSB0"



# Function to set up the input section
def setup_input_section(root):
    global input
    label1 = ctk.CTkLabel(root, text="Add Port /dev/ttyUSB0 or /dev/ttyACM0 \n Search in /dev folder", font=("Arial", 15), text_color="white", bg_color="#363a3d")
    label1.place(x=800, y=750)
    


    # Create an input field (CTkEntry)
    input_entry = ctk.CTkEntry(root, placeholder_text="/dev/tty...", border_width=1, border_color="black")
    input_entry.place(x=865, y=790)  # Adds padding around the input field



    # Function to retrieve the input from the input field
    def retrieve_input():
        global input
        input = input_entry.get().strip()  # Retrieve the text from the input field
        input_entry.delete(0, "end")

    submit_button = ctk.CTkButton(root, text="Submit", command=retrieve_input, border_width=1, border_color="black")
    submit_button.place(x=865, y=830)



# Set up input section on main page
setup_input_section(root)



# Buttons to open secondary pages
text_button_debug = ctk.CTkButton(root, text="Debug Page", command=lambda: Debug(input, default_input), border_width=3, border_color="black", width=200, height=70)
text_button_debug.place(x=400, y=550)

text_button_live_test = ctk.CTkButton(root, text="Live Test", command=lambda: LiveTest(), border_width=3, border_color="black", width=200, height=70)
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
