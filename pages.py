import sys
import sqlite3
sys.dont_write_bytecode = True

import customtkinter as ctk
import serial
import numpy as np
import os
from tabulate import tabulate
import threading
from queue import Queue
import time
import random  

#  Debug Page
class Debug(ctk.CTkFrame):
    def __init__(self, parent, input, default_input, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid(sticky="nsew",rowspan=4,columnspan=3)
        #Create the widgets
        self.create_widgets()

        #Initialize serial
        self.serial(input,default_input)

        #Multithreading
        self.data_queue=Queue()
        self.stop_event=threading.Event()
        self.is_running=False

        #Setup the vairaibles
        self.setup_variables()

        #Setup the buttons
        self.setup_buttons()

        #Start the thread
        self.start_thread()
    
    def create_widgets(self):
        """Function to create all widgets for temp, voltage, time, data summary and errors using CustomTk textboxes"""
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0) 
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        #==========================================================================
        """Temperature"""
        self.log_box1 = ctk.CTkTextbox(
            self,
            font=("Arial", 14), 
            text_color="white",
            fg_color="#242424", 
            border_width=1, 
            border_color="black",
            activate_scrollbars=True)
        self.log_box1.grid(row=0, column=0, padx=20, pady=30, sticky="nsew", rowspan=2)

        #==========================================================================
        """Voltage"""
        self.log_box2 = ctk.CTkTextbox(
            self,
            font=("Arial", 14), 
            text_color="white",
            fg_color="#242424", 
            border_width=1, 
            border_color="black",
            activate_scrollbars=True)
        self.log_box2.grid(row=0, column=1, padx=20, pady=30, sticky="nsew", rowspan=2)

        #==========================================================================
        """Time"""
        self.log_box3 = ctk.CTkTextbox(
            self,
            font=("Arial", 16), 
            text_color="white",
            fg_color="#242424", 
            border_width=1, 
            border_color="black",
            activate_scrollbars=True)
        self.log_box3.grid(row=0, column=2, padx=20, pady=30, sticky="nsew", rowspan=2)

        #==========================================================================
        """Data summary"""
        self.log_box4 = ctk.CTkTextbox(
            self,
            font=("Arial", 16), 
            text_color="white",
            fg_color="#242424", 
            border_width=1, 
            border_color="black",
            activate_scrollbars=True)
        self.log_box4.grid(row=0, column=3, padx=20, pady=30, sticky="nsew")

        """Errors"""
        self.log_box5 = ctk.CTkTextbox(
            self,
            font=("Arial", 16), 
            text_color="white",
            fg_color="#242424", 
            border_width=1, 
            border_color="black",
            activate_scrollbars=True)
        self.log_box5.grid(row=1, column=3, padx=20, pady=20, sticky="nsew")

        self.log_box1.configure(state="disable")
        self.log_box2.configure(state="disable")
        self.log_box3.configure(state="disable")
        self.log_box4.configure(state="disable")
        self.log_box5.configure(state="disable")


    def serial(self,input,default_input):
        try:
            port=default_input if len(input) < 2 else input
            self.ser=serial.Serial(port,9600,timeout=1)
        except:
            self.log_box1.configure(state="normal")
            self.log_box2.configure(state="normal")
            self.log_box3.configure(state="normal")
            self.log_box4.configure(state="normal")
            self.log_box5.configure(state="normal")
            self.log_box1.insert("1.0", f"Serial error\nCould not open port\nOr Permission Denied\nPort:{input}")
            self.log_box2.insert("1.0", f"Serial error\nCould not open port\nOr Permission Denied\nPort:{input}")
            self.log_box3.insert("1.0", f"Serial error\nCould not open port\nOr Permission Denied\nPort:{input}")
            self.log_box4.insert("1.0", f"Serial error\nCould not open port\nOr Permission Denied\nPort:{input}")
            self.log_box5.insert("1.0", f"Serial error\nCould not open port\nOr Permission Denied\nPort:{input}")
            self.log_box1.configure(state="disable")
            self.log_box2.configure(state="disable")
            self.log_box3.configure(state="disable")
            self.log_box4.configure(state="disable")
            self.log_box5.configure(state="disable")
            self.ser=None

    def setup_variables(self):
        """Declaring and initilaizing all the variables used in the code"""
        self.header = 0
        self.bufferdata = []
        self.lowest_temp = 9999999
        self.lowest_BMS_V = 9999999
        self.lowest_BMS_A = 9999999
        self.accel1 = 9999999
        self.accel2 = 9999999
        self.frana = 9999999
        self.timp = 0
        self.errtemp = ["","","","","","","",""]
        self.errbms = ["","","","","","","",""]
        self.errpedals = ["","","","","","","",""]
        self.errpedalsf = ["","","","","","","",""]
        self.err7seg = ["","","","","","","",""]
        self.errproc = ["","","","","","","",""]
        self.temp = np.zeros(128)
        self.bmsv = np.zeros(600)
        self.data = 0
    
    def setup_buttons(self):
        # Start Button
        self.text_button1 = ctk.CTkButton(self, text="Start", command=self.start, border_width=3, border_color="black",fg_color="green",hover_color="#2d6714",height=50)
        self.text_button1.grid(row=2, column=0, pady=10, ipadx=10, sticky="ew")

        # Stop Button
        self.text_button2 = ctk.CTkButton(self, text="Stop", command=self.stop, border_width=3, border_color="black",fg_color="red",hover_color="#cc0909",height=50)
        self.text_button2.grid(row=2, column=1, pady=10, ipadx=10, sticky="ew")

        # Clear log Button
        self.text_button4 = ctk.CTkButton(self, text="Clear log", command=self.clear_logs, border_width=3, border_color="black",height=50)
        self.text_button4.grid(row=2, column=2, pady=10, ipadx=10, sticky="ew")

        # EasterEgg Button
        self.text_button5 = ctk.CTkButton(self,text="Easter Egg",text_color="#2b2b2b", command=self.easter_egg, border_width=3, fg_color="#2b2b2b",border_color="#2b2b2b",hover_color="#2b2b2b",height=50)
        self.text_button5.grid(row=2, column=3, pady=10, ipadx=10, sticky="ew")
    
    def start_thread(self):
        """Start serial reading and GUI update threads"""
        self.read_thread = threading.Thread(target=self.read_serial, daemon=True)
        self.read_thread.start()
        self.after(100, self.process_serial_data)

    def read_serial(self):
        """Read data from serial port in background thread"""
        while not self.stop_event.is_set():
            if self.is_running and self.ser and self.ser.is_open:
                try:
                    if self.ser.in_waiting:
                        data = self.ser.read(self.ser.in_waiting)
                        self.data_queue.put(data)
                except serial.SerialException as e:
                    self.log_box1.configure(state="normal")
                    self.log_box2.configure(state="normal")
                    self.log_box3.configure(state="normal")
                    self.log_box4.configure(state="normal")
                    self.log_box5.configure(state="normal")
                    self.log_box1.insert("1.0", f"Serial error: {e}\n")
                    self.log_box2.insert("1.0", f"Serial error: {e}\n")
                    self.log_box3.insert("1.0", f"Serial error: {e}\n")
                    self.log_box4.insert("1.0", f"Serial error: {e}\n")
                    self.log_box5.insert("1.0", f"Serial error: {e}\n")
                    self.log_box1.configure(state="disable")
                    self.log_box2.configure(state="disable")
                    self.log_box3.configure(state="disable")
                    self.log_box4.configure(state="disable")
                    self.log_box5.configure(state="disable")
                    self.is_running = False
            time.sleep(0.01)
    
    def process_serial_data(self):
        """Process serial data in main thread"""
        while not self.data_queue.empty():
            data = self.data_queue.get()
            self.bufferdata += list(data)
            self.parse_buffer()
        self.after(100, self.process_serial_data)
    

    def parse_buffer(self):
        """Separate the buffer data"""
        while len(self.bufferdata) > 0:
            # Only get a new header if we don't have one already
            if self.header == 0:
                self.header = self.bufferdata.pop(0)
            
            try:
                # Temperature (header 10, needs 5 bytes)
                if self.header == 10:
                    if len(self.bufferdata)<5:
                        break
                    self.process_temp()
                    self.header = 0
                    continue

                # BMS Voltage (header 11, needs 8 bytes)
                elif self.header == 11:
                    if len(self.bufferdata)<8:
                        break
                    self.process_bmsv()
                    self.header = 0
                    continue

                # BMS Current (header 12, needs 6 bytes)
                elif self.header == 12:
                    if len(self.bufferdata)<6:
                        break
                    self.process_bmsa()
                    self.header = 0
                    continue
                
                # Accelerator pedal (header 13, needs 6 bytes)
                elif self.header == 13:
                    if len(self.bufferdata)<6:
                        break
                    self.process_acc()
                    self.header = 0  
                    continue
                
                # Brake pedal (header 14, needs 4 bytes)
                elif self.header == 14:
                    if len(self.bufferdata)<4:
                        break
                    self.process_brake()
                    self.header = 0
                    continue

                # Time module (header 17, needs 7 bytes)
                elif self.header == 17:
                    if len(self.bufferdata)<7:
                        break
                    self.process_time()
                    self.header = 0
                    continue
                
                # Errors (header 9, needs 3 bytes)
                elif self.header == 9:
                    if len(self.bufferdata)<3:
                        break
                    self.process_errors()
                    self.header = 0
                    continue
                
                # elif self.header == 18 and len(self.bufferdata) >= 
                
                else:
                    # If we get here, we have a header but not enough data
                    # for a complete message, so break and wait for more data
                    break
                    
            except Exception as e:
                print(f"Error processing message (header {self.header}): {e}")
                # Clear the header to start fresh on next message
                self.header = 0
                break
                
            finally:
                # Only reset header if we processed a complete message
                # (this won't execute if we hit the 'break' above)
                self.header = 0
                
    def process_temp(self):
        """Process temperature data"""
        mesaj = []
        for i in range(5):
            mesaj.append(self.bufferdata.pop(0))
        if self.crc_verify(mesaj)==0:
            celula=mesaj[0]
            valoare=float(mesaj[1]*256+mesaj[2])/10**mesaj[3]
            self.temp[celula]=valoare
            if valoare<self.lowest_temp:
                self.lowest_temp=valoare
            self.update_temp()
            self.update_text()
            self.header = 0
        else:
            print("Error1")
    
    def process_bmsv(self):
        """Process BMS voltage data"""
        mesaj = []
        
        for i in range(8):
            mesaj.append(self.bufferdata.pop(0))
        if self.crc_verify(mesaj)==0:
            celula=mesaj[0]*256+mesaj[1]
            valoare=float(mesaj[2]*256+mesaj[3])/10**mesaj[4]
            self.bmsv[celula]=valoare
            if valoare<self.lowest_BMS_V:
                self.lowest_BMS_V=valoare
            self.update_bmsv()
            self.update_text()
            self.header = 0
        else:
            print("Error2")
    
    def process_bmsa(self):
        """Process BMS current data"""
        mesaj = []
        for i in range(6):
            mesaj.append(self.bufferdata.pop(0))
        if self.crc_verify(mesaj)==0:
            valoare = float(mesaj[0]*256+mesaj[1])/10**mesaj[2]
            if valoare<self.lowest_BMS_A:
                self.lowest_BMS_A = valoare
            self.update_text()
            self.header = 0
        else:
            print("Error3")
    
    def process_acc(self):
        """Process accelerator pedal data"""
        mesaj = []
        for i in range(6):
            mesaj.append(self.bufferdata.pop(0))
        if self.crc_verify(mesaj)==0:
            self.accel1 = float(mesaj[0] * 256 + mesaj[1]) / (10 ** mesaj[4])
            self.accel2 = float(mesaj[2] * 256 + mesaj[3]) / (10 ** mesaj[4])
            self.update_text()
            self.header = 0
        else:
            print("Error4")
    
    def process_brake(self):
        """Process brake pedal data"""
        mesaj = []
        for i in range(4):
            mesaj.append(self.bufferdata.pop(0))  
        if self.crc_verify(mesaj)==0: 
            self.frana = float(mesaj[0] * 256 + mesaj[1]) / (10 ** mesaj[2])
            self.update_text()
            self.header = 0
        else:
            print("Error5")

    def process_time(self):
        """Process time data"""
        self.log_box3.configure(state="normal")
        mesaj = []
        for i in range(7):
            mesaj.append(self.bufferdata.pop(0))
        if self.crc_verify(mesaj)==0:
            self.timp = float(mesaj[2] * 256**3 + mesaj[3] * 256**2 + mesaj[4] * 256 + mesaj[5])/(10**mesaj[6])
            self.update_text()
            self.log_box3.insert("1.0", f"Time: {self.timp}\n")
            self.header = 0
            self.log_box3.configure(state="disable")
        else:
            print("Error6")
        
    def process_errors(self):
        """Process errors"""
        mesaj=[]
        for i in range(3):
            mesaj.append(self.bufferdata.pop(0))
        if self.crc_verify(mesaj)==0:
            modul = mesaj[0]
            print(modul)
            valoare = bin(mesaj[1])[2:].zfill(8)
            valoare1 = int(valoare)

            if modul == 10:  # Temperature errors
                self.process_temp_errors(valoare1)
            elif modul in (11, 12):  # BMS errors
                self.process_bms_errors(valoare1)
            elif modul == 13:  # Pedal errors
                self.process_pedal_errors(valoare1)
            elif modul == 14:  # Brake errors
                self.process_brake_errors(valoare1)
            elif modul == 15:  # 7seg errors
                self.process_7seg_errors(valoare1)
            elif modul == 16:  # Processor errors
                self.process_proc_errors(valoare1)
            else:
                print("Error: Unknown module")

            self.update_error()
            self.header = 0
        else:
            print("Error7")


    def process_temp_errors(self, valoare1):
        """Temperature errors"""
        for i in range(8):
            if valoare1 % 10 == 1 and i == 0:
                self.errtemp[i] = "Temperature: too HIGH"
            else:
                self.errtemp[i] = "Temperature: Normal"
            valoare1 = valoare1 // 10

    def process_bms_errors(self, valoare1):
        """BMS errors"""
        for i in range(8):
            if valoare1 % 10 == 1:
                if i == 0:
                    self.errbms[i] = "BMS: No Response"
                elif i == 1:
                    self.errbms[i] = "BMS: Low Voltage"
                elif i == 2:
                    self.errbms[i] = "BMS: High Consumption"
            else:
                self.errbms[i] = "BMS: Normal"
            valoare1 = valoare1 // 10

    def process_pedal_errors(self, valoare1):
        """Pedal errors"""
        for i in range(8):
            if valoare1 % 10 == 1:
                if i == 0:
                    self.errpedals[i] = "Pedals: Different OutPut"
                elif i == 1:
                    self.errpedals[i] = "Pedals: Shorted"
                elif i == 2:
                    self.errpedals[i] = "Pedals: No OutPut"
            else:
                self.errpedals[i] = "Pedals: Normal"
            valoare1 = valoare1 // 10

    def process_brake_errors(self, valoare1):
        """Brake errors"""
        for i in range(8):
            if valoare1 % 10 == 1:
                if i == 0:
                    self.errpedalsf[i] = "Break: Shorted"
                elif i == 1:
                    self.errpedalsf[i] = "Break: No OutPut"
            else:
                self.errpedalsf[i] = "Break: Normal"
            valoare1 = valoare1 // 10

    def process_7seg_errors(self, valoare1):
        """7seg errors"""
        for i in range(8):
            if valoare1 % 10 == 1:
                if i == 0:
                    self.err7seg[i] = "7seg: Bus is Broken"
                elif i == 1:
                    self.err7seg[i] = "7seg: Number too large"
                elif i == 2:
                    self.err7seg[i] = "7seg: Wrong Segment"
            else:
                self.err7seg[i] = "7seg: Normal"
            valoare1 = valoare1 // 10

    def process_proc_errors(self, valoare1):
        """Processor errors"""
        for i in range(8):
            if valoare1 % 10 == 1 and i == 0:
                self.errproc[i] = "Processor: Reset"
            else:
                self.errproc[i] = "Processor: Normal"
            valoare1 = valoare1 // 10
    
    def update_text(self):
        """Updating the Summary data widget"""
        self.log_box4.configure(state="normal")
        text=(f"Lowest Temp: {self.lowest_temp:.2f}\n\n"
              f"Lowest BMS V: {self.lowest_BMS_V:.2f}\n\n"
              f"Lowest BMS A: {self.lowest_BMS_A:.2f}\n\n"
              f"Accel(%): P1: {self.accel1:.2f} - P2: {self.accel2:.2f}\n\n"
              f"Brake(%): {self.frana:.2f}\n\n"
              f"Time: {self.timp:.2f}\n\n"
        )
        self.log_box4.delete("1.0","end")
        self.log_box4.insert("end",text)
        self.log_box4.configure(state="disable")

    def update_error(self):
        """Update error widget"""
        self.log_box5.configure(state="normal")
        error_messages = []
                # Temperature errors
        if self.errtemp[0] == "Temperature: too HIGH":
            error_messages.append("Temperature:⚠️ too HIGH\n")
        else:
            error_messages.append("Temperature: Normal\n")

        # BMS errors
        bms_errors = False
        if self.errbms[0] == "BMS: No Response":
            error_messages.append("BMS:⚠️ No Response\n")
            bms_errors = True
        if self.errbms[1] == "BMS: Low Voltage":
            error_messages.append("BMS:⚠️ Low Voltage\n")
            bms_errors = True
        if self.errbms[2] == "BMS: High Consumption":
            error_messages.append("BMS:⚠️ High Consumption\n")
            bms_errors = True
        if not bms_errors:
            error_messages.append("BMS: Normal\n")

        # Pedal errors
        pedal_errors = False
        if self.errpedals[0] == "Pedals: Different OutPut":
            error_messages.append("Pedals:⚠️ Different Output\n")
            pedal_errors = True
        if self.errpedals[1] == "Pedals: Shorted":
            error_messages.append("Pedals:⚠️ Shorted\n")
            pedal_errors = True
        if self.errpedals[2] == "Pedals: No OutPut":
            error_messages.append("Pedals:⚠️ No Output\n")
            pedal_errors = True
        if not pedal_errors:
            error_messages.append("Pedals: Normal\n")

        # Brake errors
        brake_errors = False
        if self.errpedalsf[0] == "Break: Shorted":
            error_messages.append("Break:⚠️ Shorted\n")
            brake_errors = True
        if self.errpedalsf[1] == "Break: No OutPut":
            error_messages.append("Break:⚠️ No Output\n")
            brake_errors = True
        if not brake_errors:
            error_messages.append("Break: Normal\n")

        # 7seg errors
        seg_errors = False
        if self.err7seg[0] == "7seg: Bus is Broken":
            error_messages.append("7seg:⚠️ Bus is Broken\n")
            seg_errors = True
        if self.err7seg[1] == "7seg: Number too large":
            error_messages.append("7seg:⚠️ Number too large\n")
            seg_errors = True
        if self.err7seg[2] == "7seg: Wrong Segment":
            error_messages.append("7seg:⚠️ Wrong Segment\n")
            seg_errors = True
        if not seg_errors:
            error_messages.append("7seg: Normal\n")

        # Processor errors
        if self.errproc[0] == "Processor: Reset":
            error_messages.append("Processor:⚠️ Reset\n")
        else:
            error_messages.append("Processor: Normal\n")

        self.log_box5.delete("1.0", "end")
        self.log_box5.insert("end", "".join(error_messages))
        self.log_box5.configure(state="disable")
    

    def update_temp(self):
        """Update temperature display"""
        scroll_position = self.log_box1.yview()
        self.log_box1.configure(state="normal")
        table_data = []
        for i in range(0, 128, 2):
            table_data.append([
                f"Cell:{i:>3}", f"T:{self.temp[i]:05.2f}",f"Cell:{i+1:>3}", f"T:{self.temp[i+1]:05.2f}"
            ])
        formatted_text = tabulate(table_data, tablefmt="plain")
        self.log_box1.delete("1.0", "end")
        self.log_box1.insert("end", formatted_text + "\n")
        self.log_box1.yview_moveto(scroll_position[0])
        self.log_box1.configure(state="disable")
        self.log_box1.update()  # Force immediate update



    def update_bmsv(self):
        """Update BMS voltage display using tabulate with fixed formatting"""
        scroll_position = self.log_box2.yview()
        self.log_box2.configure(state="normal")
        self.log_box2.configure(font=("Courier New", 12))  # Monospace font
        
        table_data = []
        for i in range(0, 600, 2):
            table_data.append([
                f"Cell:{i:>3}",
                f"V:{self.bmsv[i]:6.2f}",
                f"Cell:{i+1:>3}",
                f"V:{self.bmsv[i+1]:6.2f}"
            ])
        
        # Use tabulate with empty string as colalign to prevent auto-formatting
        formatted_text = tabulate(table_data, tablefmt="plain",colalign=("left", "left", "left", "left"))
        
        self.log_box2.delete("1.0", "end")
        self.log_box2.insert("end", formatted_text + "\n")
        self.log_box2.yview_moveto(scroll_position[0])
        self.log_box2.configure(state="disable")
        self.log_box2.update()  # Force immediate GUI update

    def start(self):
        """Function to start the serial communication"""
        if self.ser and not self.ser.is_open:
            try:
                self.ser.open()
            except:
                self.log_box1.configure(state="normal")
                self.log_box2.configure(state="normal")
                self.log_box3.configure(state="normal")
                self.log_box4.configure(state="normal")
                self.log_box5.configure(state="normal")
                self.log_box1.insert("1.0", f"Serial error\n")
                self.log_box2.insert("1.0", f"Serial error\n")
                self.log_box3.insert("1.0", f"Serial error\n")
                self.log_box4.insert("1.0", f"Serial error\n")
                self.log_box5.insert("1.0", f"Serial error\n")
                self.log_box1.configure(state="disable")
                self.log_box2.configure(state="disable")
                self.log_box3.configure(state="disable")
                self.log_box4.configure(state="disable")
                self.log_box5.configure(state="disable")
                return
        self.is_running = True
        if self.ser:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
        self.text_button1.configure(state="disabled")

    def stop(self):
        """Function to stop the serial communication"""
        self.is_running = False
        self.text_button1.configure(state="normal")     

    def clear_logs(self):
        """Function to clear the logs"""

        self.log_box1.configure(state="normal")
        self.log_box2.configure(state="normal")
        self.log_box3.configure(state="normal")
        self.log_box4.configure(state="normal")
        self.log_box5.configure(state="normal")

        self.log_box1.delete("1.0", "end")
        self.log_box2.delete("1.0", "end")
        self.log_box3.delete("1.0", "end")
        self.log_box4.delete("1.0", "end")
        self.log_box5.delete("1.0", "end")

        self.log_box1.configure(state="disable")
        self.log_box2.configure(state="disable")
        self.log_box3.configure(state="disable")
        self.log_box4.configure(state="disable")
        self.log_box5.configure(state="disable")
        
        self.setup_variables()
    

    def crc_verify(self, mesaj):
        message = []
        divisor = 0x8D
        message.append(self.header)
        for i in range(0, len(mesaj)):
            message.append(mesaj[i])
        print(message)
        aux = message[0] 

        for i in range(1, len(mesaj)+1):
            aux = (aux << 8) | message[i]
            for j in range(15, 7, -1):
                if(aux & (1 << j)):
                    aux ^= divisor << (j-8)

        message_status = aux % 256
        print(message_status)
        return message_status

    def easter_egg(self):
        self.log_box1.configure(state="normal")
        self.log_box2.configure(state="normal")
        self.log_box3.configure(state="normal")
        self.log_box4.configure(state="normal")
        self.log_box5.configure(state="normal")

        smug_faces = [
            "( •̀ᴗ•́ )",  # Classic smug
            "( ಠ◡ಠ )",  # Know-it-all smirk
            "( ≖‿≖ )",  # Side-eye
            "( ͡° ͜ʖ ͡°)",  # Lenny face
            "( ¬‿¬ )",   # Suspicious
            "( •_• )>⌐■-■",  # Sunglasses cool
            "( ಠ⁠∀⁠ಠ )",  # Mischievous
            "( ᵔ◡ᵔ )",   # Cheeky
            "( ◕‿◕ )",   # Cute smug
            "( ˘ω˘ )",   # Sleepy smug
            "( ￣ω￣ )",  # Noble smug
            "( ´◔ ω◔`)",  # Innocent (fake)
            "( ￢‿￢ )",  # Scheming
            "( ￣ー￣ )",  # Unimpressed
            "( ︶︿︶ )",  # Judging you
            "( ˘⌣˘ )",   # Self-satisfied
            "( ˘³˘)♥",   # Blowing a kiss
            "( ง'̀-'́)ง",  # Ready to fight
            "( ͠° ͟ʖ ͡°)", # Extreme Lenny
            "( ﾉ◕ヮ◕)ﾉ",  # Waving paws
            "[^._.^]ﾉ",   # Kawaii style
            "(=｀ω´=)",   # Angry-cute
            "(⁀ᗢ⁀)",      # Rare smug
            "(◕ᴥ◕ʋ)",     # Doge-style smug
            "ヾ(●ω●)ノ"   # Excited smug
        ]
        random_face = random.choice(smug_faces)  
        self.log_box1.insert("1.0", rf"""
               /\_/\
             {random_face}
             /　　　 \ 
            (　　　　)
            """)
        self.log_box2.insert("1.0", rf"""
               /\_/\
             {random_face}
             /　　　 \ 
            (　　　　)
            """)
        self.log_box3.insert("1.0", rf"""
               /\_/\
             {random_face}
             /　　　 \ 
            (　　　　)
            """)
        self.log_box4.insert("1.0", rf"""
               /\_/\
             {random_face}
             /　　　 \ 
            (　　　　)
            """)
        self.log_box5.insert("1.0", rf"""
               /\_/\
             {random_face}
             /　　　 \ 
            (　　　　)
            """)
        self.log_box1.configure(state="disable")
        self.log_box2.configure(state="disable")
        self.log_box3.configure(state="disable")
        self.log_box4.configure(state="disable")
        self.log_box5.configure(state="disable")

    def on_close(self):
        """Function to close the serial communication"""
        self.stop_event.set()
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.destroy()