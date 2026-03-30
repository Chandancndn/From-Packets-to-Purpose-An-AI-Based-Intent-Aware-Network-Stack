import React from 'react';
import { AlertTriangle, Info, AlertCircle, X } from 'lucide-react';
import type { Alert } from '../types';

interface AlertPanelProps {
  alerts: Alert[];
  onDismiss?: (id: string) => void;
}

const severityConfig = {
  info: {
    icon: Info,
    color: 'text-blue-400',
    bgColor: 'bg-blue-400/10',
    borderColor: 'border-blue-400/30',
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-amber-400',
    bgColor: 'bg-amber-400/10',
    borderColor: 'border-amber-400/30',
  },
  critical: {
    icon: AlertCircle,
    color: 'text-rose-400',
    bgColor: 'bg-rose-400/10',
    borderColor: 'border-rose-400/30',
  },
};

export const AlertPanel: React.FC<AlertPanelProps> = ({ alerts, onDismiss }) => {
  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white">Security Alerts</h2>
        {alerts.length > 0 && (
          <span className="px-2 py-1 text-xs font-medium rounded-full bg-rose-400/20 text-rose-400">
            {alerts.length} active
          </span>
        )}
      </div>

      <div className="space-y-3 max-h-80 overflow-y-auto">
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-dark-500">
            No security alerts at this time
          </div>
        ) : (
          alerts.slice(0, 10).map((alert) => {
            const config = severityConfig[alert.severity];
            const Icon = config.icon;

            return (
              <div
                key={alert.id}
                className={`flex items-start gap-3 p-4 rounded-lg border ${config.bgColor} ${config.borderColor} animate-slide-in`}
              >
                <Icon size={20} className={config.color} />
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium ${config.color}`}>
                    {alert.type.replace('_', ' ').toUpperCase()}
                  </p>
                  <p className="text-sm text-white/80 mt-1">{alert.message}</p>
                  <p className="text-xs text-dark-500 mt-2">
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
                {onDismiss && (
                  <button
                    onClick={() => onDismiss(alert.id)}
                    className="text-dark-500 hover:text-white transition-colors"
                  >
                    <X size={16} />
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};