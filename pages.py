import sys
import sqlite3
sys.dont_write_bytecode = True

import customtkinter as ctk
import serial

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
            width=300, height=300,
            font=("Arial", 16), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box1.grid(row=0, column=0, padx=20, pady=30, sticky="new")

        self.log_box5 = ctk.CTkTextbox(
            self,
            width=300, height=300,
            font=("Arial", 16), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box5.grid(row=1, column=0, padx=20,pady=20, sticky="sew")
        #==========================================================================

        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
        self.log_box2 = ctk.CTkTextbox(
            self,
            width=300, height=300,
            font=("Arial", 16), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box2.grid(row=0, column=1, padx=20, pady=30, sticky="new")

        self.log_box6 = ctk.CTkTextbox(
            self,
            width=300, height=300,
            font=("Arial", 16), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box6.grid(row=1, column=2, padx=20,pady=20, sticky="sew")
        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        self.log_box3 = ctk.CTkTextbox(
            self,
            width=300, height=300,
            font=("Arial", 16), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box3.grid(row=0, column=2, padx=20, pady=30, sticky="new")

        self.log_box7 = ctk.CTkTextbox(
            self,
            width=300, height=300,
            font=("Arial", 16), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box7.grid(row=1, column=1, padx=20, pady=20, sticky="sew")
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # --------------------------------------------------------------------------------------
        self.log_box4=ctk.CTkTextbox(
            self,
            width=300, height=300,
            font=("Arial", 16), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box4.grid(row=0, column=3, padx=60, pady=30, sticky="new")
        self.log_box8=ctk.CTkTextbox(
            self,
            width=300, height=300,
            font=("Arial", 16), text_color="white",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box8.grid(row=1, column=3, padx=60, pady=20, sticky="sew")
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
    Error = 0
    timp=0

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
        global Error
        global timp
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
                                
                                if valoare<self.lowest_temp:
                                    self.lowest_temp=valoare
                                    self.update_text()
                                self.log_box1.insert("1.0", f"Cell: {celula} Temp: {self.lowest_temp}" + "\n")
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
                                if valoare<self.lowest_BMS_V:
                                    self.lowest_BMS_V=valoare
                                    self.update_text()
                                self.log_box2.insert("1.0", f"Cell: {celula} Voltage: {self.lowest_BMS_V}" + "\n")
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
                                self.log_box3.insert("1.0", f"BMS A: {self.lowest_BMS_A}" + "\n")
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
                                self.log_box5.insert("1.0", f"Pedal1: {self.accel1} - Pedal2: {self.accel2}" + "\n")
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
                                self.log_box6.insert("1.0", f"Brake: {self.frana}" + "\n")
                                self.header = 0
                            else:
                                ok = 0
                        #Modul timp
                        elif self.header == 17:
                            if len(self.bufferdata) >= 4:
                                mesaj = []
                                for i in range(4):
                                    mesaj.append(self.bufferdata.pop(0))
                                modul=0
                                valoare = 0
                                modul=mesaj[0]
                                valoare = float(mesaj[1] * 256 + mesaj[2]) / (10 ** mesaj[3])
                                self.timp=valoare
                                self.update_text()
                                self.bufferdata = []
                                self.log_box7.insert("1.0", f"Time: {self.timp}" + "\n")
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
                                        self.log_box8.insert("1.0", "Temperature too HIGH 🌡️" + "\n")
                                        self.header = 0
                                if modul==11 or modul ==12:
                                    if valoare == 0:
                                        self.bufferdata = []
                                        self.log_box8.insert("1.0", "BMS not responding" + "\n")
                                        self.header = 0
                                    elif valoare == 1:
                                        self.bufferdata = []
                                        self.log_box8.insert("1.0", "BMS low voltage" + "\n")
                                        self.header = 0
                                    elif valoare == 2:
                                        self.bufferdata = []
                                        self.log_box8.insert("1.0", "BMS high consumption" + "\n")
                                        self.header = 0
                                if modul==13 or modul==14:
                                    if valoare == 0:
                                        self.bufferdata = []
                                        self.log_box8.insert("1.0", "Pedals different outputs" + "\n")
                                        self.header = 0
                                    elif valoare == 1:
                                        self.bufferdata = []
                                        self.log_box8.insert("1.0", "Pedals shorted ⚡" + "\n")
                                        self.header = 0
                                    elif valoare == 2:
                                        self.bufferdata = []
                                        self.log_box8.insert("1.0", f"Pedals no output 💀" + "\n")
                                        self.header = 0
                                if modul==15:
                                    if valoare == 0:
                                        self.bufferdata = []
                                        self.log_box8.insert("1.0", "7Seg bus is broken 💔" + "\n")
                                        self.header = 0
                                    elif valoare == 1:
                                        self.bufferdata = []
                                        self.log_box8.insert("1.0", "7Seg number is too large" + "\n")
                                        self.header = 0
                                    elif valoare == 2:
                                        self.bufferdata = []
                                        self.log_box8.insert("1.0", "7Seg wrong segment" + "\n")
                                        self.header = 0
                                if modul==16:
                                    if valoare==0:
                                        self.bufferdata = []
                                        self.log_box8.insert("1.0", "Processor reset 🧠" + "\n")
                                        self.header = 0
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
        global Error
        global timp
        self.log_box4.delete("1.0", "end")
        self.log_box4.insert("1.0", f"Lowest Temp: {self.lowest_temp}" + "\n"+ f"Lowest BMS V: {self.lowest_BMS_V}" + "\n"+ f"Lowest BMS A: {self.lowest_BMS_A}" + "\n"+ f"Accel(%): P1: {self.accel1} - P2: {self.accel2}" + "\n"+ f"Brake(%): {self.frana}" + "\n"+ f"Time: {self.timp}" + "\n")
    


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
        self.log_box6.delete("1.0", "end")
        self.log_box7.delete("1.0", "end")
        self.log_box8.delete("1.0", "end")

    def on_close(self):
        if self.ser.is_open:
            self.ser.close()
        self.destroy()