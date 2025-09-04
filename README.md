# Formula Student Car - Debug and Live Test App

This application is a real-time data visualizer and debugging tool for a Formula Student electric vehicle. It receives telemetry data via a serial connection and displays it in a user-friendly graphical interface built with CustomTkinter.

## Features

- **Main Page**:
  - Displays the team logo as a dynamic background.
  - Automatically detects the serial port connected to the car.
  - A "Refresh Port" button to re-scan for the correct serial port.
  - A "Debug Page" button to navigate to the main data visualization screen.

- **Debug Page**:
  - **Real-time Data Display**: Visualizes live data from the car's systems in separate panels:
    - **Temperature**: Shows readings from all 128 temperature sensors.
    - **BMS Voltage**: Displays voltage levels for all 600 BMS cells.
    - **Time**: Shows the elapsed time from the car's internal clock.
    - **Data Summary**: A quick overview of critical values like lowest temperature, lowest BMS voltage/current, and pedal positions.
    - **Errors**: A dedicated panel to report any system errors for quick diagnosis.
  - **Serial Communication Control**:
    - **Start/Stop**: Buttons to start and stop the flow of data from the serial port.
    - **Clear Logs**: A button to clear all display panels and reset the collected data.
  - **Multithreaded**: Uses a separate thread for serial data reading to ensure the GUI remains responsive.

## How It Works

The application is structured into two main files:

1.  **`main.py`**: This is the entry point of the application. It initializes the main window using `customtkinter`, sets up the initial screen with port detection, and handles the loading of the debug page. See [`main.py`](main.py).

2.  **`pages.py`**: This file contains the `Debug` class, which is the core of the application. It handles:
    - Creating the layout with all the data display textboxes.
    - Establishing and managing the serial connection (`pyserial`).
    - Reading and parsing a custom binary protocol from the car in a background thread.
    - Updating the GUI with the parsed data in real-time. See [`pages.py`](pages.py).

## Prerequisites

To run this application, you will need Python and the following libraries:

- `customtkinter`
- `pyserial`
- `Pillow`
- `numpy`
- `tabulate`

You can install them using pip:

```sh
pip install customtkinter pyserial Pillow numpy tabulate
```

## How to Run

1. **Clone the repository**
   ```sh
   git clone https://github.com/Mi-hai/Debug-and-Live-Test-App-for-formula-student-car.git
   cd Debug-and-Live-Test-App-for-formula-student-car
   ```
2. **Connect the car's data logger** via a serial-to-USB adapter.
3. **Install dependencies** (if not already done):
   ```sh
   pip install customtkinter pyserial Pillow numpy tabulate
   ```
4. **Run the application**:
   ```sh
   python main.py
   ```
5. The application will attempt to auto-detect the port. If it's incorrect, use the "Refresh Port" button.
6. Click "Debug Page" to open the data visualization screen.
7. Click "Start" to begin receiving and displaying data.

## File Structure

```
Debug-and-Live-Test-App-for-formula-student-car/
├── assets/
│   └── logo.jpeg
├── main.py
├── pages.py
├── README.md
└── LICENSE
```

- `main.py`: Entry point, handles main window, port detection, and navigation.
- `pages.py`: Contains the `Debug` class and all data visualization logic.
- `assets/`: Contains static assets (e.g., team logo).

## Custom Binary Protocol

The application expects telemetry data in a custom binary format sent from the car. The protocol is parsed in a background thread to ensure the GUI remains responsive. If you need to adapt the protocol, see the parsing logic in `pages.py`.

## Troubleshooting

- **No serial ports detected?**
  - Ensure the car is powered on and the USB adapter is connected.
  - Try the "Refresh Port" button.
  - Check your system's device manager for recognized COM ports.
- **GUI not displaying correctly?**
  - Make sure all dependencies are installed.
  - For Windows, ensure you are using a compatible Python version (Python 3.8+ recommended).
- **Data not updating?**
  - Confirm the car is sending data.
  - Check for errors in the terminal window.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
