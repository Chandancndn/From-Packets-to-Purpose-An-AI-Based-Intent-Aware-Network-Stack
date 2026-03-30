"""
Main FastAPI application for Intent-Aware Network Stack.
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.flows import router as flows_router
from app.api.prediction import router as prediction_router
from app.api.qos import router as qos_router
from app.api.websocket import router as websocket_router
from app.api.websocket import broadcast_classification, broadcast_flow_update, broadcast_alert
from app.core.capture import PacketCaptureEngine, SimulatedCaptureEngine
from app.core.qos_manager import QoSManager, SimulatedQoSManager
from app.ml.predict import predict_intent, get_priority_level, get_bandwidth_allocation
from app.models.flow import Flow, init_db, get_session_factory, IntentCategory
import time

# Global capture engine
capture_engine = None

# Database
engine = init_db()
SessionLocal = get_session_factory(engine)


async def process_flow(flow_data: dict):
    """Process detected flow: classify and apply QoS."""
    try:
        # Add to database
        db = SessionLocal()
        try:
            # Calculate flow duration
            duration_ms = flow_data.get("duration_ms", 0)

            # Create flow record
            db_flow = Flow(
                src_ip=flow_data["src_ip"],
                dst_ip=flow_data["dst_ip"],
                src_port=flow_data.get("src_port"),
                dst_port=flow_data.get("dst_port"),
                protocol=flow_data["protocol"],
                packet_count=flow_data["packet_count"],
                byte_count=flow_data["byte_count"],
                duration_ms=duration_ms,
                avg_packet_size=sum(flow_data.get("packet_sizes", [0])) / max(len(flow_data.get("packet_sizes", [1])), 1),
                packets_per_second=flow_data.get("packets_per_second", 0),
                bytes_per_second=flow_data.get("bytes_per_second", 0),
            )
            db.add(db_flow)
            db.commit()
            db.refresh(db_flow)

            # Classify flow
            category, confidence, probabilities = predict_intent(flow_data)

            # Update with classification
            db_flow.predicted_category = category
            db_flow.confidence_score = confidence
            db_flow.is_classified = 1
            db_flow.priority_level = get_priority_level(category)
            db.commit()

            # Broadcast to WebSocket clients
            await broadcast_flow_update({
                "id": db_flow.id,
                "src_ip": db_flow.src_ip,
                "dst_ip": db_flow.dst_ip,
                "src_port": db_flow.src_port,
                "dst_port": db_flow.dst_port,
                "protocol": db_flow.protocol,
                "packet_count": db_flow.packet_count,
                "byte_count": db_flow.byte_count,
                "category": category,
                "confidence": confidence,
                "priority_level": db_flow.priority_level,
                "created_at": db_flow.created_at.isoformat()
            })

            await broadcast_classification(db_flow.id, category, confidence)

            # Alert for malicious traffic
            if category == "malicious":
                await broadcast_alert(
                    "malicious_traffic",
                    f"Detected malicious traffic from {db_flow.src_ip} to {db_flow.dst_ip}",
                    "critical"
                )

            # Apply QoS policy
            try:
                from app.api.qos import qos_manager
                flow_id = f"flow_{db_flow.id}"
                qos_manager.apply_policy(
                    flow_id=flow_id,
                    category=category,
                    src_ip=db_flow.src_ip,
                    dst_ip=db_flow.dst_ip,
                    src_port=db_flow.src_port,
                    dst_port=db_flow.dst_port
                )
            except Exception as e:
                print(f"QoS policy error: {e}")

        finally:
            db.close()

    except Exception as e:
        print(f"Error processing flow: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    global capture_engine

    # Startup
    print("Starting Intent-Aware Network Stack...")

    # Initialize ML model
    print("Initializing ML classifier...")
    from app.ml.classifier import TrafficClassifier, create_sample_training_data
    classifier = TrafficClassifier()
    if not classifier.is_ready():
        print("Training initial model...")
        X, y = create_sample_training_data()
        classifier.train(X, y)

    # Start capture engine (use simulated for development)
    print("Starting packet capture engine...")
    try:
        # Try real capture first
        capture_engine = PacketCaptureEngine(on_flow_detected=process_flow)
        if capture_engine.start():
            print("Real packet capture started")
        else:
            raise Exception("Failed to start capture")
    except Exception as e:
        print(f"Using simulated capture: {e}")
        capture_engine = SimulatedCaptureEngine(on_flow_detected=process_flow)
        capture_engine.start()

    # Start background tasks
    asyncio.create_task(stats_broadcast_task())

    yield

    # Shutdown
    print("Shutting down...")
    if capture_engine:
        capture_engine.stop()


async def stats_broadcast_task():
    """Broadcast statistics periodically."""
    from app.api.websocket import broadcast_stats

    while True:
        await asyncio.sleep(5)  # Every 5 seconds
        try:
            if capture_engine:
                stats = capture_engine.get_statistics()
                await broadcast_stats(stats)
        except Exception as e:
            print(f"Stats broadcast error: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Based Intent-Aware Network Stack API",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(flows_router)
app.include_router(prediction_router)
app.include_router(qos_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    capture_status = capture_engine.get_statistics() if capture_engine else {"is_capturing": False}

    return {
        "status": "healthy",
        "capture_engine": capture_status,
        "ml_model": {
            "is_ready": True  # TODO: Check actual status
        }
    }


@app.get("/api/interfaces")
async def get_interfaces():
    """Get available network interfaces."""
    if capture_engine:
        return {"interfaces": capture_engine.get_interfaces()}
    return {"interfaces": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
