import React from 'react';
import { Activity, Shield, Download, Video } from 'lucide-react';
import type { Flow } from '../types';

interface FlowTableProps {
  flows: Flow[];
}

const categoryConfig = {
  interactive: {
    icon: Activity,
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-400/10',
    label: 'Interactive',
    priority: 'High',
  },
  streaming: {
    icon: Video,
    color: 'text-blue-400',
    bgColor: 'bg-blue-400/10',
    label: 'Streaming',
    priority: 'Medium',
  },
  background: {
    icon: Download,
    color: 'text-amber-400',
    bgColor: 'bg-amber-400/10',
    label: 'Background',
    priority: 'Low',
  },
  malicious: {
    icon: Shield,
    color: 'text-rose-400',
    bgColor: 'bg-rose-400/10',
    label: 'Malicious',
    priority: 'Blocked',
  },
  unknown: {
    icon: Activity,
    color: 'text-gray-400',
    bgColor: 'bg-gray-400/10',
    label: 'Unknown',
    priority: 'Pending',
  },
};

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDuration = (ms: number): string => {
  if (ms < 1000) return `${ms.toFixed(0)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
};

export const FlowTable: React.FC<FlowTableProps> = ({ flows }) => {
  return (
    <div className="glass rounded-xl overflow-hidden">
      <div className="p-6 border-b border-white/10">
        <h2 className="text-lg font-semibold text-white">Recent Flows</h2>
        <p className="text-dark-500 text-sm mt-1">
          Live network traffic classification
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-white/5">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">Category</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">Source</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">Destination</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">Protocol</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">Size</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">Confidence</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-dark-500 uppercase tracking-wider">Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {flows.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-dark-500">
                  No flows detected yet. Waiting for traffic...
                </td>
              </tr>
            ) : (
              flows.slice(0, 20).map((flow) => {
                const config = categoryConfig[flow.predicted_category as keyof typeof categoryConfig] || categoryConfig.unknown;
                const Icon = config.icon;

                return (
                  <tr key={flow.id} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${config.bgColor}`}>
                          <Icon size={16} className={config.color} />
                        </div>
                        <div>
                          <span className={`text-sm font-medium ${config.color}`}>
                            {config.label}
                          </span>
                          <p className="text-xs text-dark-500">{config.priority}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm text-white font-mono">{flow.src_ip}</p>
                        <p className="text-xs text-dark-500">{flow.src_port || 'N/A'}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm text-white font-mono">{flow.dst_ip}</p>
                        <p className="text-xs text-dark-500">{flow.dst_port || 'N/A'}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-white/10 text-white">
                        {flow.protocol}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm text-white">{formatBytes(flow.byte_count)}</p>
                        <p className="text-xs text-dark-500">{flow.packet_count} pkts</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 bg-dark-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-brand-500 rounded-full"
                            style={{ width: `${flow.confidence_score * 100}%` }}
                          />
                        </div>
                        <span className="text-sm text-white">
                          {(flow.confidence_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-dark-500">
                        {new Date(flow.created_at).toLocaleTimeString()}
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};