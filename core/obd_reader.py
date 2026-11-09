"""
Civic e:HEV (FL4) Hardware OBD2 Reader
Implements robust serial communication with OBDLink EX / MX+.
Features:
- Protocol Lock: ISO 15765-4 11-bit 500k (AT SP 6)
- Targeted ECU Addressing (AT SH 7E0 / 7E2, strictly avoids broadcast 0x7DF)
- Rate-limiting & Guard Delay (25ms between queries)
- Smart Sleep Backoff on engine-off / NO DATA
"""

import time
import serial
from PyQt5.QtCore import QThread, pyqtSignal
from core.telemetry import VehicleTelemetry


class OBDReader(QThread):
    telemetry_updated = pyqtSignal(VehicleTelemetry)
    connection_status = pyqtSignal(bool, str)

    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.ser = None
        self.telemetry = VehicleTelemetry(is_simulated=False, is_connected=False)
        self.current_header = None

    def send_cmd(self, cmd: str, timeout_sec: float = 0.5) -> str:
        """Sends an AT/PID command and reads response until prompt '>'."""
        if not self.ser or not self.ser.is_open:
            return ""
        try:
            self.ser.reset_input_buffer()
            self.ser.write((cmd.strip() + "\r").encode("ascii"))
            
            # Guard delay to prevent bus contention
            time.sleep(0.025)

            start = time.time()
            buffer = bytearray()
            while time.time() - start < timeout_sec:
                if self.ser.in_waiting > 0:
                    ch = self.ser.read(1)
                    if ch == b'>':
                        break
                    buffer.extend(ch)
                else:
                    time.sleep(0.005)

            raw = buffer.decode("ascii", errors="ignore").replace("\r", " ").replace("\n", " ").strip()
            return raw
        except Exception as e:
            return ""

    def set_header(self, header: str):
        """Switches CAN Request Header only if different."""
        if self.current_header != header:
            res = self.send_cmd(f"AT SH {header}")
            self.current_header = header

    def initialize_obd(self) -> bool:
        """Strict protocol initialization for Honda Civic e:HEV."""
        try:
            self.connection_status.emit(False, f"Connecting to {self.port}...")
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.8)
            time.sleep(0.3)

            # 1. Reset
            self.send_cmd("AT Z", 1.0)
            time.sleep(0.5)

            # 2. Quiet options
            self.send_cmd("AT E0")   # Echo off
            self.send_cmd("AT L0")   # Linefeeds off
            self.send_cmd("AT S0")   # Spaces off

            # 3. SAFETY PROTOCOL LOCK: ISO 15765-4 11-bit 500kbps (Never auto-scan)
            resp = self.send_cmd("AT SP 6")
            if "OK" not in resp:
                self.connection_status.emit(False, "Protocol lock failed")
                return False

            self.send_cmd("AT AT 1")  # Adaptive timing
            self.current_header = None
            self.connection_status.emit(True, "Connected (CAN 500k Locked)")
            return True
        except Exception as ex:
            self.connection_status.emit(False, f"Port error: {ex}")
            return False

    def run(self):
        while self.running:
            if not self.ser or not self.ser.is_open:
                if not self.initialize_obd():
                    self.msleep(3000)
                    continue

            consecutive_no_data = 0
            low_freq_timer = 0.0

            while self.running:
                loop_start = time.time()

                # --- 1. High Frequency Queries (30 Hz): Speed, Throttle, RPM ---
                self.set_header("7E0")  # ECM Engine Module

                # 1.1 Speed (010D)
                res_speed = self.send_cmd("010D")
                if "410D" in res_speed.replace(" ", ""):
                    try:
                        clean = res_speed.replace(" ", "").split("410D")[1][:2]
                        self.telemetry.speed_kmh = float(int(clean, 16))
                        consecutive_no_data = 0
                    except (ValueError, IndexError):
                        pass
                elif "NODATA" in res_speed:
                    consecutive_no_data += 1

                # 1.2 Throttle (0111)
                res_throt = self.send_cmd("0111")
                if "4111" in res_throt.replace(" ", ""):
                    try:
                        clean = res_throt.replace(" ", "").split("4111")[1][:2]
                        self.telemetry.throttle_pct = round(int(clean, 16) * 100.0 / 255.0, 1)
                    except (ValueError, IndexError):
                        pass

                # 1.3 Engine RPM (010C)
                res_rpm = self.send_cmd("010C")
                if "410C" in res_rpm.replace(" ", ""):
                    try:
                        clean = res_rpm.replace(" ", "").split("410C")[1][:4]
                        val = int(clean, 16)
                        self.telemetry.engine_rpm = int(val / 4)
                        self.telemetry.drive_mode = "HYBRID" if self.telemetry.engine_rpm > 400 else "EV"
                    except (ValueError, IndexError):
                        pass

                # --- 2. Low Frequency Queries (Every ~1.0 sec): SoC, Voltage, Coolant ---
                if time.time() - low_freq_timer > 1.0:
                    low_freq_timer = time.time()

                    # 2.1 Battery SoC (22005B) - Header 7E0
                    res_soc = self.send_cmd("22005B")
                    if "62005B" in res_soc.replace(" ", ""):
                        try:
                            clean = res_soc.replace(" ", "").split("62005B")[1][:2]
                            soc = int(clean, 16) * 100.0 / 255.0
                            self.telemetry.battery_soc_pct = round(soc, 1)
                        except (ValueError, IndexError):
                            pass

                    # 2.2 Battery Voltage (22005A)
                    res_volt = self.send_cmd("22005A")
                    if "62005A" in res_volt.replace(" ", ""):
                        try:
                            clean = res_volt.replace(" ", "").split("62005A")[1][:4]
                            v = int(clean, 16) / 10.0
                            self.telemetry.battery_voltage_v = round(v, 1)
                        except (ValueError, IndexError):
                            pass

                    # 2.3 Coolant Temp (0105)
                    res_cool = self.send_cmd("0105")
                    if "4105" in res_cool.replace(" ", ""):
                        try:
                            clean = res_cool.replace(" ", "").split("4105")[1][:2]
                            self.telemetry.coolant_temp_c = int(clean, 16) - 40
                        except (ValueError, IndexError):
                            pass

                    # 2.4 Aux 12V Voltage (0142)
                    res_aux = self.send_cmd("0142")
                    if "4142" in res_aux.replace(" ", ""):
                        try:
                            clean = res_aux.replace(" ", "").split("4142")[1][:4]
                            self.telemetry.aux_voltage = round(int(clean, 16) / 1000.0, 2)
                        except (ValueError, IndexError):
                            pass

                    # Update history buffers
                    self.telemetry.voltage_history.append(self.telemetry.battery_voltage_v)
                    if len(self.telemetry.voltage_history) > 30: self.telemetry.voltage_history.pop(0)
                    self.telemetry.batt_temp_history.append(float(self.telemetry.battery_temp_c))
                    if len(self.telemetry.batt_temp_history) > 30: self.telemetry.batt_temp_history.pop(0)
                    self.telemetry.coolant_history.append(float(self.telemetry.coolant_temp_c))
                    if len(self.telemetry.coolant_history) > 30: self.telemetry.coolant_history.pop(0)
                    self.telemetry.aux_history.append(self.telemetry.aux_voltage)
                    if len(self.telemetry.aux_history) > 30: self.telemetry.aux_history.pop(0)

                # --- 3. Smart Sleep Backoff ---
                # If vehicle turned off (5 consecutive NO DATAs), pause querying to not wake Gateway
                if consecutive_no_data >= 5:
                    self.telemetry.is_connected = False
                    self.connection_status.emit(False, "Vehicle Standby / Engine Off")
                    time.sleep(2.0)
                else:
                    self.telemetry.is_connected = True

                self.telemetry.last_update_ts = time.time()
                self.telemetry_updated.emit(self.telemetry)

                # Sleep to cap loop rate at ~30Hz
                elapsed = time.time() - loop_start
                if elapsed < 0.033:
                    self.msleep(int((0.033 - elapsed) * 1000))

    def stop(self):
        self.running = False
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass
        self.wait(1000)
