import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  color: 'green' | 'blue' | 'yellow' | 'red';
  trend?: string;
}

const colorMap = {
  green: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30',
  blue: 'text-blue-400 bg-blue-400/10 border-blue-400/30',
  yellow: 'text-amber-400 bg-amber-400/10 border-amber-400/30',
  red: 'text-rose-400 bg-rose-400/10 border-rose-400/30',
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  color,
  trend,
}) => {
  return (
    <div className="glass rounded-xl p-6 animate-fade-in">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-dark-500 text-sm font-medium mb-1">{title}</p>
          <h3 className="text-2xl font-bold text-white mb-1">{value}</h3>
          {subtitle && <p className="text-dark-500 text-xs">{subtitle}</p>}
          {trend && (
            <span className="text-emerald-400 text-sm font-medium mt-2 inline-block">
              {trend}
            </span>
          )}
        </div>
        <div className={`p-3 rounded-lg border ${colorMap[color]}`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  );
};