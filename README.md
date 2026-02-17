# Fencing Wire Control Unit

A Python application for monitoring and controlling fencing wire circuits via Arduino. This system reads sensor data from three independent fencing lines (A, B, C), detects short circuits, calculates resistance values, and stores all data in a SQLite database.

## Project Overview

The Fencing Wire Control Unit communicates with an Arduino microcontroller to continuously monitor the status and integrity of three fencing wire lines. The system captures digital and analog sensor readings, processes the data, and persists it to a database for logging and analysis.

### Key Features

- **Three Independent Line Monitoring**: Simultaneously monitors fencing lines A, B, and C
- **Real-time Sensor Data**: Captures digital outputs and raw analog values
- **Short Circuit Detection**: Identifies and logs short circuit events with "sparkling" effect simulation
- **Resistance Calculation**: Computes wire resistance based on voltage divider calculations
- **SQLite Database Storage**: Automatically stores all data for historical analysis
- **Mock Serial Interface**: Includes testing capabilities without requiring actual hardware
- **Easy Port Selection**: Auto-detects available COM ports with manual override option

## File Structure

```
├── main.py                    # Main application entry point
├── main_v4.cpp                # Arduino sketch firmware
├── mock_serial.py             # Mock serial interface for testing
├── example-code-output.txt    # Sample output from the system
├── serial_output.db           # SQLite database (created at runtime)
└── README.md                  # This file
```

## Installation

### Requirements

- Python 3.6+
- `pyserial` library
- Arduino with compatible firmware (`main_v4.cpp`)

### Setup

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install pyserial
   ```
3. Upload `main_v4.cpp` to your Arduino using the Arduino IDE

## Usage

### Running the Application

Basic usage:

```bash
python main.py
```

### Configuration

Edit the top of `main.py` to configure:

```python
USE_MOCK = True      # Set to False to use real Arduino
DB_NAME = "serial_output.db"  # Database filename
```

### Workflow

1. **Start the application** - The program initializes the database and prompts you
2. **Clear database (optional)** - Choose whether to clear previous data
3. **Connect Arduino or use mock** - If not using mock serial:
   - Application scans for available COM ports
   - You can auto-select if only one port is found
   - Manual selection available if multiple ports detected
4. **Monitor data** - Real-time serial data is displayed in the console
5. **Data storage** - All data is automatically inserted into the SQLite database

## Data Format

### Serial Protocol

The Arduino sends data in the following format:

```
data:loopcount;active_line;digi_A;digi_B;digi_C;raw_A;raw_B;raw_C;vout;resistance;short_circuit
```

### Database Schema

The `data` table contains:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key auto-increment |
| loopcount | INTEGER | Arduino loop counter |
| active_line | VARCHAR(1) | Active line (A, B, or C) |
| digi_A | INTEGER | Digital output line A |
| digi_B | INTEGER | Digital output line B |
| digi_C | INTEGER | Digital output line C |
| raw_A | INTEGER | Raw ADC value line A (0-1023) |
| raw_B | INTEGER | Raw ADC value line B (0-1023) |
| raw_C | INTEGER | Raw ADC value line C (0-1023) |
| vout | REAL | Output voltage |
| resistance | REAL | Calculated resistance (Ω) |
| short_circuit | INTEGER | Short circuit indicator (0=normal, 1+=fault) |

## Testing

### Using Mock Serial

With `USE_MOCK = True`, the application simulates Arduino output without requiring hardware:

- Generates realistic sensor data with random variations
- Simulates short circuit "sparkling" effects (3% probability)
- Alternates between lines A, B, and C
- Provides a full testing environment

The mock serial output from [example-code-output.txt](example-code-output.txt) shows sample data format.

## Features

### Short Circuit Detection

The system detects and logs short circuit events. Mock mode simulates intermittent short circuits with:
- Sparkling effect: Rapid oscillations between normal and fault states
- 3% probability per cycle of triggering a short
- Duration: 5-12 cycles per detection

### Resistance Calculation

Resistance is calculated using the voltage divider formula:

$$R = R_1 \cdot \left(\frac{V_{in}}{V_{out}} - 1\right)$$

Where:
- $R_1$ = Series resistor (typically 22Ω)
- $V_{in}$ = Supply voltage
- $V_{out}$ = Measured output voltage

### Database Management

- **Clear Data**: Option to delete all records on startup
- **Persistence**: All data persists between sessions
- **Auto-increment**: Records automatically numbered with unique IDs
- **Append-only**: New data is always added, never overwrites

## Troubleshooting

### "No ports found" error
- Ensure Arduino is connected via USB
- Check device manager for COM port assignment
- Try different USB ports
- Verify USB drivers are installed

### Invalid data format errors
- Ensure Arduino firmware matches `main_v4.cpp`
- Check baud rate (57600)
- Verify serial connection is stable

### Database locked errors
- Close other applications accessing the database
- Ensure write permissions on current directory

## Development

### Arduino Communication

The application expects 57600 baud, 8 data bits, 1 stop bit, no parity.

### Extending the Project

To modify the monitored data:
1. Update `main_v4.cpp` to change Arduino output format
2. Modify the data parsing in `main.py` `process_to_db()` function
3. Update the database schema in `init_db()`

## License

[Add your license information here]

## Author (partial)

SciTechMC