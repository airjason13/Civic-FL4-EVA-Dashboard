"""
Civic e:HEV (FL4) Telemetry Mock Simulator
Simulates realistic driving dynamics, hybrid power transitions,
regenerative braking events, and G-forces for desktop testing.
"""

import math
import time
from PyQt5.QtCore import QThread, pyqtSignal
from core.telemetry import VehicleTelemetry


class MockSimulator(QThread):
    telemetry_updated = pyqtSignal(VehicleTelemetry)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.telemetry = VehicleTelemetry(is_simulated=True, is_connected=True)
        self.step = 0.0

    def run(self):
        while self.running:
            self.step += 0.05
            t = self.step

            # 1. Driving Phase Simulation (Cycle of: Accelerate -> Cruise -> Hard Accel -> Regen Brake -> EV Idle)
            cycle_time = t % 40.0

            if cycle_time < 10.0:
                # Phase 1: EV City Cruise (0 -> 60 km/h)
                progress = cycle_time / 10.0
                target_speed = 60.0 * math.sin(progress * math.pi / 2.0)
                throttle = 35.0 + 10.0 * math.sin(t * 1.5)
                motor_kw = 22.0 + 8.0 * math.sin(t * 1.2)
                engine_rpm = 0
                drive_mode = "EV"
                g_long = 0.25 * math.cos(progress * math.pi / 2.0)
                g_lat = 0.20 * math.sin(t * 0.8)

            elif cycle_time < 22.0:
                # Phase 2: Highway On-Ramp Acceleration & Hybrid Boost (60 -> 108 km/h)
                progress = (cycle_time - 10.0) / 12.0
                target_speed = 60.0 + (48.0 * progress)
                throttle = 65.0 + 5.0 * math.sin(t * 2.0)
                motor_kw = 78.0 + 12.0 * math.sin(t * 2.5)
                engine_rpm = 2400 + int(600 * math.sin(t * 1.8))
                drive_mode = "HYBRID"
                g_long = 0.38 + 0.08 * math.sin(t)
                g_lat = 0.42 * math.sin(t * 0.5)

            elif cycle_time < 32.0:
                # Phase 3: High-speed Steady Cruise (108 km/h) with curve
                target_speed = 108.0 + 3.0 * math.sin(t * 0.6)
                throttle = 38.0 + 4.0 * math.sin(t * 0.8)
                motor_kw = 28.0 + 5.0 * math.sin(t * 0.5)
                engine_rpm = 1850 + int(100 * math.sin(t * 0.3))
                drive_mode = "HYBRID" if (int(t) % 6 < 4) else "EV"
                g_long = 0.05 * math.cos(t * 0.5)
                g_lat = 0.35 * math.sin(t * 0.4)

            else:
                # Phase 4: Regenerative Braking Deceleration (108 -> 45 km/h)
                progress = (cycle_time - 32.0) / 8.0
                target_speed = 108.0 - (63.0 * progress)
                throttle = 0.0
                motor_kw = -32.0 - 15.0 * math.sin(progress * math.pi)  # Strong regen
                engine_rpm = 0
                drive_mode = "REGEN"
                g_long = -0.48 - 0.15 * math.sin(progress * math.pi)
                g_lat = 0.15 * math.cos(t * 0.7)

            # 2. Smooth Values into Telemetry
            self.telemetry.speed_kmh = max(0.0, target_speed)
            self.telemetry.engine_rpm = max(0, engine_rpm)
            self.telemetry.throttle_pct = max(0.0, min(100.0, throttle))
            self.telemetry.motor_power_kw = motor_kw
            self.telemetry.drive_mode = drive_mode
            self.telemetry.g_long = g_long
            self.telemetry.g_lat = g_lat

            # Update Peak G
            current_total_g = math.sqrt(g_lat**2 + g_long**2)
            if current_total_g > self.telemetry.g_peak:
                self.telemetry.g_peak = round(current_total_g, 2)

            # 3. Hybrid Battery SoC & Voltage dynamics with high-frequency inverter ripple
            ripple = 2.4 * math.sin(t * 3.5) + 1.2 * math.sin(t * 7.8)
            if drive_mode == "REGEN":
                # Battery charging
                self.telemetry.battery_soc_pct = min(85.0, self.telemetry.battery_soc_pct + 0.04)
                base_v = 180.0 + 2.0 * math.sin(t * 2.0)
            elif drive_mode in ("HYBRID", "EV") and throttle > 50.0:
                # Discharging hard
                self.telemetry.battery_soc_pct = max(40.0, self.telemetry.battery_soc_pct - 0.03)
                base_v = 171.0 + 1.5 * math.sin(t * 2.0)
            else:
                base_v = 176.0 + 1.0 * math.sin(t * 0.8)

            self.telemetry.battery_voltage_v = round(base_v + ripple, 1)
            self.telemetry.battery_temp_c = int(24 + 3 * math.sin(t * 0.1) + 1.2 * math.cos(t * 0.4))
            self.telemetry.coolant_temp_c = int(88 + 4 * math.sin(t * 0.15) + 2.0 * math.cos(t * 0.6))
            self.telemetry.aux_voltage = round(14.1 + 0.3 * math.sin(t * 1.2) + 0.15 * math.cos(t * 3.4), 1)
            self.telemetry.inverter_temp_c = int(42 + 4 * math.sin(t * 0.12) + (abs(motor_kw) / 135.0) * 8)
            self.telemetry.trans_temp_c = int(65 + 3 * math.sin(t * 0.08))
            self.telemetry.motor_rpm = int(abs(motor_kw) * 35 + self.telemetry.speed_kmh * 42)
            self.telemetry.fuel_l_100km = round(4.2 + 0.8 * math.sin(t * 0.2) if engine_rpm > 0 else 0.0, 1)

            # Update Waveform History buffers
            self.telemetry.voltage_history.append(self.telemetry.battery_voltage_v)
            if len(self.telemetry.voltage_history) > 30:
                self.telemetry.voltage_history.pop(0)

            self.telemetry.batt_temp_history.append(float(self.telemetry.battery_temp_c))
            if len(self.telemetry.batt_temp_history) > 30:
                self.telemetry.batt_temp_history.pop(0)

            self.telemetry.coolant_history.append(float(self.telemetry.coolant_temp_c))
            if len(self.telemetry.coolant_history) > 30:
                self.telemetry.coolant_history.pop(0)

            self.telemetry.aux_history.append(self.telemetry.aux_voltage)
            if len(self.telemetry.aux_history) > 30:
                self.telemetry.aux_history.pop(0)

            self.telemetry.last_update_ts = time.time()
            self.telemetry_updated.emit(self.telemetry)

            # Sleep 33ms (~30 FPS telemetry feed)
            self.msleep(33)

    def stop(self):
        self.running = False
        self.wait(1000)
