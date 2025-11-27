# 🛡️ Sentinel AI – SDN Powered AI-Based DDoS Detection & Mitigation System

A complete end-to-end platform for real-time DDoS detection, SDN-based mitigation, and live traffic visualization, integrating:

- **React** (Frontend Dashboard)
- **Node.js** (Backend Layer + WebSockets)
- **Python Flask** (ML Detection API + SDN Controller Integration)
- **Ryu Controller + Mininet** (SDN Emulation)
- **Locust Load Testing** (DDoS Simulation)

Sentinel AI is designed for 5G and SDN-enabled networks, supporting real-time analytics, anomaly detection, auto-mitigation, and network slicing.

## 📁 Project Folder Structure

```
Sentinel-AI/
│
├── backend/
│   ├── controllers/
│   ├── middleware/
│   ├── routes/
│   ├── socket/
│   ├── tests/
│   ├── utils/
│   ├── .env
│   ├── index.js
│   └── package.json
│
├── frontend/
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── App.jsx / App.tsx
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── package.json
│
├── model/
│   ├── app/
│   │   ├── app.py
│   │   ├── feature_extraction.py
│   │   ├── flow_capture.py
│   │   ├── mitigation_engine.py
│   │   ├── ml_detection.py
│   │   ├── network_slicing.py
│   │   ├── performance_cache.py
│   │   ├── sdn_controller.py
│   │   └── test/
│   ├── models/
│   ├── README.md
│   └── requirements.txt
│
└── Testing/
    ├── locustfile.py
    └── __pycache__/
```

# Sentinel-AI: Intelligent DDoS Detection & Mitigation Platform

## 1. Overview
A real-time, AI-powered SDN security platform for DDoS detection and mitigation using ML and programmable networking.

## 2. System Architecture

### 2.1 Architecture Diagram
```mermaid
flowchart LR
    UI["React Dashboard"] -- Request Traffic Capture --> BE["Node.js Backend"]
    BE -- Forward Request --> ML["ML Service (Flask)"]
    ML -- Capture Traffic (scapy/tshark) --> ML
    ML -- Normal Traffic Detected --> BE
    BE -- Respond to Frontend --> UI
    ML -- Malicious Traffic Detected --> Ryu["Ryu Controller"]
    ML -- Forward Traffic (malicious) --> Ryu
    Ryu -- Block Traffic --> Mininet["Mininet Network"]
    Ryu -- Response to Model --> ML
    ML -- Forward Mitigation Result --> BE
    BE -- Respond to Frontend --> UI
```

### 2.2 Component Interactions
1. **Frontend (React Dashboard)**
   - Sends request to start traffic capture to backend
   - Receives and displays detection and mitigation results
   - Visualizes real-time network traffic
   - Displays detection results and mitigation alerts

2. **Backend (Node.js)**
   - Forwards traffic capture request from frontend to ML Service
   - Receives detection/mitigation results from ML Service
   - Responds to frontend with analysis/mitigation status

3. **ML Service (Flask)**
   - Captures traffic using scapy/tshark upon backend request
   - Analyzes captured traffic for normal/malicious patterns
   - If normal, sends result to backend
   - If malicious, forwards malicious traffic to Ryu Controller via Mininet
   - Receives mitigation response from Ryu Controller
   - Forwards mitigation result to backend

4. **Ryu Controller (SDN)**
   - Receives malicious traffic from ML Service via Mininet
   - Blocks malicious traffic in Mininet
   - Sends mitigation response/status to ML Service

5. **Mininet Network**
   - Emulates SDN environment
   - Applies flow rules to block malicious traffic

### 2.3 Data workflow
   - Frontend sends a request for traffic capture to the backend.
   - Backend forwards the request to the ML Service.
   - ML Service captures traffic using scapy/tshark and analyzes it.
   - If traffic is normal:
     - ML Service sends the result to backend.
     - Backend responds to frontend with normal status.
   - If malicious traffic is detected:
     - ML Service forwards the malicious traffic to the Ryu Controller via Mininet.
     - Ryu blocks the traffic in Mininet and sends a response back to the ML Service.
     - ML Service forwards the mitigation response to backend.
     - Backend responds to frontend with mitigation status/result.

