"""
WattWise: Smart Classroom Energy Anomaly Detection & Reasoning System
Flask Backend Server: ESP32-S3 IoT Ingestion, Python DNN Model & Generative AI Engine
"""

from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import datetime
import os
import math

app = Flask(__name__, static_folder='.')

# In-memory storage for real-time telemetry and audit logs
TELEMETRY_LOGS = []
MAX_LOGS = 100

# -------------------------------------------------------------
# 1. PYTHON DEEP NEURAL NETWORK (4 -> 8 -> 1)
# -------------------------------------------------------------
class AnomalyDNN:
    def __init__(self):
        np.random.seed(42)
        # Weights: Input (4) -> Hidden (8) -> Output (1)
        self.W1 = np.random.randn(8, 4) * 0.5
        self.b1 = np.zeros((8, 1))
        self.W2 = np.random.randn(1, 8) * 0.5
        self.b2 = 0.0
        self.train_synthetic_data()

    def sigmoid(self, z):
        return 1.0 / (1.0 + np.exp(-np.clip(z, -15, 15)))

    def forward(self, x):
        # x shape: (4, 1)
        h = self.sigmoid(np.dot(self.W1, x) + self.b1)
        y = self.sigmoid(np.dot(self.W2, h) + self.b2)
        return h, float(y[0][0])

    def train_synthetic_data(self, samples=500, epochs=800, lr=0.3):
        # Features: [Current/1.5, Occupancy (0/1), SchoolHours (0/1), Delta_I/1.5]
        X = []
        Y = []
        for _ in range(samples):
            current = np.random.uniform(0.0, 0.03) if np.random.rand() < 0.45 else np.random.uniform(0.1, 1.8)
            occ = 1 if np.random.rand() > 0.5 else 0
            sch = 1 if np.random.rand() > 0.5 else 0
            delta_i = np.random.uniform(0.0, 0.05) if np.random.rand() < 0.8 else np.random.uniform(0.5, 1.5)

            # Ground truth anomaly logic
            is_anomaly = 1 if (
                (occ == 0 and current > 0.15) or     # Waste in empty classroom
                (sch == 0 and current > 0.15) or     # Unauthorized night consumption
                (current > 1.25) or                  # Overcurrent / overload
                (delta_i > 0.85)                     # Sudden transient surge
            ) else 0

            x_vec = np.array([[current / 1.5], [occ], [sch], [delta_i / 1.5]])
            X.append(x_vec)
            Y.append(is_anomaly)

        # SGD Training
        for _ in range(epochs):
            for x_vec, t in zip(X, Y):
                h, y = self.forward(x_vec)
                e = y - t
                g = e * y * (1.0 - y)
                gh = g * (self.W2.T * h * (1.0 - h))
                self.W2 -= lr * g * h.T
                self.W1 -= lr * np.dot(gh, x_vec.T)
                self.b1 -= lr * gh
                self.b2 -= lr * g

        # Compute accuracy
        correct = sum(1 for x_vec, t in zip(X, Y) if (self.forward(x_vec)[1] >= 0.5) == t)
        self.accuracy = round((correct / samples) * 100, 2)
        print(f"[WattWise DNN] Initialized & Trained: 4->8->1 | Accuracy: {self.accuracy}%")

dnn_model = AnomalyDNN()

# -------------------------------------------------------------
# 2. AUTOMATIC OCCUPANCY & GENERATIVE AI REASONING ENGINE
# -------------------------------------------------------------
# -------------------------------------------------------------
# 2. AUTOMATIC OCCUPANCY & GENERATIVE AI REASONING ENGINE
# -------------------------------------------------------------
def calculate_occupancy(room_type, vacancy_override=False):
    if vacancy_override:
        return 0
    if room_type == 'normal_class':
        return 1  # Normal Class (Class Hours 08:00 - 17:00) -> Occupied
    # after_hours, laboratory, closed -> Empty
    return 0

