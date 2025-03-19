import sys
import sqlite3
sys.dont_write_bytecode = True

import customtkinter as ctk
import serial
import numpy as np
import os
from tabulate import tabulate
import threading

#  Debug Page
class Debug(ctk.CTkFrame):
    def __init__(self, parent, input, default_input, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.grid(sticky="nsew",rowspan=5)


        # Multi-line Text Box
        #==========================================================================
        self.log_box1 = ctk.CTkTextbox(
            self,
            width=300, height=600,
            font=("Arial", 14), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box1.grid(row=0, column=0, padx=20, pady=30, sticky="nsew",rowspan=2)
        #==========================================================================

        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        self.log_box2 = ctk.CTkTextbox(
            self,
            width=300, height=600,
            font=("Arial", 14), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box2.grid(row=0, column=1, padx=20, pady=30, sticky="nsew",rowspan=2)

        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.log_box3 = ctk.CTkTextbox(
            self,
            width=300, height=600,
            font=("Arial", 16), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box3.grid(row=0, column=2, padx=20, pady=30, sticky="nsew",rowspan=2)


        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # --------------------------------------------------------------------------------------
        self.log_box4=ctk.CTkTextbox(
            self,
            width=350, height=300,
            font=("Arial", 16), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box4.grid(row=0, column=3, padx=60, pady=30, sticky="new")

        self.log_box5=ctk.CTkTextbox(
            self,
            width=350, height=300,
            font=("Arial", 16), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box5.grid(row=1, column=3, padx=60, pady=20, sticky="nsew")
        # --------------------------------------------------------------------------------------


        # Serial Setup
        if len(input) < 2:
            self.ser = serial.Serial(port=default_input, baudrate=9600, timeout=1)
        else:
            self.ser = serial.Serial(port=input, baudrate=9600, timeout=1)

        # Sets the first state of the port as off and setups the buttons
        self.is_running = False
        self.setup_buttons()
           
    # Variables
    header = 0
    bufferdata = []
    lowest_temp = 9999999
    lowest_BMS_V = 9999999
    lowest_BMS_A = 9999999
    accel1 = 9999999
    accel2 = 9999999
    frana = 9999999
    timp=0
    errtemp=["","","","","","","",""]
    errbms=["","","","","","","",""]
    errpedals=["","","","","","","",""]
    errpedalsf=["","","","","","","",""]
    err7seg=["","","","","","","",""]
    errproc=["","","","","","","",""]
    temp=np.zeros(128)
    bmsv=np.zeros(600)



    # Function to setup the buttons
    def setup_buttons(self):
        # Start Button
        self.text_button1 = ctk.CTkButton(self, text="Start", command=self.start, border_width=3, border_color="black",height=50)
        self.text_button1.grid(row=2, column=0, pady=10, ipadx=10, sticky="ew")

        # Stop Button
        self.text_button2 = ctk.CTkButton(self, text="Stop", command=self.stop, border_width=3, border_color="black",height=50)
        self.text_button2.grid(row=2, column=1, pady=10, ipadx=10, sticky="ew")

        # Clear log Button
        self.text_button4 = ctk.CTkButton(self, text="Clear log", command=self.clear_logs, border_width=3, border_color="black",height=50)
        self.text_button4.grid(row=2, column=2, pady=10, ipadx=10, sticky="ew")

    # Function to update the text box
    def update_textbox(self):
        global header
        global bufferdata
        global lowest_temp
        global lowest_BMS_V
        global lowest_BMS_A
        global accel1
        global accel2
        global frana
        global timp
        global errtemp
        global errbms
        global errpedals
        global err7seg
        global errproc
        global temp
        global bmsv
        global errpedalsf
        ok = 1

        if self.is_running:
            if self.ser.in_waiting:
                data = self.ser.read(self.ser.in_waiting)  # Read all available bytes
                self.bufferdata += data
                while ok:
                    if len(self.bufferdata) > 0:
                        if self.header == 0:
                            self.header = self.bufferdata.pop(0)
                        #Modul Temp
                        if self.header == 10:
                            if len(self.bufferdata) >= 4:
                                mesaj = []
                                
                                for i in range(4):
                                    mesaj.append(self.bufferdata.pop(0))
                                celula = 0
                                valoare = 0
                                celula = mesaj[0]
                                valoare = float(mesaj[1] * 256 + mesaj[2]) / (10 ** mesaj[3])
                                self.temp[celula]=valoare
                                if valoare<self.lowest_temp:
                                    self.lowest_temp=valoare
                                    self.update_text()
                                self.update_temp()
                                self.header = 0
                            else:
                                ok = 0
                        #Modul BMS_V
                        elif self.header == 11:
                            if len(self.bufferdata) >= 5:
                                mesaj = []
                                for i in range(5):
                                    mesaj.append(self.bufferdata.pop(0))
                                celula = 0
                                valoare = 0
                                celula = mesaj[0] * 256 + mesaj[1]
                                valoare = float(mesaj[2] * 256 + mesaj[3]) / (10 ** mesaj[4])
                                self.bmsv[celula]=valoare
                                if valoare<self.lowest_BMS_V:
                                    self.lowest_BMS_V=valoare
                                    self.update_text()
                                self.update_bmsv()
                                self.header = 0
                            else:
                                ok = 0
                        #Modul BMS_A
                        elif self.header == 12:
                            if len(self.bufferdata) >= 3:
                                mesaj = []
                                for i in range(3):
                                    mesaj.append(self.bufferdata.pop(0))
                                valoare = 0
                                valoare = float(mesaj[0] * 256 + mesaj[1]) / (10 ** mesaj[2])
                                if valoare!=self.lowest_BMS_A:
                                    self.lowest_BMS_A=valoare
                                    self.update_text()
                                    self.bufferdata = []
                                self.header = 0
                            else:
                                ok = 0
                        #Modul Accel
                        elif self.header == 13:
                            if len(self.bufferdata) >= 5:
                                mesaj = []
                                for i in range(5):
                                    mesaj.append(self.bufferdata.pop(0))
                                valoare = 0
                                valoare1=0
                                valoare = float(mesaj[0] * 256 + mesaj[1]) / (10 ** mesaj[4])
                                valoare1 = float(mesaj[2] * 256 + mesaj[3]) / (10 ** mesaj[4])
                                self.accel1=valoare
                                self.accel2=valoare1
                                self.update_text()
                                self.bufferdata = []
                                self.header = 0
                            else:
                                ok = 0
                        #Modul Frana
                        elif self.header == 14:
                            if len(self.bufferdata) >= 3:
                                mesaj = []
                                for i in range(3):
                                    mesaj.append(self.bufferdata.pop(0))
                                valoare = 0
                                valoare = float(mesaj[0] * 256 + mesaj[1]) / (10 ** mesaj[2])
                                self.frana=valoare
                                self.update_text()
                                self.bufferdata = []
                                self.header = 0
                            else:
                                ok = 0
                        #Modul timp
                        elif self.header == 17:
                            if len(self.bufferdata) >= 6:
                                mesaj = []
                                for i in range(6):
                                    mesaj.append(self.bufferdata.pop(0))
                                modul=0
                                valoare = 0
                                modul=mesaj[0]
                                valoare = float(mesaj[1] * 256**3 + mesaj[2] * 256**2 + mesaj[3] * 256 + mesaj[4])/(10**mesaj[5])
                                self.timp=valoare
                                self.update_text()
                                self.bufferdata = []
                                self.log_box3.insert("1.0", f"Time: {self.timp}" + "\n")
                                self.header = 0
                            else:
                                ok = 0
                        #Modul Error
                        elif self.header == 9:
                            if len(self.bufferdata) >= 2:
                                mesaj = []
                                for i in range(2):
                                    mesaj.append(self.bufferdata.pop(0))
                                modul=0
                                valoare = 0
                                modul=mesaj[0]
                                valoare = bin(mesaj[1])[2:].zfill(8)
                                valoare1=int(bin(mesaj[1])[2:].zfill(8))
                                if modul==10:
                                    for i in range(len(valoare)):
                                        if valoare1%10 ==1:
                                            if i==0:
                                                self.errtemp[i]="Temperature: too HIGH" 
                                            valoare1=valoare1//10                      
                                if modul==11 or modul==12:
                                    for i in range(len(valoare)):
                                        if valoare1%10 ==1:
                                            if i==0:
                                                self.errbms[i]="BMS: No Response"
                                            if i==1:
                                                self.errbms[i]="BMS: Low Voltage"
                                            if i==2:
                                                self.errbms[i]="BMS: High Consumption"
                                            valoare1=valoare1//10
                                if modul==13:
                                    for i in range(len(valoare)):
                                        if valoare1%10==1:
                                            if i==0:
                                                self.errpedals[i]="Pedals: Different OutPut"
                                            if i==1:
                                                self.errpedals[i]="Pedals: Shorted"
                                            if i==2:
                                                self.errpedals[i]="Pedals: No OutPut"
                                            valoare1=valoare1//10
                                if modul==14:
                                    for i in range(len(valoare)):
                                        if valoare1%10==1:
                                            if i==0:
                                                self.errpedalsf[i]="Break: Shorted"
                                            if i==1:
                                                self.errpedalsf[i]="Break: No OutPut"
                                            valoare1=valoare1//10
                                if modul==15:
                                    for i in range(len(valoare)):
                                        if valoare1%10==1:
                                            if i==0:
                                                self.err7seg[i]="7seg: Bus is Broken"
                                            if i==1:
                                                self.err7seg[i]="7seg: Number too large"
                                            if i==2:
                                                self.err7seg[i]="7seg: Wrong Segment"
                                            valoare1=valoare1//10
                                if modul==16:
                                    for i in range(len(valoare)):
                                        if valoare1%10==1:
                                            if i==0:
                                                self.errproc[i]="Processor: Reset"
                                            valoare1=valoare1//10
                                self.update_error()
                                self.bufferdata = []
                                self.header = 0
                            else:
                                ok = 0
                        else:
                            ok = 0
                            self.bufferdata = []
                            self.header = 0
                    else:
                        ok = 0
                        self.bufferdata = []
                        self.header = 0

        # Schedule the next update
        self.after(1, self.update_textbox)

    #Function to update the logs textbox
    def update_text(self):
        global lowest_temp
        global lowest_BMS_V
        global lowest_BMS_A
        global accel1
        global accel2
        global frana
        global timp
        self.log_box4.delete("1.0", "end")
        self.log_box4.insert("end", f"Lowest Temp: {self.lowest_temp}" + "\n"+ "\n"+ f"Lowest BMS V: {self.lowest_BMS_V}" + "\n"+ "\n"+ f"Lowest BMS A: {self.lowest_BMS_A}" + "\n"+ "\n"+ f"Accel(%): P1: {self.accel1} - P2: {self.accel2}" + "\n"+ "\n"+ f"Brake(%): {self.frana}" + "\n"+ "\n"+ f"Time: {self.timp}" + "\n")
        
        
    #Function to update the error textbox
    def update_error(self):
        global errtemp
        global errbms
        global errpedals
        global err7seg
        global errproc
        global errpedalsf
        ok1=0
        ok2=0
        ok3=0
        ok4=0
        # Clear the previous error messages
        self.log_box5.delete("1.0", "end")  # Clear the content of the text box (log)

        # Initialize the error messages list to keep track of what to display
        error_messages = []

        # Check and display the errors based on the current state of the error variables

        # Temperature Error (check all bits)
        if self.errtemp[0] == "Temperature: too HIGH":
            error_messages.append("Temperature: too HIGH\n")
        else:
            error_messages.append("Temperature: Normal\n")

        # BMS Errors (check all bits)
        if self.errbms[0] == "BMS: No Response":
            error_messages.append("BMS: No Response\n")
            ok1=1
        if self.errbms[1] == "BMS: Low Voltage":
            error_messages.append("BMS: Low Voltage\n")
            ok1=1
        if self.errbms[2] == "BMS: High Consumption":
            error_messages.append("BMS: High Consumption\n")
            ok1=1
        
        if ok1==0:  # If none is active
            error_messages.append("BMS: Normal\n")

        # Pedals Errors (check all bits)
        if self.errpedals[0] == "Pedals: Different Output":
            error_messages.append("Pedals: Different Output\n")
            ok2=1
        if self.errpedals[1] == "Pedals: Shorted":
            error_messages.append("Pedals: Shorted\n")
            ok2=1
        if self.errpedals[2] == "Pedals: No Output":
            error_messages.append("Pedals: No Output\n")
            ok2=1
        if ok2==0:  # If none is active
            error_messages.append("Pedals: Normal\n")

        # Brake Pedals Errors (check all bits)
        if self.errpedalsf[0] == "Break: Shorted":
            error_messages.append("Break: Shorted\n")
            ok3=1
        if self.errpedalsf[1] == "Break: No Output":
            error_messages.append("Break: No Output\n")
            ok3=1
        if ok3==0:  # If none is active
            error_messages.append("Break: Normal\n")

        # 7Seg Display Errors (check all bits)
        if self.err7seg[0] == "7seg: Bus is Broken":
            error_messages.append("7seg: Bus is Broken\n")
            ok4=1
        if self.err7seg[1] == "7seg: Number too large":
            error_messages.append("7seg: Number too large\n")
            ok4=1
        if self.err7seg[2] == "7seg: Wrong Segment":
            error_messages.append("7seg: Wrong Segment\n")
            ok4=1
        if ok4==0:  # If none is active
            error_messages.append("7seg: Normal\n")

        # Processor Error
        if self.errproc[0] == "Processor: Reset":
            error_messages.append("Processor: Reset\n")
        else:
            error_messages.append("Processor: Normal\n")

        # Insert all errors into the log
        self.log_box5.insert("end", "".join(error_messages))
        




    #Function to update temp textbox
    def update_temp(self):
        global temp
        scroll_position = self.log_box1.yview()

        table_data = []
        for i in range(0, 128, 2):
            table_data.append([f"Cell:{i:>3}", f"T:{self.temp[i]:05.2f}", f"Cell:{i+1:>3}", f"T:{self.temp[i+1]:05.2f}"])

        formatted_text = tabulate(table_data, tablefmt="plain")
        self.log_box1.delete("1.0", "end")
        self.log_box1.insert("end", formatted_text + "\n")
        self.log_box1.yview_moveto(scroll_position[0])

    #Function to update bmsv textbox
    def update_bmsv(self):
        global bmsv
        scroll_position = self.log_box2.yview()

        table_data = []
        for i in range(0, 600, 2):
            table_data.append([f"Cell:{i:>3}", f"V:{self.bmsv[i]:6.2f}",f"Cell:{i+1:>3}", f"V:{self.bmsv[i+1]:6.2f}"])

        formatted_text = tabulate(table_data, tablefmt="plain")
        self.log_box2.delete("1.0", "end")
        self.log_box2.insert("end", formatted_text + "\n")
        self.log_box2.yview_moveto(scroll_position[0])

    # Function to start the serial communication
    def start(self):
        self.is_running = True
        self.ser.reset_input_buffer()  # Clears the input buffer
        self.ser.reset_output_buffer()  # Clears the output buffer
        self.update_textbox()
        self.text_button1.configure(state="disabled")

    # Function to stop the serial communication
    def stop(self):
        self.is_running = False
        # self.text_button3.configure(state="normal")
        self.text_button1.configure(state="normal")

    # Function to clear all logs
    def clear_logs(self):
        self.log_box1.delete("1.0", "end")
        self.log_box2.delete("1.0", "end")
        self.log_box3.delete("1.0", "end")
        self.log_box4.delete("1.0", "end")
        self.log_box5.delete("1.0", "end")
        global header
        global bufferdata
        global lowest_temp
        global lowest_BMS_V
        global lowest_BMS_A
        global accel1
        global accel2
        global frana
        global timp
        self.bufferdata = []
        self.lowest_temp = 9999999
        self.lowest_BMS_V = 9999999
        self.lowest_BMS_A = 9999999
        self.accel1 = 9999999
        self.accel2 = 9999999
        self.frana = 9999999
        self.timp=0



    # Function to close
    def on_close(self):
        if self.ser.is_open:
            self.ser.close()
        self.destroy()