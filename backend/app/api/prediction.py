"""
API endpoints for ML prediction and classification.
"""
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ml.predict import predict_intent, get_classifier

router = APIRouter(prefix="/api/prediction", tags=["prediction"])


class FlowData(BaseModel):
    """Flow data for prediction."""
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    packet_count: int
    byte_count: int
    packet_sizes: List[int]
    inter_arrival_times: List[float]


class PredictionResponse(BaseModel):
    """Prediction response."""
    category: str
    confidence: float
    probabilities: Dict[str, float]
    priority_level: int


@router.post("/classify", response_model=PredictionResponse)
async def classify_flow(flow: FlowData):
    """
    Classify a network flow into intent categories.
    """
    try:
        flow_dict = flow.dict()
        category, confidence, probabilities = predict_intent(flow_dict)

        # Get priority level
        from app.ml.predict import get_priority_level
        priority = get_priority_level(category)

        return PredictionResponse(
            category=category,
            confidence=confidence,
            probabilities=probabilities,
            priority_level=priority
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@router.get("/categories")
async def get_categories():
    """
    Get list of supported traffic categories.
    """
    from app.config import settings

    return {
        "categories": settings.CATEGORIES,
        "priority_levels": settings.PRIORITY_LEVELS,
        "bandwidth_allocation": settings.BANDWIDTH_ALLOCATION
    }


@router.get("/model/status")
async def get_model_status():
    """
    Get ML model status and information.
    """
    classifier = get_classifier()

    status = {
        "is_trained": classifier.is_ready(),
        "feature_count": len(classifier.feature_extractor.get_feature_names()),
        "categories": classifier.CATEGORIES,
    }

    if classifier.is_ready():
        feature_importance = classifier.get_feature_importance()
        if feature_importance:
            # Sort by importance
            sorted_features = sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            status["top_features"] = [
                {"name": name, "importance": round(float(imp), 4)}
                for name, imp in sorted_features
            ]

    return status


@router.post("/model/train")
async def train_model():
    """
    Retrain the ML model with current data.
    """
    try:
        from app.ml.classifier import TrafficClassifier, create_sample_training_data

        # In production, you'd load real labeled data from database
        X, y = create_sample_training_data()

        classifier = TrafficClassifier()
        metrics = classifier.train(X, y, model_type="random_forest")

        return {
            "status": "success",
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")