### 2.4 Machine Learning Pipeline
```mermaid
graph TD
    A[Capture Traffic (scapy/tshark)] --> B[Feature Extraction]
    B --> C[Preprocessing]
    C --> D[Model Inference]
    D --> E{Normal Traffic?}
    E -->|Yes| F[Send Result to Backend]
    E -->|No| G[Send Traffic to SDN Controller]
    G --> H[Receive Mitigation Response]
    H --> I[Forward Response to Backend]
```

### Key ML Components
- **Traffic Capture**: Uses scapy/tshark to capture network packets
- **Feature Extraction**: Extracts relevant flow characteristics
- **Anomaly Detection**: Identifies suspicious/malicious patterns
- **Classification**: Categorizes traffic as normal or malicious
- **Mitigation Handling**: Forwards malicious traffic to SDN Controller via Mininet, receives mitigation response, and forwards result to backend

## 3. Key Features
- Real-time DDoS detection & mitigation
- AI-driven traffic analysis
- SDN-based programmable defense
- Live dashboard & alerts
- End-to-end automation
- Feedback loop & scalable design

## 4. Simulation & Testing
### 4.1 DDoS Simulation
- Locust-based traffic generator
- Custom attack scenarios
- Real-time impact analysis


## 5. Installation & Setup
### 5.1 Clone Repository
```bash
git clone <https://github.com/Akshita3104/Sentinel-AI.git>
cd Sentinel-AI
```
### 5.2 Terminal Setup Overview
```mermaid
graph TD
    A[Terminal 1: Ryu Controller] --> B[Terminal 2: Mininet]
    B --> C[Terminal 3: ML API]
    C --> D[Terminal 4: Node Backend]
    D --> E[Terminal 5: React Frontend]
```
#### Terminal 1 — Start Ryu SDN Controller
```bash
# Example command
```
#### Terminal 2 — Start Mininet
```bash
# Example command
```
#### Terminal 3 — Start ML API
```bash
# Example command
```
#### Terminal 4 — Start Backend
```bash
# Example command
```
#### Terminal 5 — Start React Dashboard
```bash
cd frontend
npm install
npm run dev
```
Dashboard: [http://localhost:5173](http://localhost:5173)

## 6. Troubleshooting
### Clean Mininet Environment
```bash
sudo mn -c
```

### Kill Blocked Ports
```bash
sudo fuser -k 6633/tcp
sudo fuser -k 8080/tcp
sudo fuser -k 5001/tcp
```

### 🔍 AI-Powered DDoS Detection
```mermaid
pie
    title Detection Components
    "Feature Extraction" : 35
    "ML Classification" : 45
    "Anomaly Detection" : 20
```
- Machine Learning classifier (Random Forest / Sklearn)
- Real-time feature extraction
- Flow-based detection

### 📡 SDN-Controlled Mitigation
- Ryu + OpenFlow 1.3
- Dynamic blocking of malicious IPs
- Flow-table manipulation

### 📊 Live Dashboard
- Real-time traffic visualization
- Threat alerts and notifications
- Flow table monitoring
- Network slice analytics (eMBB, URLLC, mMTC)

### 🔥 DDoS Simulation
- Locust-based traffic generator
- Custom attack scenarios
- Real-time impact analysis

### 🧪 Full Integration Pipeline
```mermaid
flowchart LR
    UI["Frontend"] -- Request Capture --> BE["Backend"]
    BE -- Forward Request --> ML["ML Model"]
    ML -- Capture & Analyze --> ML
    ML -- Normal --> BE
    BE -- Result --> UI
    ML -- Malicious --> SDN["SDN Controller"]
    SDN -- Block/Respond --> ML
    ML -- Mitigation Result --> BE
    BE -- Result --> UI
```
- End-to-end automation
- Real-time feedback loop
- Scalable architecture

```

## 🖥 Running the Entire Workflow (5-Terminal Setup)

This is the correct & final execution order.

### Terminal Setup Overview

```mermaid
graph TD
    A[Terminal 1: Ryu Controller] --> B[Terminal 2: Mininet]
    B --> C[Terminal 3: ML API]
    C --> D[Terminal 4: Node Backend]
    D --> E[Terminal 5: React Frontend]
```

### ▶ Terminal 1 — Start Ryu SDN Controller

```bash
# Connect to Mininet VM
ssh mininet@192.168.56.101

# Start Ryu Controller
ryu-manager ryu.app.simple_switch_13 ryu.app.ofctl_rest
```

### ▶ Terminal 2 — Start Mininet Topology

```bash
# Connect to Mininet VM
ssh mininet@192.168.56.101

# Start Mininet with custom topology
sudo mn --topo single,3 --mac --switch ovsk \
--controller=remote,ip=127.0.0.1,port=6633

# Test network connectivity
pingall
```

### ▶ Terminal 3 — Start ML Detection API

```bash
# Navigate to ML application
cd model/app

# Start the Flask API
python app.py
```

> **API Documentation**: [http://127.0.0.1:5001](http://127.0.0.1:5001)

### ▶ Terminal 4 — Start Node Backend

```bash
# Navigate to backend directory
cd backend

# Start the Node.js server
nodemon index.js
```

> **Backend API**: [http://localhost:3000](http://localhost:3000)

### ▶ Terminal 5 — Start React Dashboard

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

> **Dashboard URL**: [http://localhost:5173](http://localhost:5173)

## 💣 DDoS Attack Simulation

### Launching the Attack

```bash
# Navigate to testing directory
cd Testing

# Start Locust with the test scenario
locust -f locustfile.py
```

### Accessing Locust Web Interface
Open your browser and navigate to: [http://localhost:8089](http://localhost:8089)

### Configuring the Attack
1. **Number of users**: Total concurrent users
2. **Spawn rate**: Users spawned per second
3. **Host**: `http://<your-backend-address>:3000`

### Monitoring the Attack
```bash
# Check SDN switch flow table (in a new terminal)
curl http://127.0.0.1:8080/stats/flow/1 | python -m json.tool
```

### Attack Workflow

```mermaid
sequenceDiagram
    participant M as Mininet
    participant R as Ryu Controller
    participant F as Flask API
    participant ML as ML Model
    participant N as Node Backend
    participant D as Dashboard

    M->>R: Network Traffic
    R->>F: Flow Statistics
    F->>ML: Processed Data
    ML-->>F: Attack Detection
    F->>R: Mitigation Rules
    F->>N: Alert Updates
    N->>D: Real-time Visualization
```

### Expected Outcomes
- Real-time attack detection in the dashboard
- Automatic mitigation through SDN rules
- Visual representation of attack patterns
- Performance metrics and system health monitoring
4. If attack:
       - mitigation_engine.py triggers SDN rules
5. Flask notifies Node backend
6. Backend pushes live alerts → Frontend (Socket.IO)
7. Dashboard updates traffic charts + alerts


Everything works in a continuous real-time feedback loop.

## 🚨 Troubleshooting

### Clean Mininet Environment
```bash
# Clear Mininet configuration
sudo mn -c
```

### Kill Blocked Ports
```bash
# Kill processes on commonly used ports
sudo fuser -k 6633/tcp  # OpenFlow
sudo fuser -k 8080/tcp  # Ryu Web Interface
sudo fuser -k 5001/tcp  # Flask API
```

### Common Issues
- **Port already in use**: Use the kill commands above
- **Permission denied**: Prepend commands with `sudo` if needed
- **Dependency issues**: 
  ```bash
  # For Node.js
  rm -rf node_modules package-lock.json
  npm cache clean --force
  npm install
  
  # For Python
  pip freeze > requirements.txt
  pip install -r requirements.txt --upgrade
  ```

### System Requirements
- Node.js v14+
- Python 3.8+
- Mininet 2.3+
- Ryu 4.34+
