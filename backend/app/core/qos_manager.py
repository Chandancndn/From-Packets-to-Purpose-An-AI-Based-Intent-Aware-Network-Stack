"""
QoS (Quality of Service) Manager for dynamic traffic prioritization.
Uses Linux Traffic Control (tc) for bandwidth management.
"""
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from app.config import settings


@dataclass
class QoSPolicy:
    """QoS policy configuration."""
    flow_id: str
    category: str
    priority_level: int
    bandwidth_mbps: float
    latency_ms: Optional[float] = None
    queue_limit: int = 1000


class QoSManager:
    """Manage Quality of Service policies using Linux tc."""

    # tc handle to category mapping
    HANDLE_MAP = {
        "interactive": "1:10",
        "streaming": "1:20",
        "background": "1:30",
        "malicious": "1:40",
    }

    def __init__(self, interface: str = "eth0", total_bandwidth_mbps: int = 1000):
        self.interface = interface
        self.total_bandwidth_mbps = total_bandwidth_mbps
        self.is_initialized = False
        self.active_policies: Dict[str, QoSPolicy] = {}

    def initialize(self) -> bool:
        """Initialize QoS subsystem with HTB queuing."""
        if not settings.QOS_ENABLED:
            print("QoS is disabled in configuration")
            return False

        try:
            # Clear existing configuration
            self._run_tc(["qdisc", "del", "dev", self.interface, "root"])

            # Create HTB root qdisc
            self._run_tc([
                "qdisc", "add", "dev", self.interface, "root",
                "handle", "1:", "htb", "default", "30"
            ])

            # Create main class
            self._run_tc([
                "class", "add", "dev", self.interface, "parent", "1:",
                "classid", "1:1", "htb",
                "rate", f"{self.total_bandwidth_mbps}mbit",
                "ceil", f"{self.total_bandwidth_mbps}mbit"
            ])

            # Create category classes with bandwidth allocation
            allocations = settings.BANDWIDTH_ALLOCATION

            # Interactive (highest priority)
            interactive_bw = int(self.total_bandwidth_mbps * allocations["interactive"] / 100)
            self._create_class("1:10", interactive_bw, 1)

            # Streaming (medium priority)
            streaming_bw = int(self.total_bandwidth_mbps * allocations["streaming"] / 100)
            self._create_class("1:20", streaming_bw, 2)

            # Background (low priority)
            background_bw = int(self.total_bandwidth_mbps * allocations["background"] / 100)
            self._create_class("1:30", background_bw, 3)

            # Malicious (minimal bandwidth - effectively blocked)
            self._create_class("1:40", 1, 4)

            self.is_initialized = True
            print(f"QoS initialized on {self.interface} with {self.total_bandwidth_mbps} Mbps")
            return True

        except Exception as e:
            print(f"Failed to initialize QoS: {e}")
            return False

    def _create_class(self, classid: str, bandwidth: int, priority: int):
        """Create HTB class."""
        self._run_tc([
            "class", "add", "dev", self.interface,
            "parent", "1:1", "classid", classid, "htb",
            "rate", f"{max(bandwidth, 1)}mbit",
            "ceil", f"{self.total_bandwidth_mbps}mbit",
            "prio", str(priority)
        ])

        # Add sfq (Stochastic Fairness Queueing) for fairness within class
        self._run_tc([
            "qdisc", "add", "dev", self.interface,
            "parent", classid, "handle", classid.replace(":", "0"),
            "sfq", "perturb", "10"
        ])

    def _run_tc(self, args: List[str]) -> bool:
        """Execute tc command."""
        try:
            cmd = ["tc"] + args
            subprocess.run(cmd, capture_output=True, check=False)
            return True
        except Exception as e:
            print(f"tc command failed: {e}")
            return False

    def apply_policy(self, flow_id: str, category: str,
                     src_ip: Optional[str] = None,
                     dst_ip: Optional[str] = None,
                     src_port: Optional[int] = None,
                     dst_port: Optional[int] = None) -> bool:
        """
        Apply QoS policy to a specific flow.

        Args:
            flow_id: Unique flow identifier
            category: Traffic category
            src_ip: Source IP address
            dst_ip: Destination IP address
            src_port: Source port
            dst_port: Destination port

        Returns:
            True if successful, False otherwise
        """
        if not self.is_initialized:
            print("QoS not initialized")
            return False

        if category == "malicious":
            # For malicious traffic, we can drop it entirely
            return self._block_flow(src_ip, dst_ip, src_port, dst_port)

        handle = self.HANDLE_MAP.get(category, "1:30")
        priority = settings.PRIORITY_LEVELS.get(category, 3)
        bandwidth = settings.BANDWIDTH_ALLOCATION.get(category, 10)

        # Create filter to classify traffic
        filter_args = [
            "filter", "add", "dev", self.interface,
            "parent", "1:", "protocol", "ip",
            "prio", str(priority),
            "u32"
        ]

        # Build match conditions
        matches = []
        if src_ip:
            matches.extend(["match", "ip", "src", src_ip])
        if dst_ip:
            matches.extend(["match", "ip", "dst", dst_ip])
        if src_port:
            matches.extend(["match", "ip", "sport", str(src_port), "0xffff"])
        if dst_port:
            matches.extend(["match", "ip", "dport", str(dst_port), "0xffff"])

        if matches:
            filter_args.extend(matches)
            filter_args.extend(["flowid", handle])

            if self._run_tc(filter_args):
                policy = QoSPolicy(
                    flow_id=flow_id,
                    category=category,
                    priority_level=priority,
                    bandwidth_mbps=self.total_bandwidth_mbps * bandwidth / 100
                )
                self.active_policies[flow_id] = policy
                return True

        return False

    def _block_flow(self, src_ip: Optional[str] = None,
                    dst_ip: Optional[str] = None,
                    src_port: Optional[int] = None,
                    dst_port: Optional[int] = None) -> bool:
        """Block a malicious flow using iptables."""
        try:
            # Use iptables to drop packets
            ipt_args = ["iptables", "-A", "INPUT"]

            if src_ip:
                ipt_args.extend(["-s", src_ip])
            if dst_ip:
                ipt_args.extend(["-d", dst_ip])
            if src_port:
                ipt_args.extend(["--sport", str(src_port)])
            if dst_port:
                ipt_args.extend(["--dport", str(dst_port)])

            ipt_args.extend(["-j", "DROP"])

            subprocess.run(ipt_args, capture_output=True, check=False)
            return True
        except Exception as e:
            print(f"Failed to block flow: {e}")
            return False

    def remove_policy(self, flow_id: str) -> bool:
        """Remove QoS policy for a flow."""
        if flow_id in self.active_policies:
            del self.active_policies[flow_id]
            # Note: tc filters are tricky to remove individually
            # In production, you'd want more sophisticated filter management
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get QoS statistics."""
        stats = {
            "is_initialized": self.is_initialized,
            "interface": self.interface,
            "total_bandwidth_mbps": self.total_bandwidth_mbps,
            "active_policies": len(self.active_policies),
            "policies": [
                {
                    "flow_id": p.flow_id,
                    "category": p.category,
                    "priority": p.priority_level,
                    "bandwidth_mbps": p.bandwidth_mbps
                }
                for p in self.active_policies.values()
            ]
        }

        # Try to get tc statistics
        try:
            result = subprocess.run(
                ["tc", "-s", "qdisc", "show", "dev", self.interface],
                capture_output=True,
                text=True,
                check=False
            )
            stats["tc_output"] = result.stdout
        except Exception:
            pass

        return stats

    def cleanup(self) -> bool:
        """Clean up all QoS rules."""
        try:
            self._run_tc(["qdisc", "del", "dev", self.interface, "root"])
            self.is_initialized = False
            self.active_policies.clear()
            return True
        except Exception as e:
            print(f"Failed to cleanup QoS: {e}")
            return False


class SimulatedQoSManager(QoSManager):
    """Simulated QoS manager for testing without root privileges."""

    def __init__(self, interface: str = "eth0", total_bandwidth_mbps: int = 1000):
        super().__init__(interface, total_bandwidth_mbps)
        self.simulated_policies: Dict[str, QoSPolicy] = {}
        self.dropped_flows: set = set()

    def initialize(self) -> bool:
        """Simulate QoS initialization."""
        self.is_initialized = True
        print(f"[SIMULATED] QoS initialized on {self.interface}")
        return True

    def _run_tc(self, args: List[str]) -> bool:
        """Simulate tc command."""
        print(f"[SIMULATED] tc {' '.join(args)}")
        return True

    def apply_policy(self, flow_id: str, category: str,
                     src_ip: Optional[str] = None,
                     dst_ip: Optional[str] = None,
                     src_port: Optional[int] = None,
                     dst_port: Optional[int] = None) -> bool:
        """Simulate policy application."""
        if not self.is_initialized:
            return False

        priority = settings.PRIORITY_LEVELS.get(category, 3)
        bandwidth = settings.BANDWIDTH_ALLOCATION.get(category, 10)

        policy = QoSPolicy(
            flow_id=flow_id,
            category=category,
            priority_level=priority,
            bandwidth_mbps=self.total_bandwidth_mbps * bandwidth / 100
        )
        self.simulated_policies[flow_id] = policy

        if category == "malicious":
            self.dropped_flows.add(flow_id)
            print(f"[SIMULATED] Blocked malicious flow {flow_id}")

        print(f"[SIMULATED] Applied {category} policy to {flow_id} (priority: {priority})")
        return True

    def remove_policy(self, flow_id: str) -> bool:
        """Simulate policy removal."""
        if flow_id in self.simulated_policies:
            del self.simulated_policies[flow_id]
            self.dropped_flows.discard(flow_id)
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get simulated statistics."""
        return {
            "is_initialized": self.is_initialized,
            "mode": "simulated",
            "interface": self.interface,
            "total_bandwidth_mbps": self.total_bandwidth_mbps,
            "active_policies": len(self.simulated_policies),
            "dropped_flows": len(self.dropped_flows),
            "policies": [
                {
                    "flow_id": p.flow_id,
                    "category": p.category,
                    "priority": p.priority_level,
                    "bandwidth_mbps": p.bandwidth_mbps
                }
                for p in self.simulated_policies.values()
            ]
        }

    def cleanup(self) -> bool:
        """Simulate cleanup."""
        self.is_initialized = False
        self.simulated_policies.clear()
        self.dropped_flows.clear()
        print("[SIMULATED] QoS cleaned up")
        return True
