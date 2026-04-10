"""
Sensor Monitoring Station — Flask Web Server
=============================================
Run this file:   python app.py
Then open:       http://127.0.0.1:5000

The server reads a new sensor sample every second in a background
thread, logs it to SQLite and serves it to the dashboard via a
JSON API that the frontend polls every second.
"""

import threading
import time

from flask import Flask, jsonify, render_template

from alarm import AlarmSystem
from data_logger import DataLogger
from sensor_reader import SensorReader

# ══════════════════════════════════════════════════════════════
#  Global objects
# ══════════════════════════════════════════════════════════════
app     = Flask(__name__)
sensor  = SensorReader()
logger  = DataLogger()
alarm   = AlarmSystem()

# ══════════════════════════════════════════════════════════════
#  Background sampling thread
#  Reads one sample per second and logs it to the database.
# ══════════════════════════════════════════════════════════════
def sampling_loop():
    while True:
        data = sensor.read()
        logger.log(data)
        alarm.check(data)
        time.sleep(1)

thread = threading.Thread(target=sampling_loop, daemon=True)
thread.start()

# ══════════════════════════════════════════════════════════════
#  Routes
# ══════════════════════════════════════════════════════════════
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    """
    Returns JSON with:
        latest        — most recent single reading
        recent        — last 120 readings (for log table)
        alarm         — True / False
        alarm_message — human readable alarm string
    """
    latest = logger.get_latest()
    recent = logger.get_recent(120)

    return jsonify({
        "latest"       : latest,
        "recent"       : recent,
        "alarm"        : bool(alarm.active_alarms),
        "alarm_message": alarm.status_summary(),
    })


@app.route("/api/fault/<fault_type>", methods=["POST"])
def api_fault(fault_type):
    """
    POST /api/fault/high_temp      — inject high temperature fault
    POST /api/fault/gas_leak       — inject gas leak fault
    POST /api/fault/humidity_drop  — inject humidity drop fault
    POST /api/fault/clear          — clear all faults
    """
    if fault_type == "clear":
        sensor.clear_fault()
        return jsonify({"status": "fault cleared"})

    if fault_type in ("high_temp", "gas_leak", "humidity_drop"):
        sensor.inject_fault(fault_type)
        return jsonify({"status": f"fault injected: {fault_type}"})

    return jsonify({"error": "unknown fault type"}), 400


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Sensor Monitoring Station — starting server")
    print("  Open your browser at:  http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=False)