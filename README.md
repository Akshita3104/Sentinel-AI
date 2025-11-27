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

## ⚙️ System Architecture

```mermaid
flowchart TD
    %% Main Components
    subgraph Frontend["🖥️ Frontend (React)"]
        UI[Dashboard] <-->|WebSocket| BE
        UI -->|User Interaction| UI
    end

    subgraph Backend["⚙️ Backend (Node.js)"]
        BE[API Server] <-->|REST| ML
        BE -->|WebSocket| UI
    end

    subgraph ML_Service["🧠 ML Service (Flask)"]
        ML[ML API] <-->|Process| DB[(Model Data)]
        ML -->|Analyze| Stats[Traffic Stats]
    end

    subgraph SDN["🌐 SDN Network"]
        Ryu[Ryu Controller] <-->|OpenFlow| ML
        Ryu <-->|Flow Rules| Mininet[Mininet]
    end

    %% Data Flow
    Mininet -->|1. Traffic| Ryu
    Ryu -->|2. Flow Stats| ML
    ML -->|3. Analysis| BE
    BE -->|4. Updates| UI
    ML -->|5. Mitigation| Ryu
    Ryu -->|6. Apply Rules| Mininet

    %% Styling
    classDef frontend fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef backend fill:#e8f5e9,stroke#2e7d32,stroke-width:2px
    classDef ml fill#fff3e0,stroke#ef6c00,stroke-width:2px
    classDef sdn fill#f3e5f5,stroke#7b1fa2,stroke-width:2px
    
    class UI,Frontend frontend
    class BE,Backend backend
    class ML,ML_Service ml
    class Ryu,Mininet,SDN sdn
    linkStyle 5,6,7,8,9,10 stroke:#d32f2f,stroke-width:2px
```

### Component Interactions

1. **Frontend Layer**
   - Real-time dashboard with traffic visualization
   - Interactive controls for network management
   - Alert and notification system

2. **Backend Services**
   - Handles API requests and WebSocket connections
   - Manages data flow between components
   - Processes and forwards ML analysis results

3. **Machine Learning Service**
   - Processes network traffic data
   - Implements DDoS detection algorithms
   - Generates mitigation rules
   - Maintains model performance metrics

4. **SDN Infrastructure**
   - Ryu controller for network management
   - Mininet for network emulation
   - Dynamic flow rule management

### Data Flow Sequence

1. **Traffic Monitoring**
   - Mininet generates and forwards traffic
   - Ryu controller collects flow statistics
   - Stats are sent to ML service for analysis

2. **Threat Analysis**
   - ML model processes traffic patterns
   - Detects anomalies and potential attacks
   - Generates appropriate mitigation strategies

3. **Response & Mitigation**
   - Blocking rules are sent to Ryu
   - Flow tables are updated in real-time
   - Malicious traffic is filtered

4. **Visualization & Feedback**
   - Updates are pushed to the frontend
   - Administrators monitor system status
   - Manual intervention when necessary

## 🧠 Machine Learning Pipeline

```mermaid
graph TD
    A[Raw Traffic] --> B[Feature Extraction]
    B --> C[Preprocessing]
    C --> D[Model Inference]
    D --> E{Normal Traffic?}
    E -->|Yes| F[Allow Traffic]
    E -->|No| G[Generate Mitigation Rules]
    G --> H[Update SDN Rules]
```

### Key ML Components
- **Feature Extraction**: Network flow characteristics
- **Anomaly Detection**: Identifies suspicious patterns
- **Classification**: Categorizes attack types
- **Decision Making**: Determines appropriate responses

## 🧩 Key Features

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
graph LR
    A[Frontend] --> B[Backend]
    B --> C[ML Model]
    C --> D[SDN Controller]
    D --> E[Network Nodes]
    E --> A
```
- End-to-end automation
- Real-time feedback loop
- Scalable architecture

## 🚀 Installation

### 1️⃣ Clone Repository
```bash
git clone <https://github.com/Akshita3104/Sentinel-AI.git>
cd Sentinel-AI
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

## � Development Commands

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Start development server
nodemon index.js
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### ML Model Setup
```bash
# Navigate to model directory
cd model

# Install Python dependencies
pip install -r requirements.txt

# Start the ML API
python app/app.py
```

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
