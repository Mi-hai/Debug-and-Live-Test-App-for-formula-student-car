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
        self.log_box1 = ctk.CTkTextbox(
            self,
            width=300, height=600,
            font=("Arial", 16), text_color="red",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box1.grid(row=1, column=0, padx=20, pady=30, sticky="nsew")

        self.log_box2 = ctk.CTkTextbox(
            self,
            width=300, height=600,
            font=("Arial", 16), text_color="blue",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box2.grid(row=1, column=1, padx=20, pady=30, sticky="nsew")

        self.log_box3 = ctk.CTkTextbox(
            self,
            width=300, height=600,
            font=("Arial", 16), text_color="green",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box3.grid(row=1, column=2, padx=20, pady=30, sticky="nsew")

        self.log_box4=ctk.CTkTextbox(
            self,
            width=300, height=600,
            font=("Arial", 16), text_color="green",
            fg_color="#242424", border_width=1, border_color="black",
            activate_scrollbars=True)
        self.log_box4.grid(row=1, column=3, padx=60, pady=30, sticky="nsew",rowspan=4)

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
    lowest_accel = 9999999
    lowest_frana = 9999999
    Error = 0

    # Function to update the text box
    def update_textbox(self):
        global header
        global bufferdata
        global lowest_temp
        global lowest_BMS_V
        global lowest_BMS_A
        global lowest_accel
        global lowest_frana
        global Error
        ok = 1
        if self.is_running:
            if self.ser.in_waiting:
                data = self.ser.read(self.ser.in_waiting)  # Read all available bytes
                self.bufferdata += data
                while ok:
                    if len(self.bufferdata) > 0:
                        if self.header == 0:
                            self.header = self.bufferdata.pop(0)

                        if self.header == 10:  # Senzor Temperatura
                            if len(self.bufferdata) >= 4:
                                # printare celor 4 seturi de date scoate a
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
                                
                                
                                self.log_box1.insert("1.0", f"Celula: {celula} are temperatura {valoare}" + "\n")
                                self.header = 0
                            else:
                                ok = 0

                        elif self.header == 11:
                            if len(self.bufferdata) >= 5:
                                # printare celor 5 seturi de date scoate b
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
                                self.log_box2.insert("1.0", f"Celula: {celula} are voltajul {valoare}" + "\n")
                                self.header = 0
                            else:
                                ok = 0
                        elif self.header == 12:
                            if len(self.bufferdata) >= 3:
                                mesaj = []
                                for i in range(3):
                                    mesaj.append(self.bufferdata.pop(0))
                                valoare = 0
                                valoare = float(mesaj[0] * 256 + mesaj[1]) / (10 ** mesaj[2])
                                if valoare<self.lowest_BMS_A:
                                    self.lowest_BMS_A=valoare
                                    self.update_text()
                                self.log_box3.insert("1.0", f"Amperajul din BMS: {valoare}" + "\n")
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
        global lowest_accel
        global lowest_frana
        global Error
        self.log_box4.delete("1.0", "end")
        self.log_box4.insert("1.0", f"Lowest Temp: {self.lowest_temp}" + "\n"+ f"Lowest BMS V: {self.lowest_BMS_V}" + "\n"+ f"Lowest BMS A: {self.lowest_BMS_A}" + "\n"+ f"Lowest Accel: {self.lowest_accel}" + "\n"+ f"Lowest Frana: {self.lowest_frana}" + "\n"+ f"Errors: {self.Error}" + "\n")
    


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

    def on_close(self):
        if self.ser.is_open:
            self.ser.close()
        self.destroy()