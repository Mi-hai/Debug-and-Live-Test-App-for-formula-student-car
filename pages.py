# pages.py
import sys
sys.dont_write_bytecode = True



# Importing the necessary modules
import customtkinter as ctk
import serial



buffer = []  # Store buffer globally
index = []  # Store index globally

# Live Test Page
class LiveTest(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("900x800")
        self.title("Live Test")
        self.resizable(False, False)



#  Debug Page
class Debug(ctk.CTkToplevel):
    def __init__(self, input, default_input, filter_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("900x800")
        self.title("Debug Page")
        self.resizable(False, False)




        # Debug Page Label
        label = ctk.CTkLabel(self, text="Debug Page", font=("Arial", 25), text_color="white", fg_color="transparent")
        label.pack(pady=5)



        # Multi-line Text Box
        self.log_box1 = ctk.CTkTextbox(
            self,
            width=600, height=200,
            font=("Arial", 16), text_color="red",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box1.pack(pady=20)

        self.log_box2 = ctk.CTkTextbox(
            self,
            width=600, height=200,
            font=("Arial", 16), text_color="blue",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box2.pack(pady=20)



        # Serial Setup
        if len(input) < 2:
            self.ser = serial.Serial(port=default_input, baudrate=9600, timeout=1)
        else:
            self.ser = serial.Serial(port=input, baudrate=9600, timeout=1)



        # Sets the first state of the port as off and setups the buttons
        self.is_running = False
        self.setup_buttons()



        # Load filter criteria (IDs)
        self.filter_criteria = self.load_filter_criteria(filter_file)
        for i in self.filter_criteria:
            index.append(i)



    # Function to load filter criteria from a file (extract IDs)
    def load_filter_criteria(self, file_path):
        try:
            with open(file_path, "r") as file:
                criteria= set()  # Store only the IDs as a set
                for line in file:
                    if line.strip():
                        parts = line.split(":")
                        if parts:
                            id_part = parts[0].strip()  # Get the part before the colon
                            criteria.add(id_part)  # Add the ID to the set
                return criteria
        except FileNotFoundError:
            print(f"Filter file '{file_path}' not found.")
            return set()



    # Function to setup the buttons
    def setup_buttons(self):

        # Start Button
        self.text_button1 = ctk.CTkButton(self, text="Start", command=self.start, border_width=3, border_color="black")
        self.text_button1.pack(pady=10, ipadx=10)

        # Stop Button
        self.text_button2 = ctk.CTkButton(self, text="Stop", command=self.stop, border_width=3, border_color="black")
        self.text_button2.pack(pady=10, ipadx=10)

        # # Print Data Button
        # self.text_button3 = ctk.CTkButton(self, text="Print Data", command=self.get_text, border_width=3, border_color="black")
        # self.text_button3.pack(pady=10, ipadx=10)

        # Clear log Button
        self.text_button4 = ctk.CTkButton(self, text="Clear log", command=self.clear_logs, border_width=3, border_color="black")
        self.text_button4.pack(pady=10, ipadx=10)



    # Function to update the text box
    def update_textbox(self):
        global index
        if self.is_running:
            # Read and decode the incoming data from serial
            raw_value = self.ser.readline().decode('utf-8').strip()
            if raw_value:
                # Parse the ID and message (assuming IDs are single-digit numbers or can be extended to more characters)
                id_part = raw_value[0].strip()  # Extract everything before the first colon (ID)
                message_part = raw_value[1:].strip()  # Extract the part after the colon (message)
                # Check if the ID is in the filter criteria
                print(ord(id_part))
                for i in range(len(index)):
                    if ord(id_part) == int(index[i]):
                        
                        # Route to the appropriate log box (you can modify this logic as needed)
                        if ord(id_part) == 1:
                            self.log_box1.insert("1.0", message_part + "\n")
                        elif ord(id_part) == 2:
                            self.log_box2.insert("1.0", message_part + "\n")
                        # Add more conditions if needed for other IDs
                        else:
                            # Log for other filtered IDs if required
                            self.log_box2.insert("1.0", f"ID {id_part}: {message_part}\n")

            # Schedule the next update
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
        


    # # Function to get the text from the serial communication
    # def get_text(self):
    #     global buffer
    #     value=self.ser.readline().decode('utf-8').strip()
    #     ok=1
    #     for i in buffer:
    #         if i==value:
    #             for j in buffer:
    #                 self.log_box.insert("1.0",j+"\n")
    #             ok=0
    #             buffer.clear()
    #     if value:
    #         buffer.append(value)
    #     buffer.sort(reverse=True)
    #     print(buffer)
    #     if ok == 1:
    #         self.get_text()


    # Function to clear both logs
    def clear_logs(self):
        self.log_box1.delete("1.0", "end")
        self.log_box2.delete("1.0", "end")