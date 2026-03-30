export interface Flow {
  id: number;
  src_ip: string;
  dst_ip: string;
  src_port: number | null;
  dst_port: number | null;
  protocol: string;
  packet_count: number;
  byte_count: number;
  duration_ms: number;
  predicted_category: string;
  confidence_score: number;
  priority_level: number;
  created_at: string;
  application?: string;
}

export interface FlowStatistics {
  total_flows: number;
  flows_by_category: Record<string, number>;
  avg_duration_ms: number;
  total_bytes: number;
  total_packets: number;
  classification_accuracy: number | null;
}

export interface PredictionResult {
  category: string;
  confidence: number;
  probabilities: Record<string, number>;
  priority_level: number;
}

export interface QoSStats {
  is_initialized: boolean;
  interface: string;
  total_bandwidth_mbps: number;
  active_policies: number;
  policies: QoSPolicy[];
  mode?: string;
  dropped_flows?: number;
}

export interface QoSPolicy {
  flow_id: string;
  category: string;
  priority: number;
  bandwidth_mbps: number;
}

export interface Alert {
  id: string;
  type: string;
  message: string;
  severity: 'info' | 'warning' | 'critical';
  timestamp: number;
}

export interface CategoryConfig {
  priority_levels: Record<string, number>;
  bandwidth_allocation: Record<string, number>;
  categories: string[];
}

export type TrafficCategory = 'interactive' | 'streaming' | 'background' | 'malicious' | 'unknown';