def get_school_hours(room_type):
    # Active operational hours: normal_class and laboratory = 1; after_hours and closed = 0
    if room_type in ['normal_class', 'laboratory']:
        return 1
    return 0

def format_room_type(room_type):
    mapping = {
        'normal_class': 'Normal Class (Class Hours)',
        'after_hours': 'After-Hours / Night',
        'laboratory': 'Laboratory Session',
        'closed': 'Closed Facility'
    }
    return mapping.get(room_type, room_type)

def generate_ai_explanation(current, power, occupancy, school_hours, delta_i, anomaly_score, room_type='normal_class', vacancy_override=False):
    is_anomaly = anomaly_score >= 0.5
    kwh_8h = round((power / 1000.0) * 8.0, 3)
    cost_inr = round(kwh_8h * 7.5, 2)
    carbon_g = round(kwh_8h * 820, 1)
    label = format_room_type(room_type)

    if not is_anomaly and current < 0.05:
        why = "The load circuit is dormant. Hall-effect current is at sensor zero reference. Standard standby idle pattern."
        rec = "Optimal standby behavior. No control commands necessary."
        severity = "NONE"
    elif not is_anomaly:
        why = f"Legitimate academic load: Room ({label}) is Occupied during scheduled hours with stable consumption of {power:.1f}W ({current:.2f}A)."
        rec = "Continuous baseline monitoring active. No anomalies detected."
        severity = "NORMAL"
    elif delta_i > 0.85 or current > 1.25:
        why = f"CRITICAL SURGE / FAULT: Current escalated instantaneously to {current:.2f}A (step change delta = {delta_i:.2f}A), exceeding safe operational bounds."
        rec = "Trigger smart relay cut-off. Dispatch technician to inspect circuit branch for short circuits, degraded insulation, or motor stalling."
        severity = "CRITICAL"
    elif occupancy == 0:
        if vacancy_override:
            why = f"UNEXPECTED VACANCY ENERGY DRAIN: Classroom is scheduled for session, but is unexpectedly empty while appliances draw {power:.1f}W ({current:.2f}A)."
            rec = f"Issue automated shut-down command to lighting/fan relays. Preventing {kwh_8h} kWh unnecessary waste and ₹{cost_inr} penalty per 8-hour shift."
        elif room_type == 'after_hours':
            why = f"AFTER-HOURS UNREGISTERED LOAD: Room is marked {label} (facility is closed), but active power consumption of {power:.1f}W is detected."
            rec = "Cross-reference with building facility access control. Initiate remote timer cutoff if room is unreserved."
        elif room_type == 'laboratory':
            why = f"LABORATORY UNATTENDED CONSUMPTION: Laboratory is unreserved/empty in current schedule, yet equipment is drawing {power:.1f}W ({current:.2f}A)."
            rec = f"Verify if lab experiments require power. If not, trigger relay shut-off to save {kwh_8h} kWh."
        elif room_type == 'closed':
            why = f"CLOSED ROOM POWER LEAKAGE: Room is marked CLOSED, but active power draw of {power:.1f}W is detected. Unnecessary energy consumption identified."
            rec = f"Inspect for phantom vampire loads or forgotten switches in closed room. Isolate power to save {kwh_8h} kWh."
        else:
            why = f"EMPTY CLASSROOM ENERGY DRAIN: Room is automatically marked empty, yet appliances continue drawing {power:.1f}W ({current:.2f}A)."
            rec = f"Issue automated shut-down command to lighting/fan relays. Preventing {kwh_8h} kWh unnecessary waste and ₹{cost_inr} penalty per 8-hour shift."
        severity = "HIGH"
    else:
        why = f"AFTER-HOURS UNREGISTERED LOAD: Facility is closed ({label}), but active power draw of {power:.1f}W is detected."
        rec = "Cross-reference with building facility access control. Initiate remote timer cutoff if room is unreserved."
        severity = "MEDIUM"

    return {
        "why": why,
        "recommendation": rec,
        "severity": severity,
        "metrics": {
            "wasted_kwh_8h": kwh_8h,
            "cost_penalty_inr": cost_inr,
            "carbon_footprint_g": carbon_g
        }
    }

