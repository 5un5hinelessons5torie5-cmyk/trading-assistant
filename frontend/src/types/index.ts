export interface Symbol {
  id: number;
  name: string;
  broker: string;
  status: 'live_ready' | 'research_only' | 'blocked';
  asset_group: string;
  blocked_reason?: string;
}

export interface Signal {
  id: number;
  strategy_id: string;
  strategy_label: string;
  strategy_role: string;
  symbol: string;
  timeframe: string;
  side: 'buy' | 'sell';
  confidence: number;
  ml_score?: number;
  ml_pass?: boolean;
}

export interface QueueItem {
  id: number;
  signal_id: number;
  status: string;
  requested_volume: number;
  execution_message?: string;
  queue_admission_note?: string;
}

export interface Position {
  id: number;
  symbol: string;
  side: string;
  volume: number;
  entry_price: number;
  pnl: number;
  status: string;
  created_at: string;
  notes?: string;
  discipline_score?: number;
  setup_quality_score?: number;
}

export interface Experiment {
  id: number;
  preset_name: string;
  strategy_id: string;
  oos_winrate: number;
  trust_score: number;
  is_active: boolean;
}

export interface Alert {
  id: number;
  title: string;
  message: string;
  level: string;
  is_read: boolean;
}

export interface BrokerAccount {
  id: number;
  broker_name: string;
  login: number;
  is_active: boolean;
}

export interface SystemSettings {
  kill_switch: boolean;
  daily_loss_stop_pct: number;
}
