"""
Database models for network flows.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

Base = declarative_base()


class IntentCategory(str, Enum):
    """Traffic intent categories."""
    INTERACTIVE = "interactive"
    STREAMING = "streaming"
    BACKGROUND = "background"
    MALICIOUS = "malicious"
    UNKNOWN = "unknown"


class Flow(Base):
    """Database model for network flows."""
    __tablename__ = "flows"

    id = Column(Integer, primary_key=True, index=True)

    # Flow identifiers
    src_ip = Column(String(45), nullable=False, index=True)
    dst_ip = Column(String(45), nullable=False, index=True)
    src_port = Column(Integer, nullable=True)
    dst_port = Column(Integer, nullable=True)
    protocol = Column(String(20), nullable=False)

    # Flow statistics
    packet_count = Column(Integer, default=0)
    byte_count = Column(Integer, default=0)
    duration_ms = Column(Float, default=0.0)

    # Timing features
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    inter_arrival_times = Column(String, nullable=True)  # JSON string

    # Size features
    packet_sizes = Column(String, nullable=True)  # JSON string
    avg_packet_size = Column(Float, default=0.0)
    std_packet_size = Column(Float, default=0.0)
    min_packet_size = Column(Integer, default=0)
    max_packet_size = Column(Integer, default=0)

    # Rate features
    packets_per_second = Column(Float, default=0.0)
    bytes_per_second = Column(Float, default=0.0)

    # Classification
    predicted_category = Column(String(20), default=IntentCategory.UNKNOWN)
    confidence_score = Column(Float, default=0.0)
    is_classified = Column(Integer, default=0)

    # QoS
    priority_level = Column(Integer, default=3)  # 1=highest, 4=lowest
    bandwidth_limit_mbps = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Application info (if detected)
    application = Column(String(100), nullable=True)
    hostname = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Flow(id={self.id}, {self.src_ip}:{self.src_port} -> {self.dst_ip}:{self.dst_port}, category={self.predicted_category})>"


# Pydantic models for API
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class FlowBase(BaseModel):
    """Base flow model."""
    src_ip: str
    dst_ip: str
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: str


class FlowCreate(FlowBase):
    """Flow creation model."""
    packet_count: int = 0
    byte_count: int = 0
    packet_sizes: Optional[List[int]] = None
    inter_arrival_times: Optional[List[float]] = None


class FlowUpdate(BaseModel):
    """Flow update model."""
    predicted_category: Optional[str] = None
    confidence_score: Optional[float] = None
    priority_level: Optional[int] = None
    bandwidth_limit_mbps: Optional[float] = None


class FlowResponse(FlowBase):
    """Flow response model."""
    id: int
    packet_count: int
    byte_count: int
    duration_ms: float
    avg_packet_size: float
    packets_per_second: float
    bytes_per_second: float
    predicted_category: str
    confidence_score: float
    priority_level: int
    start_time: datetime
    end_time: Optional[datetime]
    created_at: datetime
    application: Optional[str]

    class Config:
        from_attributes = True


class FlowStatistics(BaseModel):
    """Flow statistics response."""
    total_flows: int
    flows_by_category: Dict[str, int]
    avg_duration_ms: float
    total_bytes: int
    total_packets: int
    classification_accuracy: Optional[float] = None


# Database setup
def init_db():
    """Initialize database tables."""
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
    )
    Base.metadata.create_all(bind=engine)
    return engine


def get_session_factory(engine):
    """Get session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
