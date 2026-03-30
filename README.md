# 🚀 From Packets to Purpose: AI-Based Intent-Aware Network Stack

A modern, production-ready network traffic classification and management system that uses Machine Learning to intelligently classify network traffic into intent categories and dynamically apply QoS policies.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Modern%20Web%20Framework-green.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML%20Framework-orange.svg)

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Screenshots](#screenshots)

## ✨ Features

### 🔍 Traffic Analysis
- **Real-time Packet Capture** using Tshark and Scapy
- **Flow-level Feature Extraction** (packet size, inter-arrival time, duration, etc.)
- **Deep Packet Inspection** for encrypted traffic analysis

### 🤖 AI-Powered Classification
- **Four Intent Categories:**
  - 🟢 **Interactive** (Video calls, VoIP, Gaming) - Highest Priority
  - 🔵 **Streaming** (Video streaming, Music) - Medium Priority
  - 🟡 **Background** (Downloads, Updates) - Low Priority
  - 🔴 **Malicious** (Threats, Attacks) - Blocked/Isolated
- **Machine Learning Models:** Random Forest, Gradient Boosting
- **Real-time Prediction** with sub-millisecond latency

### ⚡ Dynamic QoS Management
- **Automatic Priority Assignment** based on predicted intent
- **Linux Traffic Control (tc) Integration** for bandwidth shaping
- **Queue Management** with HTB (Hierarchical Token Bucket)
- **Latency & Throughput Optimization**

### 🎨 Modern Web Dashboard
- **Real-time Traffic Visualization** with WebSocket
- **Live Flow Monitoring** with filtering and search
- **Performance Metrics & Analytics**
- **Alert System** for malicious traffic detection
- **Dark/Light Theme Support**

### 🧪 Simulation Environment
- **Mininet Network Emulator** integration
- **Custom Topology Generation**
- **Traffic Generation** with Iperf3
- **Controlled Testing Scenarios**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        WEB DASHBOARD                             │
│                      (React + WebSocket)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/WebSocket
┌────────────────────────────▼────────────────────────────────────┐
│                      API SERVER                                  │
│                    (FastAPI + Uvicorn)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌──────▼──────┐
│  ML Prediction │  │  Network Capture  │  │   QoS       │
│   Pipeline     │  │   (Scapy/Tshark)  │  │  Manager    │
└────────────────┘  └──────────────────┘  └─────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Database      │
                    │  (PostgreSQL)   │
                    └─────────────────┘
```

## 🚀 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- Wireshark/Tshark
- Linux (for QoS features)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/intent-aware-network-stack.git
cd intent-aware-network-stack

# Run the setup script
chmod +x setup.sh
./setup.sh

# Start all services
docker-compose up -d

# Or run locally
make dev
```

### Manual Installation

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📊 Usage

### 1. Start the System
```bash
# Start backend
python backend/main.py

# Start frontend
npm run dev --prefix frontend
```

### 2. Access the Dashboard
Open your browser and navigate to `http://localhost:5173`

### 3. Configure Network Capture
- Select network interface
- Set capture filters
- Configure flow aggregation settings

### 4. Monitor Traffic
- View real-time flow classification
- Analyze traffic patterns
- Receive alerts for malicious activity

### 5. Manage QoS Policies
- Customize priority levels
- Set bandwidth limits
- Configure queue management

## 📁 Project Structure

```
intent-aware-network-stack/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── api/
│   │   │   ├── flows.py         # Flow management endpoints
│   │   │   ├── prediction.py    # ML prediction endpoints
│   │   │   ├── qos.py           # QoS management endpoints
│   │   │   └── websocket.py     # Real-time updates
│   │   ├── core/
│   │   │   ├── capture.py       # Packet capture engine
│   │   │   ├── features.py      # Feature extraction
│   │   │   ├── classifier.py    # ML classifier
│   │   │   └── qos_manager.py   # QoS policy manager
│   │   ├── models/
│   │   │   └── flow.py          # Database models
│   │   └── ml/
│   │       ├── train.py         # Model training
│   │       ├── predict.py       # Inference pipeline
│   │       └── models/          # Saved model files
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── FlowTable.tsx
│   │   │   ├── TrafficChart.tsx
│   │   │   ├── QOSPanel.tsx
│   │   │   └── AlertPanel.tsx
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── mininet/
│   ├── topologies/
│   └── traffic_generator.py
├── models/
│   └── trained_models/
├── tests/
├── docker-compose.yml
├── Makefile
└── setup.sh
```

## 📡 API Documentation

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/flows` | Get all traffic flows |
| GET | `/api/flows/{id}` | Get specific flow details |
| POST | `/api/flows/classify` | Classify a flow |
| GET | `/api/stats` | Get system statistics |
| POST | `/api/qos/policy` | Create QoS policy |
| GET | `/api/qos/policies` | List QoS policies |

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `flow_update` | Server → Client | New flow detected |
| `classification_result` | Server → Client | Classification complete |
| `alert` | Server → Client | Security alert |

## 🖼️ Screenshots

### Real-time Dashboard
![Dashboard](docs/images/dashboard.png)

### Flow Classification
![Classification](docs/images/classification.png)

### QoS Management
![QoS](docs/images/qos.png)

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run Mininet simulation
cd mininet
sudo python topology.py
```

## 🔒 Security Features

- Input validation and sanitization
- Rate limiting on API endpoints
- CORS configuration
- Malicious traffic detection and blocking
- Audit logging

## 📝 License

This project is licensed under the MIT License.

## 👥 Contributors

- Kritika [1SI23CI065]
- Monisha
- Chetan Kumar
- K Chandan Jayasimha

**Guide:** Dr. Savithramma R M, Assistant Professor

**Institution:** Siddaganga Institute of Technology, Tumkur

---

<p align="center">Made with ❤️ for Major Project Review</p>
