import random
import time

class MockSerial:
    def __init__(self):
        self.loop_counter = 0
        self.sequence = ['C', 'B', 'A'] 
        self.seq_idx = 0
        self.R1 = 22.0
        self.Vin = 4.1
        self.short_active = False
        self.short_timer = 0

    def readline(self):
        time.sleep(0.1)
        active_letter = self.sequence[self.seq_idx]
        
        # 1. Logic for "Sparkling" Short Circuits
        if not self.short_active and random.random() < 0.03:
            self.short_active = True
            self.short_timer = random.randint(5, 12) # Duration of the "sparkle"

        # 2. Generate Realistic Raw Values
        # To get Resistance between 0-20 ohms, Raw must be between ~535 and 1023
        if self.short_active:
            # "Sparkle" effect: Rapidly oscillating between near-zero and high interference
            raw_A = random.choice([random.randint(950, 1023), random.randint(100, 400)])
            raw_B = random.choice([random.randint(950, 1023), random.randint(100, 400)])
            raw_C = random.randint(500, 1023)
            short_status = random.choice([2, 3])
            self.short_timer -= 1
            if self.short_timer <= 0: self.short_active = False
        else:
            # Normal data: Targeted Raw to keep Resistance between 0 and 20
            # Math: Raw = 1023 / ( (TargetRes / R1) + 1 )
            raw_A = random.randint(550, 1023) 
            raw_B = random.randint(550, 1023)
            raw_C = random.randint(550, 1023)
            short_status = 0

        # Calculate values for the currently active line
        active_raw = {'A': raw_A, 'B': raw_B, 'C': raw_C}[active_letter]
        vout = (active_raw * self.Vin) / 1023.0
        # Resistance calculation derived from: R = R1 * ( (Vin/Vout) - 1 )
        res = self.R1 * (self.Vin / vout - 1.0) if vout > 0 else 0.0
        
        # Ensure we clamp mock resistance for "Normal" depiction
        if not self.short_active: res = max(0.0, min(20.0, res))

        # 3. Exact Arduino print_data() Replication
        noise = (
            f"\n ------- Line {active_letter} ------- \n"
            f"Output A: 0\nOutput B: 0\nOutput C: 0\n \n"
            f"Raw A: {raw_A}\nRaw B: {raw_B}\nRaw C: {raw_C}\n \n"
            f"Vout {active_letter}: {vout:.2f} V\n"
            f"Resistance {active_letter}: {res:.2f} Ω\n"
            f"----------------------"
        )

        # 4. Machine Readable Packet
        data_packet = (f"data:{self.loop_counter};{active_letter};"
                       f"0;0;0;{raw_A};{raw_B};{raw_C};"
                       f"{vout:.2f};{res:.2f};{short_status}")

        full_output = f"{noise}\n{data_packet}"

        # 5. Sequence Management
        self.seq_idx += 1
        if self.seq_idx >= len(self.sequence):
            self.seq_idx = 0
            self.loop_counter += 1
            
        return full_output.encode('utf-8')

    def in_waiting(self): return True