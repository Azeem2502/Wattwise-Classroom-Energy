# WattWise: Smart Classroom Energy Monitoring & Anomaly Detection System

WattWise is an end-to-end IoT, Deep Neural Network (DNN), and Generative AI powered smart energy management platform designed for educational and institutional classrooms. It monitors power consumption via an ESP32-S3 microcontroller and ACS712 current sensor, detects anomalous energy usage patterns using an in-browser & backend Multi-Layer Perceptron (DNN), and provides real-time natural language root-cause analysis and actionable remediation directives via Generative AI.

---

## 🚀 Key Features

- **Hardware & Sensor Simulation**: Accurate mathematical modeling of the ESP32-S3 SoC, ACS712-05B Hall-Effect current sensor, and a 10kΩ/20kΩ voltage divider circuit.
- **Automated Room & Schedule Occupancy**: Occupancy is dynamically calculated based on room type (`Normal Class`, `Laboratory`, `After-Hours / Night`, `Closed`) without requiring manual toggling.
- **Deep Neural Network (DNN) Anomaly Classifier**:
  - $4 \to 8 \to 1$ topology trained using Stochastic Gradient Descent (SGD) with backpropagation.
  - Features: Normalized Current ($I/1.5$), Occupancy ($0/1$), School Hours Window ($0/1$), and Instantaneous Derivative ($\Delta I/1.5$).
  - Live synaptic activation visualizer rendering real-time neuron intensities and firing paths.
- **Generative AI Decision Engine**:
  - Contextual root-cause diagnosis ("Why").
  - Prescriptive remediation steps ("Action to Take").
  - Real-time impact quantification: 8-hour projected waste in kWh, financial cost penalty in ₹, and carbon footprint in $g\text{ CO}_2$.
- **Real-Time Interactive Waveforms**: Live Chart.js rolling graph with color-coded markers for normal operations vs. anomaly states.
- **Hardware Circuit Wiring & Architecture Tabs**: Interactive SVG circuit schematics detailing pinout mappings, voltage scaling math, and formulas.
- **Audit Logging**: Exportable real-time event log with CSV download capability.

---

## 📂 Project Structure

```text
├── index.html                   # Main interactive dashboard with standalone client-side engine
├── WattWise - Classroom Energy Simulation.html # Synchronized standalone dashboard copy
├── app.py                       # Python Flask backend (REST API, Python DNN, & GenAI engine)
├── esp32_firmware.ino           # Embedded C++ firmware for physical ESP32-S3 microcontroller
├── start_server.bat             # 1-click Windows launcher for Flask server
├── REVIEW_PRESENTATION_GUIDE.md # Viva defense script, reviewer questions, and technical formulas
└── README.md                    # Project documentation
```

---

## ⚡ Quick Start

### Option 1: Standalone Browser (Zero Setup / 100% Offline)
Simply double-click `index.html` in any modern web browser (Google Chrome, Microsoft Edge, Mozilla Firefox). The simulation, in-browser neural network training, Chart.js graphs, and AI reasoning engine will run completely client-side without requiring internet access or software installations.

### Option 2: Full Python Flask Backend
1. Ensure Python 3.8+ is installed.
2. Install dependencies:
   ```bash
   pip install flask numpy
   ```
3. Run the backend server:
   ```bash
   python app.py
   ```
   *(Or double-click `start_server.bat` on Windows)*
4. Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🔌 Hardware Specifications

- **Microcontroller**: ESP32-S3 (Dual-core Xtensa LX7 @ 240 MHz, ADC1 GPIO 4)
- **Current Sensor**: ACS712-05B ($2500\text{ mV}$ null offset, $185\text{ mV/A}$ sensitivity)
- **Signal Conditioning**: $10\text{k}\Omega / 20\text{k}\Omega$ voltage divider (clamps $5\text{ V}$ sensor output to $3.33\text{ V}$ to protect ESP32 ADC)
- **Communication**: Wi-Fi 802.11 b/g/n, HTTP POST JSON telemetry to `/api/telemetry`

---

## 👥 Authors
- **Mohamed Azeem**
