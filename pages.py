# pages.py
import sys
sys.dont_write_bytecode = True



# Importing the necessary modules
import customtkinter as ctk
import serial



buffer = []  # Store buffer globally if needed



# Live Test Page
class LiveTest(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("900x800")
        self.title("Live Test")
        self.resizable(False, False)



#  Debug Page
class Debug(ctk.CTkToplevel):
    def __init__(self, input, default_input, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("900x800")
        self.title("Debug Page")
        self.resizable(False, False)



        # Debug Page Label
        label = ctk.CTkLabel(self, text="Debug Page", font=("Arial", 25), text_color="white", fg_color="transparent")
        label.pack(pady=5)



        # Multi-line Text Box
        self.log_box = ctk.CTkTextbox(
         self,
         width=600, height=400,
         font=("Arial", 16), text_color="red",
         fg_color="#242424",border_width=1,border_color="black",
         activate_scrollbars=True)
        
        self.log_box.pack(pady=40)



        # Serial Setup
        if len(input) < 2:
            self.ser = serial.Serial(port=default_input, baudrate=9600, timeout=1)
        else:
            self.ser = serial.Serial(port=input, baudrate=9600, timeout=1)



        # Sets the first state of the port as off and setsup the buttons
        self.is_running = False
        self.setup_buttons()



    # Function to setup the buttons
    def setup_buttons(self):

        # Start Button
        self.text_button1 = ctk.CTkButton(self, text="Start", command=self.start, border_width=3, border_color="black")
        self.text_button1.pack(pady=10, ipadx=10)

        # Stop Button
        self.text_button2 = ctk.CTkButton(self, text="Stop", command=self.stop, border_width=3, border_color="black")
        self.text_button2.pack(pady=10, ipadx=10)

        # Print Data Button
        self.text_button3 = ctk.CTkButton(self, text="Print Data", command=self.get_text, border_width=3, border_color="black")
        self.text_button3.pack(pady=10, ipadx=10)

        # Clear log Button
        self.text_button4 = ctk.CTkButton(self, text="Clear log", command=lambda: self.log_box.delete("1.0", "end"), border_width=3, border_color="black")
        self.text_button4.pack(pady=10, ipadx=10)



    # Function to update the text box
    def update_textbox(self):
        if self.is_running:
            value = self.ser.readline().decode('utf-8').strip()
            if value:
                self.log_box.insert("1.0", value + "\n")
            self.after(1000, self.update_textbox)



    # Function to start the serial communication
    def start(self):
        self.is_running = True
        self.update_textbox()
        self.text_button3.configure(state="disabled")
        self.text_button1.configure(state="disabled")



    # Function to stop the serial communication
    def stop(self):
        self.is_running = False
        self.text_button3.configure(state="normal")
        self.text_button1.configure(state="normal")
        


    # Function to get the text from the serial communication
    def get_text(self):
        global buffer
        value=self.ser.readline().decode('utf-8').strip()
        ok=1
        for i in buffer:
            if i==value:
                for j in buffer:
                    self.log_box.insert("1.0",j+"\n")
                ok=0
                buffer.clear()
        if value:
            buffer.append(value)
        buffer.sort(reverse=True)
        print(buffer)
        if ok == 1:
            self.get_text()