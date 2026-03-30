import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import type { FlowStatistics } from '../types';

interface TrafficChartProps {
  statistics: FlowStatistics | null;
}

const COLORS = {
  interactive: '#10b981',
  streaming: '#3b82f6',
  background: '#f59e0b',
  malicious: '#ef4444',
};

export const TrafficChart: React.FC<TrafficChartProps> = ({ statistics }) => {
  if (!statistics) {
    return (
      <div className="glass rounded-xl p-6 h-80 flex items-center justify-center">
        <div className="text-dark-500">Loading statistics...</div>
      </div>
    );
  }

  const data = Object.entries(statistics.flows_by_category).map(([category, count]) => ({
    name: category.charAt(0).toUpperCase() + category.slice(1),
    value: count,
    color: COLORS[category as keyof typeof COLORS] || '#64748b',
  }));

  return (
    <div className="glass rounded-xl p-6">
      <h2 className="text-lg font-semibold text-white mb-4">Traffic Distribution</h2>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                color: '#fff',
              }}
            />
            <Legend
              verticalAlign="bottom"
              height={36}
              formatter={(value) => (
                <span className="text-white text-sm">{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-4">
        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-dark-500 text-xs">Total Flows</p>
          <p className="text-xl font-bold text-white">{statistics.total_flows}</p>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <p className="text-dark-500 text-xs">Avg Duration</p>
          <p className="text-xl font-bold text-white">
            {(statistics.avg_duration_ms / 1000).toFixed(2)}s
          </p>
        </div>
      </div>
    </div>
  );
};