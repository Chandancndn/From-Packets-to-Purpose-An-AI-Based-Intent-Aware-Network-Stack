import { useState, useEffect, useCallback } from 'react';
import { getFlows, getStatistics } from '../services/api';
import type { Flow, FlowStatistics } from '../types';

export function useFlows(refreshInterval = 5000) {
  const [flows, setFlows] = useState<Flow[]>([]);
  const [statistics, setStatistics] = useState<FlowStatistics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFlows = useCallback(async () => {
    try {
      const data = await getFlows(0, 100);
      setFlows(data);
    } catch (err) {
      setError('Failed to fetch flows');
    }
  }, []);

  const fetchStatistics = useCallback(async () => {
    try {
      const data = await getStatistics();
      setStatistics(data);
    } catch (err) {
      console.error('Failed to fetch statistics');
    }
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      await Promise.all([fetchFlows(), fetchStatistics()]);
      setIsLoading(false);
    };

    loadData();

    const interval = setInterval(() => {
      fetchFlows();
      fetchStatistics();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [fetchFlows, fetchStatistics, refreshInterval]);

  return {
    flows,
    statistics,
    isLoading,
    error,
    refetch: fetchFlows,
  };
}