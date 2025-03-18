import sys
import sqlite3
sys.dont_write_bytecode = True

import customtkinter as ctk
import serial
import numpy as np
import os

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
    errtemp=9
    errbms=9
    errpedals=9
    err7seg=9
    errproc=9
    temp=np.zeros(128)
    bmsv=np.zeros(600)

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
                                if mesaj[1]<=2:
                                    valoare = mesaj[1]
                                if modul==10:
                                    if valoare == 0:
                                        self.bufferdata = []
                                        self.errtemp=0
                                        self.header = 0
                                if modul==11 or modul ==12:
                                    if valoare == 0:
                                        self.bufferdata = []
                                        self.errbms=0
                                        self.header = 0
                                    elif valoare == 1:
                                        self.bufferdata = []
                                        self.errbms=1
                                        self.header = 0
                                    elif valoare == 2:
                                        self.bufferdata = []
                                        self.errbms=2
                                        self.header = 0
                                if modul==13 or modul==14:
                                    if valoare == 0:
                                        self.bufferdata = []
                                        self.errpedals=0
                                        self.header = 0
                                    elif valoare == 1:
                                        self.bufferdata = []
                                        self.errpedals=1
                                        self.header = 0
                                    elif valoare == 2:
                                        self.bufferdata = []
                                        self.errpedals=2
                                        self.header = 0
                                if modul==15:
                                    if valoare == 0:
                                        self.bufferdata = []
                                        self.err7seg=0
                                        self.header = 0
                                    elif valoare == 1:
                                        self.bufferdata = []
                                        self.err7seg=1
                                        self.header = 0
                                    elif valoare == 2:
                                        self.bufferdata = []
                                        self.err7seg=2
                                        self.header = 0
                                if modul==16:
                                    if valoare==0:
                                        self.bufferdata = []
                                        self.errproc=0
                                        self.header = 0
                                self.update_error()
                                self.header = 0
                                self.bufferdata = []
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
        self.log_box5.delete("1.0", "end")
        if self.errtemp == 0:
            self.log_box5.insert("end", "Temperature: too HIGH" + "\n"+"\n")
        else:
            self.log_box5.insert("end", "Temperature: Normal" + "\n"+ "\n")


        if self.errbms != 9:
            if self.errbms == 0:
                self.log_box5.insert("end", "BMS: not responding" + "\n"+ "\n")

            if self.errbms == 1:
                self.log_box5.insert("end", "BMS: low voltage" + "\n"+ "\n")

            if self.errbms == 2:
                self.log_box5.insert("end", "BMS: high consumption" + "\n"+ "\n")
        else:
            self.log_box5.insert("end", "BMS: Normal" + "\n"+ "\n")

        if self.errpedals == 0:
            self.log_box5.insert("end", "Pedals: different outputs" + "\n"+ "\n")


        if self.errpedals != 9:
            if self.errpedals == 1:
                self.log_box5.insert("end", "Pedals: shorted" + "\n"+ "\n")

            if self.errpedals == 2:
                self.log_box5.insert("end", "Pedals: no output" + "\n"+ "\n")
        else:
            self.log_box5.insert("end", "Pedals: Normal" + "\n"+ "\n")


        if self.err7seg != 9:
            if self.err7seg == 0:
                self.log_box5.insert("end", "7Seg: bus is broken" + "\n"+ "\n")

            if self.err7seg == 1:
                self.log_box5.insert("end", "7Seg: number is too large" + "\n"+ "\n")

            if self.err7seg == 2:
                self.log_box5.insert("end", "7Seg: wrong segment" + "\n"+ "\n")
        else:
            self.log_box5.insert("end", "7Seg: Normal" + "\n"+ "\n")

        if self.errproc == 0:
            self.log_box5.insert("end", "Processor: reset" + "\n"+ "\n")
        else:
            self.log_box5.insert("end", "Processor: Normal" + "\n"+ "\n")

    #Function to update temp textbox
    def update_temp(self):
        global temp
        scroll_position=self.log_box1.yview()
        self.log_box1.delete("1.0", "end")
        for i in range(0, 128,2):
            self.log_box1.insert("end", f"Cell:{i} T:{self.temp[i]}              Cell:{i+1} T:{self.temp[i+1]}" + "\n")
        self.log_box1.yview_moveto(scroll_position[0])

    def update_bmsv(self):
        global bmsv
        scroll_position=self.log_box2.yview()
        self.log_box2.delete("1.0", "end")
        for i in range (0, 600,2):
            self.log_box2.insert("end", f"Cell:{i} V:{self.bmsv[i]}              Cell:{i+1} V:{self.bmsv[i+1]}" + "\n")
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
        global errtemp
        global errbms
        global errpedals
        global err7seg
        global errproc
        self.bufferdata = []
        self.lowest_temp = 9999999
        self.lowest_BMS_V = 9999999
        self.lowest_BMS_A = 9999999
        self.accel1 = 9999999
        self.accel2 = 9999999
        self.frana = 9999999
        self.timp=0
        self.errtemp=9
        self.errbms=9
        self.errpedals=9
        self.err7seg=9
        self.errproc=9

    def on_close(self):
        if self.ser.is_open:
            self.ser.close()
        self.destroy()