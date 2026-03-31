import React, { useState } from 'react';
import { Header } from '../components/Header';
import { StatCard } from '../components/StatCard';
import { RecentFlowsPanel } from '../components/RecentFlowsPanel';
import { TrafficChart } from '../components/TrafficChart';
import { AlertPanel } from '../components/AlertPanel';
import { useWebSocket } from '../hooks/useWebSocket';
import { useFlows } from '../hooks/useFlows';
import {
  Activity,
  Shield,
  Wifi,
  Download,
  AlertTriangle,
  Clock,
  Database,
  Zap,
} from 'lucide-react';
import type { Alert } from '../types';

export const Dashboard: React.FC = () => {
  const { isConnected, flows: wsFlows, alerts: wsAlerts, stats } = useWebSocket();
  const { flows: apiFlows, statistics } = useFlows();
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());

  // Merge WebSocket and API flows
  const allFlows = [...wsFlows, ...apiFlows].slice(0, 100);

  // Filter dismissed alerts
  const activeAlerts = wsAlerts.filter((alert) => !dismissedAlerts.has(alert.id));

  const handleDismissAlert = (id: string) => {
    setDismissedAlerts((prev) => new Set([...prev, id]));
  };

  // Calculate stats
  const maliciousCount = allFlows.filter(
    (f) => f.predicted_category === 'malicious'
  ).length;
  const totalBytes = statistics?.total_bytes || 0;
  const totalPackets = statistics?.total_packets || 0;

  return (
    <div className="min-h-screen bg-dark-900 bg-grid">
      <Header isConnected={isConnected} />

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Flows"
            value={statistics?.total_flows || 0}
            subtitle="Network flows captured"
            icon={Activity}
            color="blue"
            trend="+12% from last hour"
          />

          <StatCard
            title="Traffic Volume"
            value={
              totalBytes > 1000000
                ? `${(totalBytes / 1000000).toFixed(2)} MB`
                : `${(totalBytes / 1000).toFixed(2)} KB`
            }
            subtitle={`${totalPackets.toLocaleString()} packets`}
            icon={Database}
            color="green"
          />

          <StatCard
            title="Active Connections"
            value={allFlows.length}
            subtitle="Currently monitored"
            icon={Wifi}
            color="yellow"
          />

          <StatCard
            title="Threats Blocked"
            value={maliciousCount}
            subtitle="Malicious flows detected"
            icon={Shield}
            color="red"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Recent Flows Panel - Scrollable */}
          <div className="lg:col-span-2">
            <div style={{ height: '500px' }}>
              <RecentFlowsPanel flows={allFlows} />
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <TrafficChart statistics={statistics} />
            <AlertPanel alerts={activeAlerts} onDismiss={handleDismissAlert} />
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-8 glass rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">About the System</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium text-white mb-2">How It Works</h3>
              <ul className="space-y-2 text-sm text-dark-500">
                <li className="flex items-start gap-2">
                  <span className="text-brand-500">1.</span>
                  Captures network packets in real-time
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-brand-500">2.</span>
                  Extracts statistical features from flows
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-brand-500">3.</span>
                  Classifies into intent categories using ML
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-brand-500">4.</span>
                  Applies dynamic QoS policies
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-sm font-medium text-white mb-2">Traffic Categories</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
                  <span className="text-sm text-dark-500">Interactive (Video calls, Gaming) - High Priority</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-400"></div>
                  <span className="text-sm text-dark-500">Streaming (Video, Audio) - Medium Priority</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                  <span className="text-sm text-dark-500">Background (Downloads, Updates) - Low Priority</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-rose-400"></div>
                  <span className="text-sm text-dark-500">Malicious (Blocked/Isolated)</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-8 text-center text-dark-500 text-sm">
          <p>Intent-Aware Network Stack © 2024</p>
          <p className="mt-1">Siddaganga Institute of Technology, Tumkur</p>
          <p className="mt-1 text-xs">Developed by Kritika, Monisha, Chetan Kumar, K Chandan Jayasimha</p>
        </footer>
      </main>
    </div>
  );
};