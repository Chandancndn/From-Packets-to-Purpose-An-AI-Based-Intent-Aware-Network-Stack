"""
API endpoints for flow management.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.flow import (
    Flow,
    FlowCreate,
    FlowResponse,
    FlowStatistics,
    FlowUpdate,
    get_session_factory,
    init_db,
)

router = APIRouter(prefix="/api/flows", tags=["flows"])

# Initialize database
engine = init_db()
SessionLocal = get_session_factory(engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=List[FlowResponse])
async def list_flows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    min_confidence: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of network flows with optional filtering.
    """
    query = db.query(Flow)

    if category:
        query = query.filter(Flow.predicted_category == category)

    if min_confidence:
        query = query.filter(Flow.confidence_score >= min_confidence)

    flows = query.order_by(Flow.created_at.desc()).offset(skip).limit(limit).all()
    return flows


@router.get("/{flow_id}", response_model=FlowResponse)
async def get_flow(flow_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific flow.
    """
    flow = db.query(Flow).filter(Flow.id == flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return flow


@router.get("/stats/summary", response_model=FlowStatistics)
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get traffic statistics summary.
    """
    from sqlalchemy import func

    total = db.query(Flow).count()

    # Count by category
    category_counts = db.query(
        Flow.predicted_category,
        func.count(Flow.id)
    ).group_by(Flow.predicted_category).all()

    flows_by_category = {cat: count for cat, count in category_counts}

    # Average duration
    avg_duration = db.query(func.avg(Flow.duration_ms)).scalar() or 0.0

    # Total bytes and packets
    total_bytes = db.query(func.sum(Flow.byte_count)).scalar() or 0
    total_packets = db.query(func.sum(Flow.packet_count)).scalar() or 0

    return FlowStatistics(
        total_flows=total,
        flows_by_category=flows_by_category,
        avg_duration_ms=float(avg_duration),
        total_bytes=int(total_bytes),
        total_packets=int(total_packets),
    )


@router.post("", response_model=FlowResponse)
async def create_flow(flow: FlowCreate, db: Session = Depends(get_db)):
    """
    Create a new flow entry (typically called internally).
    """
    db_flow = Flow(**flow.dict())
    db.add(db_flow)
    db.commit()
    db.refresh(db_flow)
    return db_flow


@router.patch("/{flow_id}", response_model=FlowResponse)
async def update_flow(flow_id: int, flow_update: FlowUpdate, db: Session = Depends(get_db)):
    """
    Update flow classification and QoS settings.
    """
    db_flow = db.query(Flow).filter(Flow.id == flow_id).first()
    if not db_flow:
        raise HTTPException(status_code=404, detail="Flow not found")

    update_data = flow_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_flow, key, value)

    db.commit()
    db.refresh(db_flow)
    return db_flow


@router.delete("/{flow_id}")
async def delete_flow(flow_id: int, db: Session = Depends(get_db)):
    """
    Delete a flow entry.
    """
    db_flow = db.query(Flow).filter(Flow.id == flow_id).first()
    if not db_flow:
        raise HTTPException(status_code=404, detail="Flow not found")

    db.delete(db_flow)
    db.commit()
    return {"message": "Flow deleted successfully"}
