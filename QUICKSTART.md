# 🚀 Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies

```bash
# Install Python 3.9+ and Node.js 18+ first
# Then run:

chmod +x setup.sh
./setup.sh
```

### Step 2: Start the Backend

```bash
cd backend
source venv/bin/activate
python -m app.main
```

You should see:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
Starting Intent-Aware Network Stack...
Initializing ML classifier...
Training initial model...
Starting packet capture engine...
Using simulated capture
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Start the Frontend

In a **new terminal**:

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 4: Open Dashboard

Open your browser and go to: **http://localhost:5173**

You should see the Intent-Aware Network Stack dashboard!

---

## 🎯 What You'll See

### Initial State
- Dashboard with 4 statistic cards (all showing 0)
- Empty flow table
- Empty traffic distribution chart
- "No security alerts" message

### After ~10 Seconds
- Simulated traffic starts appearing
- Flows appear in the table with categories
- Traffic distribution chart shows data
- Statistics update in real-time

### Example Flow Entry
```
Category: Interactive (green icon)
Source: 192.168.1.11:52145 → Destination: 13.107.42.14:443
Protocol: TCP
Size: 45.2 KB (78 packets)
Confidence: 94%
Time: 10:23:45 AM
```

---

## 🧪 Testing the System

### 1. View API Documentation
Open: **http://localhost:8000/docs**

This shows all available API endpoints with interactive testing.

### 2. Test Classification API

```bash
# Test with a sample flow
curl -X POST http://localhost:8000/api/prediction/classify \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.1.10",
    "dst_ip": "8.8.8.8",
    "src_port": 54321,
    "dst_port": 443,
    "protocol": "TCP",
    "packet_count": 150,
    "byte_count": 75000,
    "packet_sizes": [500, 520, 480, ...],
    "inter_arrival_times": [0.01, 0.02, 0.015, ...]
  }'
```

Expected response:
```json
{
  "category": "interactive",
  "confidence": 0.92,
  "probabilities": {
    "interactive": 0.92,
    "streaming": 0.05,
    "background": 0.02,
    "malicious": 0.01
  },
  "priority_level": 1
}
```

### 3. Check QoS Status

```bash
curl http://localhost:8000/api/qos/status
```

---

## 🔧 Common Issues

### Issue 1: "Port already in use"
**Fix:** Kill existing processes
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

### Issue 2: "Module not found"
**Fix:** Reinstall dependencies
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm install
```

### Issue 3: "Permission denied" for packet capture
**Fix:** Run with sudo (Linux) or use simulated capture
```bash
# Option 1: Use simulated capture (default)
# No action needed - it auto-falls back

# Option 2: Run with sudo (Linux only)
sudo python -m app.main
```

---

## 🐳 Docker Quick Start

```bash
# Start everything with Docker
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Access services
# Backend: http://localhost:8000
# Frontend: http://localhost:5173

# Stop everything
docker-compose down
```

---

## 📊 Understanding the Dashboard

### 1. Header Section
- **Green "Live" indicator**: WebSocket connected
- **Blue "Monitoring"**: Packet capture active

### 2. Statistics Cards
- **Total Flows**: Number of flows captured
- **Traffic Volume**: Total bytes transferred
- **Active Connections**: Currently tracked flows
- **Threats Blocked**: Malicious flows detected

### 3. Flow Table
Shows recent network flows with:
- **Category badge**: Color-coded (green/blue/yellow/red)
- **IP addresses**: Source → Destination
- **Protocol**: TCP/UDP/ICMP
- **Size**: Byte and packet count
- **Confidence**: ML prediction confidence

### 4. Traffic Distribution
Pie chart showing percentage of each traffic category.

### 5. Security Alerts
Red boxes appear when malicious traffic is detected.

---

## 🎓 Try These Experiments

### Experiment 1: Watch Traffic Classification
1. Open the dashboard
2. Wait 30 seconds
3. Observe different categories appearing
4. Click on different category badges

### Experiment 2: Test QoS Policies
```bash
# Check current QoS configuration
curl http://localhost:8000/api/qos/config

# Initialize QoS (if not already running)
curl -X POST http://localhost:8000/api/qos/initialize
```

### Experiment 3: Train New Model
```bash
# Trigger model retraining
curl -X POST http://localhost:8000/api/prediction/model/train
```

---

## 🔄 Development Workflow

### Making Changes to Backend
```bash
cd backend
# Edit files...
# Server auto-reloads on save (if using --reload)
```

### Making Changes to Frontend
```bash
cd frontend
# Edit files...
# Browser auto-refreshes on save
```

### Adding New Features
1. Add API endpoint in `backend/app/api/`
2. Add frontend component in `frontend/src/components/`
3. Connect with API service in `frontend/src/services/api.ts`
4. Test in browser

---

## 🛑 Stopping the System

### If running manually:
- **Backend**: Press `Ctrl+C` in backend terminal
- **Frontend**: Press `Ctrl+C` in frontend terminal

### If running with Docker:
```bash
docker-compose down
```

---

## 📞 Need Help?

1. **Check logs** for error messages
2. **Review** PROJECT_EXPLANATION.md for details
3. **Check** README.md for architecture info

---

**Happy Monitoring! 🎉**