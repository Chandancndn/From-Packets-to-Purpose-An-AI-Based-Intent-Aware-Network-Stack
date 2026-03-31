import React, { useMemo } from 'react';
import { Activity, Shield, Download, Video, Clock } from 'lucide-react';
import type { Flow } from '../types';

interface RecentFlowsPanelProps {
  flows: Flow[];
}

const categoryConfig = {
  interactive: {
    icon: Activity,
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/20',
    borderColor: 'border-emerald-500/30',
    label: 'Interactive',
  },
  streaming: {
    icon: Video,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/20',
    borderColor: 'border-blue-500/30',
    label: 'Streaming',
  },
  background: {
    icon: Download,
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/20',
    borderColor: 'border-amber-500/30',
    label: 'Background',
  },
  malicious: {
    icon: Shield,
    color: 'text-rose-400',
    bgColor: 'bg-rose-500/20',
    borderColor: 'border-rose-500/30',
    label: 'Malicious',
  },
  unknown: {
    icon: Activity,
    color: 'text-gray-400',
    bgColor: 'bg-gray-500/20',
    borderColor: 'border-gray-500/30',
    label: 'Unknown',
  },
};

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatConfidence = (confidence: number | null | undefined): string => {
  if (confidence === null || confidence === undefined || isNaN(confidence)) {
    return '—';
  }
  const percentage = Math.max(0, Math.min(100, confidence * 100));
  return `${percentage.toFixed(0)}%`;
};

const formatTime = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    
    if (diffSecs < 60) return `${diffSecs}s ago`;
    const diffMins = Math.floor(diffSecs / 60);
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    return date.toLocaleTimeString();
  } catch {
    return 'Unknown';
  }
};

export const RecentFlowsPanel: React.FC<RecentFlowsPanelProps> = ({ flows }) => {
  // Sort by created_at to show latest first, limit to 20
  const sortedFlows = useMemo(() => {
    return [...flows]
      .sort((a, b) => {
        const dateA = new Date(a.created_at || 0).getTime();
        const dateB = new Date(b.created_at || 0).getTime();
        return dateB - dateA;
      })
      .slice(0, 20);
  }, [flows]);

  return (
    <div className="glass rounded-xl overflow-hidden h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-white/10 flex-shrink-0">
        <div className="flex items-center gap-2 mb-2">
          <Clock size={18} className="text-blue-400" />
          <h3 className="text-md font-semibold text-white">Recent Flows</h3>
          <span className="ml-auto text-xs px-2 py-1 rounded-full bg-blue-500/20 text-blue-400">
            {sortedFlows.length} shown
          </span>
        </div>
        <p className="text-dark-500 text-xs">Latest network traffic (newest first)</p>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        {sortedFlows.length === 0 ? (
          <div className="p-8 text-center text-dark-500 flex items-center justify-center h-full">
            <div>
              <Activity size={32} className="mx-auto mb-2 opacity-50" />
              <p>No flows detected yet</p>
            </div>
          </div>
        ) : (
          <div className="space-y-2 p-4">
            {sortedFlows.map((flow, index) => {
              const config = categoryConfig[flow.predicted_category as keyof typeof categoryConfig] || categoryConfig.unknown;
              const Icon = config.icon;

              return (
                <div
                  key={`${flow.id}-${index}`}
                  className={`p-3 rounded-lg border ${config.borderColor} ${config.bgColor} hover:bg-white/10 transition-colors cursor-pointer group`}
                >
                  {/* Top Row: Category and Time */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Icon size={14} className={config.color} />
                      <span className="text-xs font-medium text-white">
                        {config.label}
                      </span>
                      {flow.predicted_category === 'malicious' && (
                        <span className="text-xs px-1.5 py-0.5 rounded bg-rose-500/30 text-rose-300 font-medium">
                          ALERT
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-dark-400">
                      {formatTime(flow.created_at)}
                    </span>
                  </div>

                  {/* IPs Row */}
                  <div className="text-xs mb-2 font-mono">
                    <div className="text-dark-300 truncate">
                      <span className="text-blue-300">{flow.src_ip}</span>
                      <span className="text-dark-500">:{flow.src_port}</span>
                      <span className="text-dark-500 mx-1">→</span>
                      <span className="text-purple-300">{flow.dst_ip}</span>
                      <span className="text-dark-500">:{flow.dst_port}</span>
                    </div>
                  </div>

                  {/* Stats Row */}
                  <div className="flex items-center justify-between text-xs text-dark-400">
                    <div className="space-x-3 flex">
                      <span className="truncate">
                        <span className="text-dark-500">Size:</span> {formatBytes(flow.byte_count)}
                      </span>
                      <span className="truncate">
                        <span className="text-dark-500">Confidence:</span> {formatConfidence(flow.confidence_score)}
                      </span>
                    </div>
                    <span className="text-dark-500">{flow.protocol}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer - Summary */}
      {sortedFlows.length > 0 && (
        <div className="border-t border-white/10 p-3 bg-white/5 flex-shrink-0">
          <div className="text-xs text-dark-500 text-center">
            Showing latest {sortedFlows.length} flows • Updates in real-time
          </div>
        </div>
      )}
    </div>
  );
};
