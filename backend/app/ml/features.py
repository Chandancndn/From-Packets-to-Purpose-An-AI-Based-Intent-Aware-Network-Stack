"""
Feature extraction module for network traffic analysis.
"""
import json
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats


class FeatureExtractor:
    """Extract statistical features from network flows."""

    # Port to application mapping
    WELL_KNOWN_PORTS = {
        20: "FTP_DATA",
        21: "FTP_CONTROL",
        22: "SSH",
        23: "TELNET",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        993: "IMAPS",
        995: "POP3S",
        1935: "RTMP",
        3389: "RDP",
        5060: "SIP",
        5222: "XMPP",
        8080: "HTTP_PROXY",
    }

    def __init__(self):
        self.feature_names = [
            # Packet count features
            "packet_count",
            "total_bytes",
            "avg_packet_size",
            "std_packet_size",
            "min_packet_size",
            "max_packet_size",

            # Timing features
            "flow_duration_ms",
            "avg_inter_arrival_time",
            "std_inter_arrival_time",
            "min_inter_arrival_time",
            "max_inter_arrival_time",

            # Rate features
            "packets_per_second",
            "bytes_per_second",

            # Distribution features
            "packet_size_variance",
            "packet_size_skewness",
            "packet_size_kurtosis",

            # Protocol features (one-hot encoded)
            "protocol_tcp",
            "protocol_udp",
            "protocol_icmp",
            "protocol_other",

            # Port features
            "is_well_known_port",
            "dst_port",
        ]

    def extract_features(self, flow_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract features from flow data.

        Args:
            flow_data: Dictionary containing flow information

        Returns:
            Dictionary of extracted features
        """
        features = {}

        # Basic statistics
        packet_count = flow_data.get("packet_count", 0)
        byte_count = flow_data.get("byte_count", 0)
        duration_ms = flow_data.get("duration_ms", 0.1)  # Avoid division by zero

        features["packet_count"] = packet_count
        features["total_bytes"] = byte_count

        # Packet size statistics
        packet_sizes = flow_data.get("packet_sizes", [])
        if packet_sizes:
            features["avg_packet_size"] = np.mean(packet_sizes)
            features["std_packet_size"] = np.std(packet_sizes)
            features["min_packet_size"] = np.min(packet_sizes)
            features["max_packet_size"] = np.max(packet_sizes)
            features["packet_size_variance"] = np.var(packet_sizes)

            # Higher-order statistics
            if len(packet_sizes) >= 3:
                features["packet_size_skewness"] = stats.skew(packet_sizes)
                features["packet_size_kurtosis"] = stats.kurtosis(packet_sizes)
            else:
                features["packet_size_skewness"] = 0.0
                features["packet_size_kurtosis"] = 0.0
        else:
            features["avg_packet_size"] = 0.0
            features["std_packet_size"] = 0.0
            features["min_packet_size"] = 0.0
            features["max_packet_size"] = 0.0
            features["packet_size_variance"] = 0.0
            features["packet_size_skewness"] = 0.0
            features["packet_size_kurtosis"] = 0.0

        # Timing statistics
        inter_arrival_times = flow_data.get("inter_arrival_times", [])
        if inter_arrival_times:
            features["flow_duration_ms"] = sum(inter_arrival_times)
            features["avg_inter_arrival_time"] = np.mean(inter_arrival_times)
            features["std_inter_arrival_time"] = np.std(inter_arrival_times)
            features["min_inter_arrival_time"] = np.min(inter_arrival_times) if inter_arrival_times else 0.0
            features["max_inter_arrival_time"] = np.max(inter_arrival_times) if inter_arrival_times else 0.0
        else:
            features["flow_duration_ms"] = duration_ms
            features["avg_inter_arrival_time"] = 0.0
            features["std_inter_arrival_time"] = 0.0
            features["min_inter_arrival_time"] = 0.0
            features["max_inter_arrival_time"] = 0.0

        # Rate features
        duration_sec = features["flow_duration_ms"] / 1000.0
        if duration_sec > 0:
            features["packets_per_second"] = packet_count / duration_sec
            features["bytes_per_second"] = byte_count / duration_sec
        else:
            features["packets_per_second"] = 0.0
            features["bytes_per_second"] = 0.0

        # Protocol encoding
        protocol = flow_data.get("protocol", "OTHER").upper()
        features["protocol_tcp"] = 1.0 if protocol == "TCP" else 0.0
        features["protocol_udp"] = 1.0 if protocol == "UDP" else 0.0
        features["protocol_icmp"] = 1.0 if protocol == "ICMP" else 0.0
        features["protocol_other"] = 1.0 if protocol not in ["TCP", "UDP", "ICMP"] else 0.0

        # Port features
        dst_port = flow_data.get("dst_port", 0)
        features["dst_port"] = dst_port
        features["is_well_known_port"] = 1.0 if dst_port in self.WELL_KNOWN_PORTS else 0.0

        return features

    def extract_features_batch(self, flow_list: List[Dict[str, Any]]) -> np.ndarray:
        """
        Extract features from multiple flows.

        Args:
            flow_list: List of flow data dictionaries

        Returns:
            NumPy array of feature vectors
        """
        features_list = []
        for flow in flow_list:
            features = self.extract_features(flow)
            features_list.append([features.get(name, 0.0) for name in self.feature_names])
        return np.array(features_list)

    def get_feature_vector(self, flow_data: Dict[str, Any]) -> np.ndarray:
        """
        Get feature vector for a single flow.

        Args:
            flow_data: Flow data dictionary

        Returns:
            NumPy feature vector
        """
        features = self.extract_features(flow_data)
        return np.array([features.get(name, 0.0) for name in self.feature_names])

    def get_feature_names(self) -> List[str]:
        """Get list of feature names."""
        return self.feature_names.copy()


class FlowAggregator:
    """Aggregate packets into flows."""

    def __init__(self, timeout_seconds: int = 60):
        self.timeout_seconds = timeout_seconds
        self.active_flows: Dict[str, Dict[str, Any]] = {}

    def _get_flow_key(self, src_ip: str, dst_ip: str, src_port: int,
                      dst_port: int, protocol: str) -> str:
        """Generate unique flow key (bidirectional)."""
        # Sort endpoints to make flow bidirectional
        if (src_ip, src_port) < (dst_ip, dst_port):
            return f"{src_ip}:{src_port}-{dst_ip}:{dst_port}-{protocol}"
        else:
            return f"{dst_ip}:{dst_port}-{src_ip}:{src_port}-{protocol}"

    def add_packet(self, packet_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add packet to flow aggregation.

        Args:
            packet_info: Dictionary with packet information

        Returns:
            Completed flow if timeout reached, None otherwise
        """
        flow_key = self._get_flow_key(
            packet_info["src_ip"],
            packet_info["dst_ip"],
            packet_info.get("src_port", 0),
            packet_info.get("dst_port", 0),
            packet_info["protocol"]
        )

        current_time = packet_info["timestamp"]

        # Check if flow exists
        if flow_key in self.active_flows:
            flow = self.active_flows[flow_key]

            # Check timeout
            if current_time - flow["last_seen"] > self.timeout_seconds:
                # Flow timed out, return completed flow
                completed_flow = self._finalize_flow(flow)
                del self.active_flows[flow_key]
                return completed_flow

            # Update existing flow
            flow["packet_count"] += 1
            flow["byte_count"] += packet_info.get("length", 0)
            flow["packet_sizes"].append(packet_info.get("length", 0))

            inter_arrival = current_time - flow["last_seen"]
            flow["inter_arrival_times"].append(inter_arrival)
            flow["last_seen"] = current_time

            if packet_info.get("length", 0) > flow["max_packet_size"]:
                flow["max_packet_size"] = packet_info.get("length", 0)
            if packet_info.get("length", 0) < flow["min_packet_size"]:
                flow["min_packet_size"] = packet_info.get("length", 0)
        else:
            # Create new flow
            self.active_flows[flow_key] = {
                "src_ip": packet_info["src_ip"],
                "dst_ip": packet_info["dst_ip"],
                "src_port": packet_info.get("src_port", 0),
                "dst_port": packet_info.get("dst_port", 0),
                "protocol": packet_info["protocol"],
                "start_time": current_time,
                "last_seen": current_time,
                "packet_count": 1,
                "byte_count": packet_info.get("length", 0),
                "packet_sizes": [packet_info.get("length", 0)],
                "inter_arrival_times": [],
                "min_packet_size": packet_info.get("length", 0),
                "max_packet_size": packet_info.get("length", 0),
            }

        return None

    def _finalize_flow(self, flow: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize flow data."""
        flow["duration_ms"] = (flow["last_seen"] - flow["start_time"]) * 1000
        return flow

    def get_active_flows(self) -> List[Dict[str, Any]]:
        """Get all active flows."""
        return list(self.active_flows.values())

    def cleanup_expired(self, current_time: float) -> List[Dict[str, Any]]:
        """Clean up and return expired flows."""
        expired = []
        to_remove = []

        for key, flow in self.active_flows.items():
            if current_time - flow["last_seen"] > self.timeout_seconds:
                expired.append(self._finalize_flow(flow))
                to_remove.append(key)

        for key in to_remove:
            del self.active_flows[key]

        return expired
