import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export const api = {
  get: (url: string) => axios.get(`${API_BASE}${url}`),
  post: (url: string, data?: any) => axios.post(`${API_BASE}${url}`, data),
};

export const workstationService = {
  getSymbols: () => api.get('/brokers/symbols'),
  getSignals: () => api.get('/strategies/signals'),
  getQueue: () => api.get('/execution/queue'),
  getPositions: () => api.get('/management/positions'),
  getExperiments: () => api.get('/validation/experiments'),
  getSettings: () => api.get('/system/settings'),
  getAnalytics: () => api.get('/analytics/summary'),
  getAlerts: () => api.get('/alerts/?unread_only=false'),
  getBrokerAccounts: () => api.get('/brokers/accounts'),

  toggleKillSwitch: () => api.post('/system/kill-switch'),
  exportState: () => api.get('/system/export'),

  runScan: (symbol: string, timeframe: string) => api.post(`/strategies/scan/${symbol}/${timeframe}`),
  runAutoBest: (symbol: string, timeframes: string) => api.post(`/strategies/auto-best-setup/${symbol}?timeframes=${timeframes}`),

  addToQueue: (signalId: number) => api.post(`/execution/queue-add/${signalId}`),
  executeTrade: (queueId: number) => api.post(`/execution/execute/${queueId}`),

  promoteExperiment: (id: number) => api.post(`/validation/promote/${id}`),
  runBacktest: (strategyId: string, symbol: string) => api.post(`/validation/run-backtest?strategy_id=${strategyId}&symbol=${symbol}`),

  markAlertRead: (id: number) => api.post(`/alerts/mark-read/${id}`),

  linkAccount: (data: any) => api.post('/brokers/accounts', data),
  testConnection: (id: number) => api.post(`/brokers/test-connection/${id}`),

  updatePosition: (id: number, params: string) => api.post(`/management/update-position/${id}?${params}`),
};
