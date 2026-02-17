import serial
import serial.tools.list_ports
import sqlite3

DB_NAME = "serial_output.db"

def select_com_port():
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("Error: No COM ports detected.")
        return None

    # If only one port is found, use it automatically
    if len(ports) == 1:
        port_name = ports[0].device
        print(f"Single port detected: {port_name}")
        return port_name

    # If multiple ports are found, let the user choose
    print("Multiple COM ports detected:")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} [{port.description}]")
    
    try:
        choice = int(input(f"Select port index (0-{len(ports)-1}): "))
        return ports[choice].device
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None

def init_db(db_name="fencing_data.db"):
    """Initializes the SQLite database based on the finalized schema."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create table based on Image 3 layout
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loopcount INTEGER,
            active_line VARCHAR(1),
            digi_A INTEGER,
            digi_B INTEGER,
            digi_C INTEGER,
            raw_A INTEGER,
            raw_B INTEGER,
            raw_C INTEGER,
            vout REAL,
            resistance REAL,
            short_circuit INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def process_output(cursor, line):
    if not line.startswith("data:"):
        return 

    try:
        payload = line.split(":", 1)[1]
        data = payload.split(";")
        
        if len(data) != 11:
            print(f"Skipping malformed line (Length {len(data)}): {line}")
            return

        cursor.execute("""
            INSERT INTO data(
                loopcount, active_line, 
                digi_A, digi_B, digi_C, 
                raw_A, raw_B, raw_C, 
                vout, resistance, short_circuit
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """, data)
        
    except Exception as e:
        print(f"Error processing line: {e}")

if __name__ == "__main__":
    init_db(DB_NAME)
    selected_port = select_com_port()
    
    if selected_port:
        try:
            # Keep one connection open for the duration of the script
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            with serial.Serial(selected_port, 115200, timeout=1) as ser:
                print(f"Connected to {selected_port}. Reading data...")
                while True:
                    line = ser.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        print(line)
                        process_output(cursor, line)
                        conn.commit() # Commit frequently or every X lines
        except KeyboardInterrupt:
            print("\nClosing...")
        finally:
            if 'conn' in locals():
                conn.close()