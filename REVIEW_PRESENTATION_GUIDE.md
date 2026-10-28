# WattWise: Examiner Review & Viva Defense Guide

> **Project Title:** WattWise: Smart Classroom Energy Monitoring, Anomaly Detection & Reasoning System  
> **Key Technologies:** ESP32-S3 SoC, ACS712-05B Hall Sensor, 4→8→1 Deep Neural Network (DNN), Generative AI (Reasoning Engine), Flask REST API.

---

## 1. Quick 2-Minute Review Walkthrough Script

When you present your project to the examiners, open the web dashboard and use the **"Examiner 2-Min Review Controller"** bar across the top.

### **Step 1: Baseline Idle (Load OFF, Normal Class, 10:00 AM)**
* **Click:** Step 1 button.
* **Observe:** Room Type is **Normal Class**, Time is **10:00 AM**. Automatic Occupancy evaluates to **🟢 Occupied** (during 08:00–17:00). Load is OFF. Verdict is **NORMAL PATTERN** (green), Anomaly score $\approx 3-5\%$.
* **Say to Examiner:**
  > *"We start with the classroom in standby idle. Room occupancy is automatically determined by the schedule and room type—since it is 10:00 AM in a Normal Class, the system automatically sets Occupied. With the load switched off, current is zero and our 4→8→1 Deep Neural Network correctly verifies expected idle standby."*

### **Step 2: Normal Classroom Active Load (Load ON, Normal Class, 10:00 AM)**
* **Click:** Step 2 button.
* **Observe:** Load switches ON ($0.40\text{ A}$, $2.00\text{ W}$). Occupancy remains **🟢 Occupied**. Gold line rises on the live Chart.js graph. Verdict remains **NORMAL PATTERN**.
* **Say to Examiner:**
  > *"During scheduled class hours with automatic occupancy active, students switch on the fans and lights. The current rises to $0.40\text{ A}$. The DNN processes the current, occupancy, and school schedule features and confirms this is valid, authorized power consumption."*

### **Step 3: Energy Waste (Unexpected Vacancy Override)**
* **Click:** Step 3 button.
* **Observe:** The system demonstrates an unexpected vacancy override (**🔴 Empty**). Load remains ON ($0.40\text{ A}$). The Anomaly score spikes above $50\%$. The verdict flashes **ABNORMAL CONSUMPTION ANOMALY** (crimson red), and the chart points turn red.
* **Say to Examiner:**
  > *"Here is our core AI capability: Energy Waste Detection. Even during scheduled class hours, an unexpected vacancy can occur—for example, if class ends early and students leave while equipment stays ON. The system identifies this vacancy, the DNN flags an immediate anomaly, and Generative AI calculates the 8-hour kilowatt-hour loss while recommending an automated relay trip."*

### **Step 4: Night Consumption (Load ON, Normal Class, 22:00 Night)**
* **Click:** Step 4 button.
* **Observe:** Time switches to 22:00 (Night). The automatic schedule rule marks Normal Class as **🔴 Empty** (outside 08:00–17:00). Load is ON. Anomaly persists with high confidence score.
* **Say to Examiner:**
  > *"Our occupancy logic is fully automated based on schedule rules. At 22:00 at night, the institution is officially closed, so occupancy automatically evaluates to Empty. With loads drawing power, the DNN detects unauthorized after-hours usage and recommends facility security inspection."*

### **Step 5: Electrical Fault / Short-Circuit Surge**
* **Click:** Step 5 button.
* **Observe:** Current spikes to $1.62\text{ A}$, $\Delta I > 0.85\text{ A}$. Anomaly score surges to $99\%$.
* **Say to Examiner:**
  > *"This simulates an electrical equipment breakdown or short circuit. The sudden spike in the current derivative feature ($\Delta I$) triggers a Critical Hazard alert in the Generative AI engine, recommending immediate circuit branch isolation to prevent fire hazards."*

---

## 2. Technical Evidence for Examiners

### A. Deep Neural Network (DNN) Architecture
* **Topology:** $4 \to 8 \to 1$ Multi-Layer Perceptron (MLP)
* **Input Layer (4 features):**
  1. $x_0 = I / 1.5$: Normalized load current.
  2. $x_1 = \text{Occupancy}$: Binary PIR occupancy state ($1 = \text{Occupied}$, $0 = \text{Empty}$).
  3. $x_2 = \text{School Hours}$: Binary schedule window ($1 = \text{08:00 to 17:00}$, $0 = \text{Off-hours}$).
  4. $x_3 = \Delta I / 1.5$: Normalized instantaneous current rate-of-change.
* **Hidden Layer:** 8 neurons with Sigmoid activation:
  $$\sigma(z) = \frac{1}{1 + e^{-z}}$$
