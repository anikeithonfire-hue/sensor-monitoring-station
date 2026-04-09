class AlarmSystem:
    """
    Checks every sensor reading against safety thresholds.
    Simulates LED indicators:
        GREEN  — all values normal
        RED    — one or more values outside safe range

    Thresholds are based on typical industrial indoor monitoring limits.
    On real hardware these would trigger GPIO pins connected to physical LEDs.
    """

    THRESHOLDS = {
        "temp"    : {"min": 10.0,  "max": 45.0,   "unit": "C"},
        "humidity": {"min": 20.0,  "max": 85.0,   "unit": "%"},
        "pressure": {"min": 980.0, "max": 1040.0, "unit": "hPa"},
        "gas"     : {"min": 0.0,   "max": 500.0,  "unit": "ppm"},
    }

    def __init__(self):
        self.active_alarms = []
        self.led_status    = "GREEN"   # "GREEN" or "RED"

    # ─────────────────────────────────────────────────────────
    def check(self, data: dict):
        """
        Evaluate one reading dict against all thresholds.
        Updates self.active_alarms and self.led_status.
        Returns True if any alarm is active.
        """
        self.active_alarms = []

        for sensor, limits in self.THRESHOLDS.items():
            value = data.get(sensor)
            if value is None:
                continue

            if value < limits["min"]:
                self.active_alarms.append(
                    f"{sensor.upper()} LOW: {value} {limits['unit']} "
                    f"(min {limits['min']} {limits['unit']})"
                )
            elif value > limits["max"]:
                self.active_alarms.append(
                    f"{sensor.upper()} HIGH: {value} {limits['unit']} "
                    f"(max {limits['max']} {limits['unit']})"
                )

        self.led_status = "RED" if self.active_alarms else "GREEN"
        return bool(self.active_alarms)

    # ─────────────────────────────────────────────────────────
    def status_summary(self):
        """Return a short human readable status string."""
        if not self.active_alarms:
            return "All sensors normal"
        return " | ".join(self.active_alarms)