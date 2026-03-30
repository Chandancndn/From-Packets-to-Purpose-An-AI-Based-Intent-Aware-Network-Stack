"""
API endpoints for QoS management.
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.config import settings
from app.core.qos_manager import QoSManager, SimulatedQoSManager

router = APIRouter(prefix="/api/qos", tags=["qos"])

# Initialize QoS manager (use simulated for development)
try:
    qos_manager = QoSManager()
    if not qos_manager.initialize():
        print("Using simulated QoS manager")
        qos_manager = SimulatedQoSManager()
        qos_manager.initialize()
except Exception:
    qos_manager = SimulatedQoSManager()
    qos_manager.initialize()


class QoSPolicyRequest(BaseModel):
    """QoS policy request."""
    flow_id: str
    category: str
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None


class QoSConfig(BaseModel):
    """QoS configuration."""
    bandwidth_mbps: int
    queue_limit: int
    enabled: bool


@router.get("/status")
async def get_qos_status():
    """
    Get QoS subsystem status.
    """
    return qos_manager.get_statistics()


@router.post("/policy")
async def create_policy(policy: QoSPolicyRequest):
    """
    Apply QoS policy to a flow.
    """
    success = qos_manager.apply_policy(
        flow_id=policy.flow_id,
        category=policy.category,
        src_ip=policy.src_ip,
        dst_ip=policy.dst_ip,
        src_port=policy.src_port,
        dst_port=policy.dst_port
    )

    if success:
        return {
            "status": "success",
            "message": f"QoS policy applied for {policy.category} traffic",
            "priority": settings.PRIORITY_LEVELS.get(policy.category, 3),
            "bandwidth_allocation": settings.BANDWIDTH_ALLOCATION.get(policy.category, 10)
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to apply QoS policy")


@router.delete("/policy/{flow_id}")
async def remove_policy(flow_id: str):
    """
    Remove QoS policy for a flow.
    """
    success = qos_manager.remove_policy(flow_id)
    if success:
        return {"status": "success", "message": "Policy removed"}
    else:
        raise HTTPException(status_code=404, detail="Policy not found")


@router.get("/policies")
async def list_policies():
    """
    List active QoS policies.
    """
    stats = qos_manager.get_statistics()
    return {
        "active_policies": stats.get("policies", []),
        "total_policies": stats.get("active_policies", 0)
    }


@router.post("/initialize")
async def initialize_qos():
    """
    Initialize QoS subsystem.
    """
    success = qos_manager.initialize()
    if success:
        return {"status": "success", "message": "QoS initialized"}
    else:
        raise HTTPException(status_code=500, detail="Failed to initialize QoS")


@router.post("/cleanup")
async def cleanup_qos():
    """
    Clean up all QoS rules.
    """
    success = qos_manager.cleanup()
    if success:
        return {"status": "success", "message": "QoS rules cleaned up"}
    else:
        raise HTTPException(status_code=500, detail="Failed to cleanup QoS")


@router.get("/config")
async def get_qos_config():
    """
    Get QoS configuration.
    """
    return {
        "enabled": settings.QOS_ENABLED,
        "total_bandwidth_mbps": settings.DEFAULT_BANDWIDTH_Mbps,
        "categories": settings.CATEGORIES,
        "priority_levels": settings.PRIORITY_LEVELS,
        "bandwidth_allocation": settings.BANDWIDTH_ALLOCATION
    }


@router.post("/config")
async def update_qos_config(config: QoSConfig):
    """
    Update QoS configuration.
    """
    # Note: In production, persist to database
    settings.DEFAULT_BANDWIDTH_Mbps = config.bandwidth_mbps
    settings.QOS_ENABLED = config.enabled

    return {
        "status": "success",
        "config": {
            "bandwidth_mbps": settings.DEFAULT_BANDWIDTH_Mbps,
            "enabled": settings.QOS_ENABLED
        }
    }
