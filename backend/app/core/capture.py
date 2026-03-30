"""
Network packet capture engine using Scapy.
"""
import asyncio
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set

from scapy.all import sniff, get_if_list, conf
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.packet import Packet

from app.config import settings
from app.ml.features import FlowAggregator


class PacketCaptureEngine:
    """Real-time packet capture and flow aggregation engine."""

    def __init__(self,
                 interface: Optional[str] = None,
                 timeout_seconds: int = 60,
                 on_flow_detected: Optional[Callable] = None):
        self.interface = interface or settings.CAPTURE_INTERFACE
        self.timeout_seconds = timeout_seconds
        self.on_flow_detected = on_flow_detected

        self.flow_aggregator = FlowAggregator(timeout_seconds)
        self.is_capturing = False
        self.capture_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # Statistics
        self.packets_captured = 0
        self.flows_detected = 0
        self.start_time: Optional[float] = None

        # Available interfaces
        self.available_interfaces: List[str] = []
        self._update_interfaces()

    def _update_interfaces(self):
        """Update list of available network interfaces."""
        try:
            self.available_interfaces = get_if_list()
        except Exception:
            self.available_interfaces = []

    def get_interfaces(self) -> List[str]:
        """Get list of available network interfaces."""
        self._update_interfaces()
        return self.available_interfaces

    def _process_packet(self, packet: Packet):
        """Process a captured packet."""
        try:
            # Skip non-IP packets
            if not packet.haslayer(IP):
                return

            ip_layer = packet[IP]
            timestamp = time.time()

            # Extract basic info
            packet_info = {
                "src_ip": ip_layer.src,
                "dst_ip": ip_layer.dst,
                "protocol": "OTHER",
                "src_port": 0,
                "dst_port": 0,
                "length": len(packet),
                "timestamp": timestamp,
            }

            # Determine protocol
            if packet.haslayer(TCP):
                packet_info["protocol"] = "TCP"
                packet_info["src_port"] = packet[TCP].sport
                packet_info["dst_port"] = packet[TCP].dport
            elif packet.haslayer(UDP):
                packet_info["protocol"] = "UDP"
                packet_info["src_port"] = packet[UDP].sport
                packet_info["dst_port"] = packet[UDP].dport
            elif packet.haslayer(ICMP):
                packet_info["protocol"] = "ICMP"

            # Add to flow aggregator
            completed_flow = self.flow_aggregator.add_packet(packet_info)
            self.packets_captured += 1

            # If flow is complete (timed out), notify callback
            if completed_flow and self.on_flow_detected:
                self.flows_detected += 1
                asyncio.run_coroutine_threadsafe(
                    self._notify_flow(completed_flow),
                    asyncio.get_event_loop()
                )

        except Exception as e:
            print(f"Error processing packet: {e}")

    async def _notify_flow(self, flow: Dict[str, Any]):
        """Notify flow detected callback."""
        if self.on_flow_detected:
            try:
                await self.on_flow_detected(flow)
            except Exception as e:
                print(f"Error in flow callback: {e}")

    def _cleanup_expired_flows(self):
        """Periodic cleanup of expired flows."""
        while not self.stop_event.is_set():
            time.sleep(self.timeout_seconds)
            if self.stop_event.is_set():
                break

            current_time = time.time()
            expired_flows = self.flow_aggregator.cleanup_expired(current_time)

            for flow in expired_flows:
                if self.on_flow_detected:
                    try:
                        asyncio.run_coroutine_threadsafe(
                            self._notify_flow(flow),
                            asyncio.get_event_loop()
                        )
                    except Exception as e:
                        print(f"Error notifying expired flow: {e}")

    def _capture_loop(self):
        """Main packet capture loop."""
        try:
            print(f"Starting packet capture on interface: {self.interface or 'default'}")

            # Set filter based on configuration
            filter_str = "ip"  # Capture only IP packets

            # Use async sniff
            sniff(
                iface=self.interface,
                prn=self._process_packet,
                filter=filter_str,
                store=0,
                stop_filter=lambda x: self.stop_event.is_set()
            )
        except Exception as e:
            print(f"Error in capture loop: {e}")

    def start(self) -> bool:
        """Start packet capture."""
        if self.is_capturing:
            print("Capture already running")
            return False

        self.stop_event.clear()
        self.is_capturing = True
        self.start_time = time.time()
        self.packets_captured = 0
        self.flows_detected = 0

        # Start capture thread
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()

        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_flows, daemon=True)
        self.cleanup_thread.start()

        print("Packet capture started")
        return True

    def stop(self) -> bool:
        """Stop packet capture."""
        if not self.is_capturing:
            return False

        self.stop_event.set()
        self.is_capturing = False

        # Wait for threads to finish
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)

        print("Packet capture stopped")
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get capture statistics."""
        duration = time.time() - (self.start_time or time.time())
        return {
            "is_capturing": self.is_capturing,
            "interface": self.interface,
            "packets_captured": self.packets_captured,
            "flows_detected": self.flows_detected,
            "duration_seconds": duration,
            "packets_per_second": self.packets_captured / duration if duration > 0 else 0,
            "active_flows": len(self.flow_aggregator.get_active_flows()),
        }


class SimulatedCaptureEngine:
    """Simulated packet capture for testing without root privileges."""

    def __init__(self,
                 on_flow_detected: Optional[Callable] = None,
                 simulation_interval: float = 1.0):
        self.on_flow_detected = on_flow_detected
        self.simulation_interval = simulation_interval
        self.is_capturing = False
        self.stop_event = threading.Event()
        self.capture_thread: Optional[threading.Thread] = None

        self.packets_captured = 0
        self.flows_detected = 0
        self.start_time: Optional[float] = None

        # Simulated endpoints
        self.endpoints = [
            ("192.168.1.10", "8.8.8.8"),      # Web browsing
            ("192.168.1.11", "13.107.42.14"),  # Teams/Zoom
            ("192.168.1.12", "142.250.185.78"), # YouTube
            ("192.168.1.13", "104.244.42.193"), # Background download
            ("192.168.1.14", "185.220.101.48"), # Suspicious
        ]

    def _generate_flow(self, category: str) -> Dict[str, Any]:
        """Generate a simulated flow."""
        import random

        src_ip, dst_ip = random.choice(self.endpoints)

        # Category-specific parameters
        params = {
            "interactive": {
                "packet_count": random.randint(50, 100),
                "byte_count": random.randint(10000, 50000),
                "packets_per_second": random.uniform(50, 200),
                "avg_packet_size": random.uniform(200, 600),
                "dst_port": random.choice([5060, 443, 3389]),
                "protocol": "TCP",
            },
            "streaming": {
                "packet_count": random.randint(100, 500),
                "byte_count": random.randint(50000, 500000),
                "packets_per_second": random.uniform(20, 60),
                "avg_packet_size": random.uniform(1000, 1500),
                "dst_port": random.choice([443, 80]),
                "protocol": "TCP",
            },
            "background": {
                "packet_count": random.randint(20, 50),
                "byte_count": random.randint(10000, 100000),
                "packets_per_second": random.uniform(1, 10),
                "avg_packet_size": random.uniform(500, 1000),
                "dst_port": random.choice([443, 8080]),
                "protocol": "TCP",
            },
            "malicious": {
                "packet_count": random.randint(200, 1000),
                "byte_count": random.randint(8000, 100000),
                "packets_per_second": random.uniform(100, 500),
                "avg_packet_size": random.uniform(40, 100),
                "dst_port": random.randint(10000, 65000),
                "protocol": random.choice(["TCP", "UDP"]),
            }
        }.get(category, params["background"])

        params["src_ip"] = src_ip
        params["dst_ip"] = dst_ip
        params["src_port"] = random.randint(49152, 65535)
        params["duration_ms"] = random.uniform(1000, 30000)
        params["inter_arrival_times"] = [
            random.uniform(0.001, 0.1) for _ in range(params["packet_count"])
        ]
        params["packet_sizes"] = [
            int(random.gauss(params["avg_packet_size"], params["avg_packet_size"] * 0.1))
            for _ in range(params["packet_count"])
        ]

        return params

    def _simulation_loop(self):
        """Generate simulated traffic."""
        import random
        import time

        categories = ["interactive", "streaming", "background", "malicious"]
        weights = [0.3, 0.4, 0.25, 0.05]  # Distribution of traffic types

        while not self.stop_event.is_set():
            # Generate 1-3 flows per interval
            for _ in range(random.randint(1, 3)):
                category = random.choices(categories, weights=weights)[0]
                flow = self._generate_flow(category)

                self.packets_captured += flow["packet_count"]
                self.flows_detected += 1

                if self.on_flow_detected:
                    try:
                        asyncio.run_coroutine_threadsafe(
                            self._notify_flow(flow),
                            asyncio.get_event_loop()
                        )
                    except Exception as e:
                        print(f"Error in simulated flow callback: {e}")

            # Wait for next interval
            time.sleep(self.simulation_interval)

    async def _notify_flow(self, flow: Dict[str, Any]):
        """Notify flow callback."""
        if self.on_flow_detected:
            await self.on_flow_detected(flow)

    def start(self) -> bool:
        """Start simulated capture."""
        if self.is_capturing:
            return False

        self.is_capturing = True
        self.stop_event.clear()
        self.start_time = time.time()
        self.packets_captured = 0
        self.flows_detected = 0

        self.capture_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.capture_thread.start()

        print("Simulated packet capture started")
        return True

    def stop(self) -> bool:
        """Stop simulated capture."""
        if not self.is_capturing:
            return False

        self.stop_event.set()
        self.is_capturing = False

        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)

        print("Simulated packet capture stopped")
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get simulated statistics."""
        duration = time.time() - (self.start_time or time.time())
        return {
            "is_capturing": self.is_capturing,
            "mode": "simulated",
            "packets_captured": self.packets_captured,
            "flows_detected": self.flows_detected,
            "duration_seconds": duration,
            "packets_per_second": self.packets_captured / duration if duration > 0 else 0,
        }

    def get_interfaces(self) -> List[str]:
        """Return simulated interfaces."""
        return ["simulated-eth0", "simulated-wlan0"]
