"""
Prediction utilities for the Intent-Aware Network Stack.
"""
from typing import Any, Dict, Tuple

from app.config import settings
from app.ml.classifier import TrafficClassifier


# Global classifier instance
_classifier: TrafficClassifier = None


def get_classifier() -> TrafficClassifier:
    """Get or create the global classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = TrafficClassifier()
    return _classifier


def predict_intent(flow_data: Dict[str, Any]) -> Tuple[str, float, Dict[str, float]]:
    """
    Predict intent category for a network flow.

    Args:
        flow_data: Dictionary containing flow features

    Returns:
        Tuple of (category, confidence, probabilities)
    """
    classifier = get_classifier()
    return classifier.predict(flow_data)


def get_priority_level(category: str) -> int:
    """
    Get priority level for a traffic category.

    Args:
        category: Intent category

    Returns:
        Priority level (1=highest, 4=lowest)
    """
    return settings.PRIORITY_LEVELS.get(category, 3)


def get_bandwidth_allocation(category: str) -> int:
    """
    Get bandwidth allocation percentage for a category.

    Args:
        category: Intent category

    Returns:
        Bandwidth percentage
    """
    return settings.BANDWIDTH_ALLOCATION.get(category, 10)