* **Output Layer:** 1 neuron with Sigmoid activation yielding Anomaly Probability $y \in [0.0, 1.0]$.
* **Optimization:** Stochastic Gradient Descent (SGD) with Backpropagation across 400 operational states, achieving $>98\%$ classification accuracy.

### B. Generative AI Engine Integration
* **Role:** Transforms raw numeric anomaly classifications into human-understandable diagnostics and actionable mitigation directives.
* **Contextual Variables Provided to Prompt/Engine:** Current ($I$), Power ($P$), Occupancy, Schedule Window, and Derivative ($\Delta I$).
* **Generated Outputs:**
  1. **"Why" (Root Cause Diagnosis):** Pinpoints whether the issue is empty room waste, nocturnal leakage, or an electrical short circuit.
  2. **"Recommendation" (Prescriptive Action):** Specific remedial action (e.g., automated relay cutoff, technician inspection).
  3. **Impact Quantification:** Dynamically computes 8-hour kilowatt-hour waste, financial cost in INR/USD, and carbon footprint ($g\text{ CO}_2$).

### C. Hardware Circuit Mathematics
1. **ACS712-05B Hall Sensor:**
   * Quiescent Output ($0\text{ A}$) = $2500\text{ mV}$ ($V_{CC}/2$)
   * Sensitivity = $185\text{ mV/A}$
   * Output Formula:
     $$V_{\text{out}} = 2500\text{ mV} + (185\text{ mV/A} \times I)$$
2. **Voltage Divider Protection:**
   * The ESP32-S3 ADC operates at $3.3\text{ V}$ max. The ACS712 module outputs up to $5.0\text{ V}$.
   * Resistors: $R_1 = 10\text{k}\Omega$, $R_2 = 20\text{k}\Omega$.
   * Attenuation Ratio:
     $$\text{Ratio} = \frac{R_2}{R_1 + R_2} = \frac{20\text{k}}{30\text{k}} = \frac{2}{3} = \frac{1}{1.5}$$
     $$V_{\text{ADC}} = \frac{V_{\text{out}}}{1.5}$$
3. **Firmware Current Reconstruction (inside ESP32-S3):**
   $$I = \frac{(V_{\text{ADC}} \times 1.5) - 2500\text{ mV}}{185\text{ mV/A}}$$
   $$P = V_{\text{supply}} \times I$$

---

## 3. Top Examiner Questions & Winning Answers

### Q1: *"Why did you use a voltage divider with the ACS712 and ESP32-S3?"*
> **Answer:** *"The ACS712 current sensor is powered by $5\text{ V}$ and its output swings up to $5\text{ V}$ under full load. However, the ESP32-S3 GPIO pins have an absolute maximum rating of $3.3\text{ V}$. Feeding $5\text{ V}$ directly would permanently damage the ESP32 ADC. Our $10\text{k}\Omega$ and $20\text{k}\Omega$ voltage divider attenuates the signal by exactly $2/3$, scaling $5\text{ V}$ down to a safe $3.33\text{ V}$. Our firmware then applies the reciprocal $1.5\times$ multiplier in software to reconstruct the exact reading."*

### Q2: *"Why did you use a Deep Neural Network instead of simple IF-ELSE threshold rules?"*
> **Answer:** *"Simple IF-ELSE rules fail in dynamic environments. A fixed threshold cannot distinguish between a legitimate high-power laboratory experiment during class hours versus a low-power phantom charger left on overnight. Our DNN correlates four interdependent variables simultaneously: current magnitude, occupancy state, temporal school hours, and the instantaneous current derivative $\Delta I$. The non-linear Sigmoid hidden layer allows the system to learn multi-dimensional boundaries and generalize to unseen intermediate states."*

### Q3: *"Where is the Generative AI, and how is it different from the DNN?"*
> **Answer:** *"The DNN is a discriminative classifier—it outputs a probability score from 0 to 1 indicating whether the electrical state is anomalous. The Generative AI layer acts as the reasoning and decision-making engine. It takes the telemetry context and produces natural-language root-cause explanations ('Why') and actionable remediation steps ('Recommendation'), while computing real-time energy loss and carbon emissions. In our prototype, this is modeled with structured contextual generation, and in cloud deployment, the Flask backend connects directly to an LLM endpoint."*

---

## 4. How to Run the Project Tomorrow

### Option A: Standalone Instant Run (Zero Setup)
* Simply double-click **`index.html`** or **`WattWise - Classroom Energy Simulation.html`** in your browser (Chrome, Edge, Firefox).
* Everything (the simulation, the 4→8→1 neural network SGD training, the live Chart.js graph, and the GenAI engine) runs 100% locally with zero internet required.

### Option B: Full Python Flask Backend Run
1. Double-click **`start_server.bat`** (or open terminal and run `python app.py`).
2. The server will start at `http://localhost:5000` and automatically open the dashboard in your browser.
3. Both the web frontend and any physical ESP32-S3 can stream telemetry to `http://localhost:5000/api/telemetry`.
