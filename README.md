Sentinel AI – SDN Powered AI-Based DDoS Detection & Mitigation System

A complete end-to-end platform for real-time DDoS detection, SDN-based mitigation, and live traffic visualization, integrating:

React (Frontend Dashboard)

Node.js (Backend Layer + WebSockets)

Python Flask (ML Detection API + SDN Controller Integration)

Ryu Controller + Mininet (SDN Emulation)

Locust Load Testing (DDoS Simulation)

Sentinel AI is designed for 5G and SDN-enabled networks, supporting real-time analytics, anomaly detection, auto-mitigation, and network slicing.

📁 Project Folder Structure
Ly-Project/
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

⚙️ System Architecture Overview
┌──────────┐       ┌────────────┐       ┌─────────────┐       ┌─────────────┐
│ Mininet  │ ───▶  │ Ryu SDN    │ ───▶  │ Flask ML     │ ───▶  │ Node Backend │ ───▶ React UI
└──────────┘       │ Controller │       │ API + SDN     │       │ (Socket.IO)  │
                   └────────────┘       │ Controls      │       └─────────────┘
                                          └─────────────┘

Flow Explanation

Traffic packets generated inside Mininet topology

Ryu controller pushes flow stats to Flask API

ML Model analyses & detects anomalies

If attack detected → mitigation engine triggers SDN rules

Node backend receives updates via Python API

Frontend dashboard updates in real-time via WebSockets

🧩 Key Features
🔍 AI-Powered DDoS Detection

Machine Learning classifier (Random Forest / Sklearn)

Real-time feature extraction

Flow-based detection

📡 SDN-Controlled Mitigation

Ryu + OpenFlow 1.3

Dynamic blocking of malicious IPs

Flow-table manipulation

📊 Live Dashboard

Traffic charts

Threat alerts

Flow table logs

Slice-specific data (eMBB, URLLC, mMTC)

🔥 DDoS Simulation

Locust traffic generator

Custom attack scenarios

🧪 Full Integration Pipeline

Frontend → Backend → Model → SDN → Nodes

Fully automated loop

🚀 Installation
1️⃣ Clone Repository
git clone <your-repository-url>
cd Ly-Project

🖥 Running the Entire Workflow (5-Terminal Setup)

This is the correct & final execution order.

▶ Terminal 1 — Start Ryu SDN Controller

Inside Mininet VM:

ssh mininet@192.168.56.101
ryu-manager ryu.app.simple_switch_13 ryu.app.ofctl_rest

▶ Terminal 2 — Start Mininet Topology
ssh mininet@192.168.56.101

sudo mn --topo single,3 --mac --switch ovsk \
--controller=remote,ip=127.0.0.1,port=6633


Test connectivity:

pingall

▶ Terminal 3 — Start Python ML Detection API

On your host machine:

cd model/app
python app.py


This runs at:

http://127.0.0.1:5001

▶ Terminal 4 — Start Node Backend
cd backend
nodemon index.js


Runs at:

http://localhost:3000

▶ Terminal 5 — Start React Frontend Dashboard
cd frontend
npm run dev


Open browser:

http://localhost:5173

💣 Simulating a DDoS Attack (Optional)
cd Testing
locust -f locustfile.py


Open Locust UI:

http://localhost:8089


Enter:

Number of users

Spawn rate

Target host (backend API)

Start attack → watch real-time detection in dashboard 🎯

🔍 Optional: Check SDN Switch Flow Table
curl http://127.0.0.1:8080/stats/flow/1

🧠 Internal Workflow (Detailed)
1. Mininet sends traffic → Ryu controller  
2. Ryu exposes OpenFlow stats → Flask API  
3. Flask extracts features → ML model predicts attack  
4. If attack:
       - mitigation_engine.py triggers SDN rules
5. Flask notifies Node backend
6. Backend pushes live alerts → Frontend (Socket.IO)
7. Dashboard updates traffic charts + alerts


Everything works in a continuous real-time feedback loop.

👨‍💻 Development Commands
Backend
cd backend
npm install
nodemon index.js

Frontend
cd frontend
npm install
npm run dev

Model
cd model
pip install -r requirements.txt
python app/app.py

🧪 Troubleshooting
Clean Mininet
sudo mn -c

Kill blocked ports
sudo fuser -k 6633/tcp
sudo fuser -k 8080/tcp
sudo fuser -k 5001/tcp
