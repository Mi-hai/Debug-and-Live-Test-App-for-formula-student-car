import sys
import sqlite3
sys.dont_write_bytecode = True

import customtkinter as ctk
import serial

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

buffer = []  # Store buffer globally
index = []  # Store index globally

class LiveTest(ctk.CTkToplevel):
    def __init__(self, input, default_input, filter_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("900x800")
        self.title("Live Test")
        self.resizable(True, True)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.battery_history={}
        self.current_battery_id = None

        # Initialize database connection and cursor here
        self.conn = sqlite3.connect('battery.db')
        self.c = self.conn.cursor()

        # Create battery_table if not exists
        self.c.execute('''CREATE TABLE IF NOT EXISTS battery_table(
            battery_id INTEGER PRIMARY KEY,
            battery_voltage REAL,
            battery_state CHAR(16)
        )''')

        # Initialize serial connection
        if len(input) < 2:
            self.ser = serial.Serial(port=default_input, baudrate=9600, timeout=1)
        else:
            self.ser = serial.Serial(port=input, baudrate=9600, timeout=1)

        # Load filter criteria
        self.filter_criteria = self.load_filter_criteria(filter_file)
        for i in self.filter_criteria:
            index.append(i)

        # Start UI components
        self.create_dropdown_and_screen()
        self.get_data()

    #Create the filter criteria
    def load_filter_criteria(self, file_path):
        try:
            with open(file_path, "r") as file:
                criteria = set()  # Store only the IDs as a set
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

    # Function to get data from the serial port and insert into the database
    def get_data(self):
        raw_value = self.ser.readline().decode('utf-8')
        if raw_value:
            # Parse the ID and message (assuming IDs are single-digit numbers or can be extended to more characters)
            id_part = raw_value[0]  # Extract everything before the first colon (ID)
            message_part1 = raw_value[1:].strip()  # Extract the part after the colon (message)
            if":" in message_part1:
                id ,message_part= message_part1.split(":",1)
                id =id.strip()
                message_part = message_part.strip()
                # Check if the ID is in the filter criteria
                #print(ord(id_part))
                for i in range(len(index)):
                    if ord(id_part) in range(1, 5):
                        if ";" in message_part:
                                # Split the message part on ';' to separate voltage and state
                                voltage, state = message_part.split(";")
                                voltage = voltage.strip()  # Extract voltage
                                state = state.strip()      # Extract state (e.g., Charging or Discharging)
                                # Update battery voltage history
                                if id not in self.battery_history:
                                    self.battery_history[id] = []
                                self.battery_history[id].append(float(voltage))

                                # Insert data into the database
                                self.c.execute('''
                                INSERT INTO battery_table (battery_id, battery_voltage, battery_state)
                                VALUES (?, ?, ?)
                                ON CONFLICT(battery_id) DO UPDATE SET 
                                    battery_voltage = excluded.battery_voltage,
                                    battery_state = excluded.battery_state
                            ''', (id, voltage, state))
                                #print(f"ID: {id}, Voltage: {voltage}, State: {state}")
                                self.conn.commit()
                                self.refresh_dropdown()
                        if id == self.current_battery_id:
                             self.refresh_graph()


        # Schedule the next update
        self.after(1000, self.get_data)

    # Function to refresh the dropdown menu with updated data
    def refresh_dropdown(self):
        # Fetch updated data from the database
        self.c.execute('SELECT battery_id, battery_voltage, battery_state FROM battery_table')
        rows = self.c.fetchall()

        # Format data for the dropdown
        self.options = [f"Battery {row[0]}" for row in rows]  # Use only the battery_id for display

        # Update the dropdown menu with the new options
        self.dropdown.configure(values=self.options)

    # Function to create the dropdown menu and screen
    def create_dropdown_and_screen(self):
        # Fetch data from the database
        self.c.execute('SELECT battery_id, battery_voltage, battery_state FROM battery_table')
        rows = self.c.fetchall()

        # Format data for the dropdown: "Index - Name - Voltage - Status"
        self.options = []
        for row in rows:
            battery_id, voltage, state = row
            self.options.append(f"Battery {battery_id}")

        # Create the dropdown menu
        self.dropdown = ctk.CTkComboBox(
            self,
            values=self.options,
            command=self.update_screen,  # Only called when dropdown value changes
            state="readonly", height=60, font=("Arial", 16)
        )
        self.dropdown.configure(dropdown_font=("Arial", 24))
        self.dropdown.set("Select a Battery")
        self.dropdown.grid(row=0, column=0, padx=20, sticky="ew")

        # Create a screen to display the selected battery data
        self.screen = ctk.CTkTextbox(
            self,
            width=600, height=200,
            font=("Arial", 16), text_color="red",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True
        )
        self.screen.grid(row=1, column=1, padx=10, sticky="new")
        
        # Add a graph to the UI
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="new")

    def update_screen(self, choice):
        # Extract battery_id from the choice (assuming format: "Battery <id> - ...")
        if choice.startswith("Battery"):
            battery_id = choice.split()[1]
            self.current_battery_id = battery_id
            self.refresh_graph()

            # Fetch detailed information for the selected battery
            self.c.execute('SELECT battery_voltage, battery_state FROM battery_table WHERE battery_id = ?', (battery_id,))
            result = self.c.fetchone()

            if result:
                voltage, state = result
                self.screen.delete("1.0", "end")
                self.screen.insert("1.0", f"Battery {battery_id}:\nVoltage: {voltage}V\nState: {state}")
            else:
                self.screen.delete("1.0", "end")
                self.screen.insert("1.0", f"Battery {battery_id} details not found.")


    # Function to refresh the graph with updated data
    def refresh_graph(self):
        if self.current_battery_id in self.battery_history:
            self.ax.clear()
            self.ax.plot(self.battery_history[self.current_battery_id], label=f"Battery {self.current_battery_id} Voltage")
            self.ax.set_title(f"Battery {self.current_battery_id} Voltage Evolution")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Voltage (V)")
            self.ax.legend()
            self.canvas.draw()
            
            self.c.execute('SELECT battery_voltage, battery_state FROM battery_table WHERE battery_id = ?', (self.current_battery_id,))
            result = self.c.fetchone()

            if result:
                voltage, state = result
                self.screen.delete("1.0", "end")
                self.screen.insert("1.0", f"Battery {self.current_battery_id}:\nVoltage: {voltage}V\nState: {state}")
            else:
                self.screen.delete("1.0", "end")
                self.screen.insert("1.0", f"Battery {self.current_battery_id} details not found.")

    def on_close(self):
        # Close the database connection and kill graph window
        if self.ser.is_open:
            self.ser.close()
        plt.close(self.figure)
        self.canvas.get_tk_widget().destroy()
        self.c.execute('DELETE FROM battery_table')
        self.conn.commit()
        self.c.execute('DROP TABLE IF EXISTS battery_table')
        self.conn.commit()
        self.conn.close()
        self.destroy()
