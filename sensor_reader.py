import numpy as np
import time


class SensorReader:
    """
    Simulates three physical sensors:
        DHT22  — temperature (C) and humidity (%)
        BMP280 — barometric pressure (hPa)
        MQ2    — gas / smoke level (ppm)

    Each sensor has:
        - A slowly drifting baseline (like a real environment)
        - Gaussian noise on every reading (like real sensor hardware)
        - Occasional spike to simulate a real world disturbance
    """

    def __init__(self):
        # ── Baseline values ──────────────────────────────────
        self.base_temp     = 27.0    # celsius
        self.base_humidity = 55.0    # percent
        self.base_pressure = 1013.0  # hPa
        self.base_gas      = 200.0   # ppm

        # ── Drift state ──────────────────────────────────────
        self._temp_drift     = 0.0
        self._humidity_drift = 0.0
        self._pressure_drift = 0.0
        self._gas_drift      = 0.0

        # ── Fault injection ──────────────────────────────────
        self.fault_active = False
        self.fault_type   = None

        self._tick = 0

    # ─────────────────────────────────────────────────────────
    def _drift(self, current, speed=0.02):
        """Slowly random-walk the baseline so it feels alive."""
        return current + np.random.normal(0, speed)

    # ─────────────────────────────────────────────────────────
    def read(self):
        """
        Return one set of sensor readings as a dict.
        Call this every second from the data logger.
        """
        self._tick += 1

        # Update drifts
        self._temp_drift     = self._drift(self._temp_drift,     0.01)
        self._humidity_drift = self._drift(self._humidity_drift, 0.05)
        self._pressure_drift = self._drift(self._pressure_drift, 0.02)
        self._gas_drift      = self._drift(self._gas_drift,      0.5)

        # Base readings with noise
        temp     = self.base_temp     + self._temp_drift     + np.random.normal(0, 0.3)
        humidity = self.base_humidity + self._humidity_drift + np.random.normal(0, 0.5)
        pressure = self.base_pressure + self._pressure_drift + np.random.normal(0, 0.2)
        gas      = self.base_gas      + self._gas_drift      + np.random.normal(0, 5.0)

        # Occasional random spike (1 in 60 chance each tick)
        if np.random.randint(0, 60) == 0:
            gas += np.random.uniform(80, 200)

        # Fault overrides
        if self.fault_active:
            if self.fault_type == "high_temp":
                temp += np.random.uniform(15, 25)
            elif self.fault_type == "gas_leak":
                gas  += np.random.uniform(300, 600)
            elif self.fault_type == "humidity_drop":
                humidity -= np.random.uniform(20, 35)

        # Clamp to realistic physical limits
        temp     = float(np.clip(temp,     -10.0, 80.0))
        humidity = float(np.clip(humidity,   0.0, 100.0))
        pressure = float(np.clip(pressure, 900.0, 1100.0))
        gas      = float(np.clip(gas,        0.0, 10000.0))

        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "temp"     : round(temp,     2),
            "humidity" : round(humidity, 2),
            "pressure" : round(pressure, 2),
            "gas"      : round(gas,      1),
        }

    # ─────────────────────────────────────────────────────────
    def inject_fault(self, fault_type):
        """Activate a fault: 'high_temp', 'gas_leak', 'humidity_drop'"""
        self.fault_active = True
        self.fault_type   = fault_type

    def clear_fault(self):
        """Return all sensors to normal operating conditions."""
        self.fault_active = False
        self.fault_type   = None