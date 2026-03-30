"""
Machine Learning classifier for network traffic intent classification.
"""
import os
import pickle
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from app.config import settings
from app.ml.features import FeatureExtractor


class TrafficClassifier:
    """ML-based traffic intent classifier."""

    CATEGORIES = ["interactive", "streaming", "background", "malicious"]

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.MODEL_PATH
        self.feature_extractor = FeatureExtractor()
        self.model: Optional[Any] = None
        self.scaler: Optional[StandardScaler] = None
        self.is_trained = False

        # Load existing model if available
        self._load_model()

    def _load_model(self) -> bool:
        """Load trained model from disk."""
        model_file = os.path.join(self.model_path, "classifier.joblib")
        scaler_file = os.path.join(self.model_path, "scaler.joblib")

        if os.path.exists(model_file) and os.path.exists(scaler_file):
            try:
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                self.is_trained = True
                print(f"Loaded model from {model_file}")
                return True
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
        return False

    def _save_model(self) -> bool:
        """Save trained model to disk."""
        os.makedirs(self.model_path, exist_ok=True)
        model_file = os.path.join(self.model_path, "classifier.joblib")
        scaler_file = os.path.join(self.model_path, "scaler.joblib")

        try:
            joblib.dump(self.model, model_file)
            joblib.dump(self.scaler, scaler_file)
            print(f"Saved model to {model_file}")
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False

    def train(self, X: np.ndarray, y: np.ndarray,
              model_type: str = "random_forest") -> Dict[str, float]:
        """
        Train the classifier.

        Args:
            X: Feature matrix
            y: Target labels
            model_type: 'random_forest' or 'gradient_boosting'

        Returns:
            Dictionary with training metrics
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Initialize model
        if model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            )
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Train
        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        train_accuracy = self.model.score(X_train_scaled, y_train)
        test_accuracy = self.model.score(X_test_scaled, y_test)

        self.is_trained = True
        self._save_model()

        return {
            "train_accuracy": train_accuracy,
            "test_accuracy": test_accuracy,
            "model_type": model_type,
            "feature_count": X.shape[1],
            "sample_count": X.shape[0]
        }

    def predict(self, flow_data: Dict[str, Any]) -> Tuple[str, float, Dict[str, float]]:
        """
        Predict intent category for a flow.

        Args:
            flow_data: Flow feature dictionary

        Returns:
            Tuple of (category, confidence, probabilities)
        """
        if not self.is_trained or self.model is None:
            return "unknown", 0.0, {cat: 0.25 for cat in self.CATEGORIES}

        # Extract features
        features = self.feature_extractor.get_feature_vector(flow_data)
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # Predict
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]

        # Create probability dict
        prob_dict = {cat: float(prob) for cat, prob in zip(self.model.classes_, probabilities)}
        confidence = float(np.max(probabilities))

        return prediction, confidence, prob_dict

    def predict_batch(self, flow_list: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """
        Predict categories for multiple flows.

        Args:
            flow_list: List of flow dictionaries

        Returns:
            List of (category, confidence) tuples
        """
        if not self.is_trained or self.model is None:
            return [("unknown", 0.0) for _ in flow_list]

        # Extract features
        X = self.feature_extractor.extract_features_batch(flow_list)
        X_scaled = self.scaler.transform(X)

        # Predict
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        confidences = np.max(probabilities, axis=1)

        return list(zip(predictions, confidences))

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance from the model."""
        if not self.is_trained or self.model is None:
            return None

        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            return dict(zip(self.feature_extractor.get_feature_names(), importance))
        return None

    def is_ready(self) -> bool:
        """Check if classifier is ready for predictions."""
        return self.is_trained and self.model is not None


def create_sample_training_data() -> Tuple[np.ndarray, np.ndarray]:
    """
    Create synthetic training data for demonstration.
    In production, this should be replaced with real labeled data.
    """
    np.random.seed(42)
    n_samples = 1000

    # Define feature characteristics for each category
    categories = {
        "interactive": {
            "packet_count": (50, 100),
            "avg_packet_size": (200, 600),
            "packets_per_second": (50, 200),
            "inter_arrival_time": (0.005, 0.02),
            "protocol_tcp": 0.7,
            "protocol_udp": 0.3,
        },
        "streaming": {
            "packet_count": (100, 500),
            "avg_packet_size": (1000, 1500),
            "packets_per_second": (20, 60),
            "inter_arrival_time": (0.02, 0.05),
            "protocol_tcp": 0.9,
            "protocol_udp": 0.1,
        },
        "background": {
            "packet_count": (20, 50),
            "avg_packet_size": (500, 1000),
            "packets_per_second": (1, 10),
            "inter_arrival_time": (0.1, 1.0),
            "protocol_tcp": 0.6,
            "protocol_udp": 0.4,
        },
        "malicious": {
            "packet_count": (200, 1000),
            "avg_packet_size": (40, 100),
            "packets_per_second": (100, 500),
            "inter_arrival_time": (0.001, 0.01),
            "protocol_tcp": 0.8,
            "protocol_udp": 0.2,
        }
    }

    X_list = []
    y_list = []
    extractor = FeatureExtractor()

    for category, params in categories.items():
        for _ in range(n_samples // 4):
            # Generate synthetic flow data
            flow = {
                "packet_count": np.random.randint(*params["packet_count"]),
                "byte_count": np.random.randint(1000, 100000),
                "avg_packet_size": np.random.uniform(*params["avg_packet_size"]),
                "std_packet_size": np.random.uniform(10, 200),
                "min_packet_size": np.random.randint(40, 200),
                "max_packet_size": np.random.randint(500, 1500),
                "duration_ms": np.random.uniform(100, 10000),
                "packets_per_second": np.random.uniform(*params["packets_per_second"]),
                "bytes_per_second": np.random.uniform(1000, 100000),
                "inter_arrival_times": np.random.uniform(
                    params["inter_arrival_time"][0],
                    params["inter_arrival_time"][1],
                    50
                ).tolist(),
                "packet_sizes": np.random.randint(40, 1500, 50).tolist(),
                "protocol": np.random.choice(
                    ["TCP", "UDP"],
                    p=[params["protocol_tcp"], params["protocol_udp"]]
                ),
                "dst_port": np.random.choice([80, 443, 53, 5060, 3389, 12345]),
            }

            features = extractor.extract_features(flow)
            X_list.append([features.get(name, 0.0) for name in extractor.get_feature_names()])
            y_list.append(category)

    return np.array(X_list), np.array(y_list)
