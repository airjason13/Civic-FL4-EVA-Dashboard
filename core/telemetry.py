"""
Civic e:HEV (FL4) Telemetry Data Model
Defines the state and sensor metrics captured from OBD2 / simulated.
"""

from dataclasses import dataclass, field
import time


@dataclass
class VehicleTelemetry:
    # Basic Speed & Engine metrics
    speed_kmh: float = 0.0          # 0 ~ 220 km/h
    engine_rpm: int = 0             # 0 ~ 6500 RPM (2.0L Atkinson engine)
    coolant_temp_c: int = 88        # Engine Coolant Temp °C (typically 80~95°C)
    aux_voltage: float = 14.1       # 12V Auxiliary battery voltage (V)
    throttle_pct: float = 0.0       # Throttle pedal position 0 ~ 100%

    # Honda e:HEV Hybrid Metrics (Mode 22)
    battery_soc_pct: float = 78.0   # High-Voltage Battery SoC % (typically 30~85%)
    battery_voltage_v: float = 176.0 # High-Voltage Battery pack voltage (V)
    battery_temp_c: int = 24        # High-Voltage Battery module temp °C
    motor_power_kw: float = 0.0     # Drive Motor (MG2) power in kW (-50kW regen to +135kW output)
    motor_rpm: int = 0              # Drive Motor RPM
    inverter_temp_c: int = 42       # Power Control Unit / Inverter Temp °C
    trans_temp_c: int = 65          # e-CVT Transmission Fluid Temp °C
    fuel_l_100km: float = 4.2       # Instant / average fuel economy (L/100km)

    # Dynamics & G-Force
    g_lat: float = 0.0              # Lateral G (turn left/right: -1.5G to +1.5G)
    g_long: float = 0.0             # Longitudinal G (accel/brake: -1.5G to +1.5G)
    g_peak: float = 0.82            # Peak G recorded in current session

    # Powertrain State
    # Modes: "EV", "HYBRID", "ENGINE", "CHARGE", "REGEN"
    drive_mode: str = "EV"
    gear: str = "D"
    is_connected: bool = True
    is_simulated: bool = False
    last_update_ts: float = field(default_factory=time.time)

    # Historical waveforms for oscilloscope widgets (stores last 30 samples)
    voltage_history: list = field(default_factory=lambda: [176.0 + 3.5 * __import__("math").sin(i * 0.45) + 1.8 * __import__("math").cos(i * 0.9) for i in range(30)])
    batt_temp_history: list = field(default_factory=lambda: [24.0 + 1.5 * __import__("math").sin(i * 0.35) for i in range(30)])
    coolant_history: list = field(default_factory=lambda: [88.0 + 3.0 * __import__("math").sin(i * 0.28) for i in range(30)])
    aux_history: list = field(default_factory=lambda: [14.1 + 0.35 * __import__("math").sin(i * 0.55) for i in range(30)])