#  Debug Page
class Debug(ctk.CTkToplevel):
    def __init__(self, input, default_input, filter_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("900x800")
        self.title("Debug Page")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)




        #Make the setup for resizable window
        self.grid_rowconfigure(1, weight=1) # Row for textboxes
        self.grid_columnconfigure(0, weight=1)  # Column for log_box1
        self.grid_columnconfigure(1, weight=1)  # Column for log_box2
        self.grid_columnconfigure(2, weight=1)  # Column for log_box3



        # Debug Page Label
        label = ctk.CTkLabel(self, text="Debug Page", font=("Arial", 25), text_color="white", fg_color="transparent")
        label.grid(row=0, column=1, pady=10)



        # Multi-line Text Box
        self.log_box1 = ctk.CTkTextbox(
            self,
            width=600, height=200,
            font=("Arial", 16), text_color="red",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box1.grid(row=1, column=0, padx=10, sticky="nsew",)

        self.log_box2 = ctk.CTkTextbox(
            self,
            width=600, height=200,
            font=("Arial", 16), text_color="blue",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box2.grid(row=1, column=1, padx=10, sticky="nsew")

        self.log_box3 = ctk.CTkTextbox(
            self,
            width=600, height=200,
            font=("Arial", 16), text_color="green",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box3.grid(row=1, column=2, padx=10, sticky="nsew")
        


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
        self.text_button1.grid(row=3,column=1, pady=10, ipadx=10)

        # Stop Button
        self.text_button2 = ctk.CTkButton(self, text="Stop", command=self.stop, border_width=3, border_color="black")
        self.text_button2.grid(row=4,column=1, pady=10, ipadx=10)

        # Clear log Button
        self.text_button4 = ctk.CTkButton(self, text="Clear log", command=self.clear_logs, border_width=3, border_color="black")
        self.text_button4.grid(row=5,column=1, pady=10, ipadx=10)



    # Function to update the text box
    def update_textbox(self):
        global index
        if self.is_running:
            # Read and decode the incoming data from serial
            raw_value = self.ser.readline().decode('utf-8')
            if raw_value:
                # Parse the ID and message (assuming IDs are single-digit numbers or can be extended to more characters)
                id_part = raw_value[0]  # Extract everything before the first colon (ID)
                message_part = raw_value[1:].strip()  # Extract the part after the colon (message)
                # Check if the ID is in the filter criteria
                #print(ord(id_part))
                for i in range(len(index)):
                    if ord(id_part) == int(index[i]):
                        # Route to the appropriate log box (you can modify this logic as needed)
                        if ord(id_part) in range(1, 10) :
                            self.log_box1.insert("1.0",message_part+"\n")
                        elif ord(id_part) in range(10, 20):
                            self.log_box2.insert("1.0",message_part+"\n")
                        elif ord(id_part) in range(20, 128):
                            self.log_box3.insert("1.0",message_part+"\n")
                        else:
                            # Log for other filtered IDs if required
                            self.log_box2.insert("1.0", f"ID {id_part}: {message_part}\n")

            # Schedule the next update
            self.after(1000, self.update_textbox)



    # Function to start the serial communication
    def start(self):
        self.is_running = True
        self.ser.reset_input_buffer()  # Clears the input buffer
        self.ser.reset_output_buffer()  # Clears the output buffer
        self.update_textbox()
        #self.text_button3.configure(state="disabled")
        self.text_button1.configure(state="disabled")



    # Function to stop the serial communication
    def stop(self):
        self.is_running = False
        #self.text_button3.configure(state="normal")
        self.text_button1.configure(state="normal")
        


    # Function to clear all logs
    def clear_logs(self):
        self.log_box1.delete("1.0", "end")
        self.log_box2.delete("1.0", "end")
        self.log_box3.delete("1.0", "end")
    
    def on_close(self):
        if self.ser.is_open:
            self.ser.close()
        self.destroy()