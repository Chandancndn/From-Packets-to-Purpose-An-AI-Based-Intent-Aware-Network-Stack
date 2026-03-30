import React from 'react';
import { Network, Activity, Wifi } from 'lucide-react';

interface HeaderProps {
  isConnected: boolean;
}

export const Header: React.FC<HeaderProps> = ({ isConnected }) => {
  return (
    <header className="glass sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-brand-500/20 rounded-lg">
              <Network size={24} className="text-brand-500" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">
                Intent-Aware Network Stack
              </h1>
              <p className="text-xs text-dark-500">
                AI-Based Traffic Classification &amp; Management
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Activity size={16} className={isConnected ? 'text-emerald-400' : 'text-rose-400'} />
              <span className={`text-sm ${isConnected ? 'text-emerald-400' : 'text-rose-400'}`}>
                {isConnected ? 'Live' : 'Disconnected'}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Wifi size={16} className="text-brand-500" />
              <span className="text-sm text-white">Monitoring</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};