# -------------------------------------------------------------
# 3. REST API ENDPOINTS
# -------------------------------------------------------------

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/telemetry', methods=['POST'])
def receive_telemetry():
    """
    Endpoint for physical ESP32-S3 microcontroller to POST real-time sensor packets.
    Payload: {"voltage": 5.0, "current": 0.40, "room_type": "normal_class", "device_id": "ESP32_ROOM_101"}
    """
    data = request.get_json(force=True)
    current = float(data.get('current', 0.0))
    voltage = float(data.get('voltage', 5.0))
    room_type = str(data.get('room_type', 'normal_class'))
    vacancy_override = bool(data.get('vacancy_override', False))
    device_id = str(data.get('device_id', 'ESP32_S3_SIM'))
    delta_i = float(data.get('delta_i', 0.0))

    now = datetime.datetime.now()
    power = voltage * current

    # Automatic occupancy & schedule determination directly from room_type
    occupancy = calculate_occupancy(room_type, vacancy_override)
    school_hours = get_school_hours(room_type)

    # Run DNN inference
    x_input = np.array([[current / 1.5], [occupancy], [school_hours], [delta_i / 1.5]])
    _, anomaly_score = dnn_model.forward(x_input)

    # Run Generative AI reasoning
    ai_result = generate_ai_explanation(current, power, occupancy, school_hours, delta_i, anomaly_score, room_type, vacancy_override)

    entry = {
        "timestamp": now.strftime("%H:%M:%S"),
        "device_id": device_id,
        "room_type": room_type,
        "voltage": voltage,
        "current": current,
        "power": round(power, 2),
        "occupancy": occupancy,
        "school_hours": school_hours,
        "anomaly_score": round(anomaly_score, 4),
        "is_anomaly": anomaly_score >= 0.5,
        "ai_explanation": ai_result
    }

    TELEMETRY_LOGS.append(entry)
    if len(TELEMETRY_LOGS) > MAX_LOGS:
        TELEMETRY_LOGS.pop(0)

    return jsonify({"status": "SUCCESS", "analysis": entry})

@app.route('/api/dnn/predict', methods=['POST'])
def dnn_predict():
    data = request.get_json(force=True)
    current = float(data.get('current', 0.0))
    room_type = str(data.get('room_type', 'normal_class'))
    vacancy_override = bool(data.get('vacancy_override', False))
    delta_i = float(data.get('delta_i', 0.0))

    occ = calculate_occupancy(room_type, vacancy_override)
    sch = get_school_hours(room_type)

    x_input = np.array([[current / 1.5], [occ], [sch], [delta_i / 1.5]])
    _, anomaly_score = dnn_model.forward(x_input)
    return jsonify({
        "anomaly_score": round(anomaly_score, 4),
        "is_anomaly": anomaly_score >= 0.5,
        "model_accuracy": dnn_model.accuracy,
        "occupancy": occ,
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify({"logs": TELEMETRY_LOGS, "total": len(TELEMETRY_LOGS)})

@app.route('/api/model/info', methods=['GET'])
def model_info():
    return jsonify({
        "model_type": "Multi-Layer Perceptron (DNN)",
        "topology": [4, 8, 1],
        "activation": "Sigmoid",
        "accuracy": dnn_model.accuracy,
        "features": ["Normalized Current", "Occupancy", "School Hours", "Current Derivative"]
    })

if __name__ == '__main__':
    print("==================================================================")
    print(" WattWise Energy Optimization & Anomaly Reasoning Server Running ")
    print(" Web Dashboard: http://localhost:5000                             ")
    print(" REST API:      http://localhost:5000/api/telemetry               ")
    print("==================================================================")
    app.run(host='0.0.0.0', port=5000, debug=False)
