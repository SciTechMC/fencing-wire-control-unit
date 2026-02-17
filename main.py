import serial
import sqlite3
import serial.tools.list_ports
import time

# SET THIS TO FALSE TO USE REAL ARDUINO
USE_MOCK = True 
DB_NAME = "serial_output.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loopcount INTEGER,
                active_line VARCHAR(1),
                digi_A INTEGER, digi_B INTEGER, digi_C INTEGER,
                raw_A INTEGER, raw_B INTEGER, raw_C INTEGER,
                vout REAL, resistance REAL, short_circuit INTEGER
            )
        ''')

def clear_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM data")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='data'")
            conn.commit()
            print("--- DATABASE CLEARED ---")
    except Exception as e:
        print(f"Error clearing database: {e}")

def process_to_db(cursor, line):
    if not line.startswith("data:"):
        print(f"[Arduino Info]: {line}")
        return

    try:
        payload = line.split(":", 1)[1]
        data_points = payload.split(";")
        if len(data_points) == 11:
            cursor.execute("""
                INSERT INTO data(loopcount, active_line, digi_A, digi_B, digi_C, 
                                 raw_A, raw_B, raw_C, vout, resistance, short_circuit)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """, data_points)
    except Exception as e:
        print(f"Error: {e}")

def wait_for_port():
    """Pings the system until a COM port is found."""
    while True:
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            # \r and end="" keep the message on one line so it doesn't spam the console
            print("\rScanning for Arduino... (Plug it in or press Ctrl+C)", end="", flush=True)
            time.sleep(1)
            continue
        
        print("\n\nPorts found:")
        for i, p in enumerate(ports):
            print(f"{i}: {p.device} [{p.description}]")
        
        if len(ports) == 1:
            print(f"Only one port found. Auto-selecting {ports[0].device}...")
            return ports[0].device
            
        try:
            idx = input("\nSelect Port Index (or press Enter to rescan): ")
            if idx == "": continue
            return ports[int(idx)].device
        except (ValueError, IndexError):
            print("Invalid selection. Rescanning...")

if __name__ == "__main__":
    init_db()
    
    choice = input("Clear existing database data? (y/n): ").lower().strip()
    if choice == 'y':
        clear_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        if USE_MOCK:
            from mock_serial import MockSerial
            ser = MockSerial()
            print("--- RUNNING MOCK SERIAL ---")
        else:
            port_name = wait_for_port()
            ser = serial.Serial(port_name, 57600, timeout=1)
            print(f"--- CONNECTED TO {port_name} ---")

        while True:
            raw = ser.readline()
            chunk = raw.decode('utf-8', errors='replace').strip()
            
            if chunk:
                for line in chunk.split('\n'):
                    process_to_db(cursor, line.strip())
                
                conn.commit()
                
    except KeyboardInterrupt:
        print("\nStopping program...")
    except serial.SerialException as e:
        print(f"\nSerial error (Hardware unplugged?): {e}")
    finally:
        if 'conn' in locals():
            conn.close()