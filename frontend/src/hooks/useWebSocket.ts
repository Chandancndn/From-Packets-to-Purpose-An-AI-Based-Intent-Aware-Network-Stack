import { useEffect, useRef, useState } from 'react';
import { wsService } from '../services/websocket';
import type { Flow, Alert } from '../types';

interface WebSocketState {
  isConnected: boolean;
  flows: Flow[];
  alerts: Alert[];
  stats: unknown;
}

export function useWebSocket() {
  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    flows: [],
    alerts: [],
    stats: null,
  });

  const flowsRef = useRef<Flow[]>([]);

  useEffect(() => {
    wsService.connect();

    const unsubscribeFlow = wsService.subscribe('flow_update', (data: unknown) => {
      const flow = data as Flow;
      flowsRef.current = [flow, ...flowsRef.current].slice(0, 100);
      setState((prev) => ({
        ...prev,
        flows: flowsRef.current,
      }));
    });

    const unsubscribeAlert = wsService.subscribe('alert', (data: unknown) => {
      const alert = data as { type: string; message: string; severity: string };
      const newAlert: Alert = {
        id: Date.now().toString(),
        type: alert.type,
        message: alert.message,
        severity: alert.severity as 'info' | 'warning' | 'critical',
        timestamp: Date.now(),
      };
      setState((prev) => ({
        ...prev,
        alerts: [newAlert, ...prev.alerts].slice(0, 50),
      }));
    });

    const unsubscribeStats = wsService.subscribe('stats_update', (data: unknown) => {
      setState((prev) => ({
        ...prev,
        stats: data,
      }));
    });

    // Set connected after a delay
    setTimeout(() => {
      setState((prev) => ({ ...prev, isConnected: true }));
    }, 1000);

    return () => {
      unsubscribeFlow();
      unsubscribeAlert();
      unsubscribeStats();
      wsService.disconnect();
    };
  }, []);

  return state;
}